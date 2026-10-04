"""Chatbot de plantas de interior con LLM (Gemini).

El modelo responde usando como unica fuente la base de conocimiento de la
version Prolog (Chatbot/conocimiento.pl), que se inserta tal cual en el prompt
del sistema. Asi las dos versiones parten del mismo conocimiento y cualquier
cambio hecho en ese archivo (agregar una planta, una regla) tambien afecta a
esta version despues de reiniciarla.

Uso desde la consola (desde la carpeta principal del repositorio):
    python LLM/chatbot_llm.py

Uso desde otro programa (por ejemplo, la web):
    from chatbot_llm import ChatbotLLM
    bot = ChatbotLLM()
    print(bot.responder("¿Qué plantas necesitan poca luz?"))
"""

import argparse
import os
import sys
import time
from pathlib import Path

import httpx
from google import genai
from google.genai import errors, types

try:  # Opcional: permite guardar la API key en un archivo .env
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_CONOCIMIENTO = RAIZ / "Chatbot" / "conocimiento.pl"

# Se puede cambiar sin tocar el codigo con la variable de entorno GEMINI_MODEL.
MODELO_POR_DEFECTO = "gemini-3.8-flash"

MAX_INTENTOS = 3
ESPERA_BASE_SEGUNDOS = 2.0
# Errores temporales (cuota por minuto, servidor ocupado): vale la pena reintentar.
CODIGOS_REINTENTABLES = {429, 500, 503}

PROMPT_SISTEMA = """Eres un chatbot sobre cuidado de plantas de interior.
Respondes usando SOLO la base de conocimiento que aparece al final. Esta
escrita en Prolog: los hechos describen cada planta y las reglas definen
conceptos derivados (por ejemplo, facil_cuidado o apta_bano).

Reglas de comportamiento:
1. Usa unicamente las plantas, hechos y reglas de la base. No agregues
   conocimiento externo sobre plantas, aunque lo conozcas.
2. Para saber si una planta cumple una condicion derivada, aplica las reglas
   de la base a los hechos de esa planta.
3. Lo que no esta en la base es desconocido. Si una planta no figura como
   segura para mascotas, di que "no esta registrada como segura", no que
   es toxica.
4. Si te preguntan por una planta que no esta en la base, dilo claramente
   y no inventes datos.
5. Si la pregunta no trata de plantas de interior, responde que solo puedes
   ayudar con cuidado de plantas de interior.
6. Si la pregunta tiene varias condiciones, combinalas todas.
7. Responde en español, en 1 a 3 frases, de forma directa. Al listar plantas,
   nombralas separadas por comas.

<base_de_conocimiento>
{conocimiento}
</base_de_conocimiento>"""

MENSAJE_AYUDA = (
    "Puedes preguntar, por ejemplo: ¿qué plantas necesitan poca luz?, "
    "¿la cinta es segura para mascotas? o ¿qué necesita la calathea?"
)


class ErrorLLM(Exception):
    """Error al obtener una respuesta del LLM, con un mensaje apto para mostrar."""


def cargar_conocimiento(ruta=ARCHIVO_CONOCIMIENTO):
    """Lee el archivo de conocimiento Prolog y devuelve su texto."""
    try:
        return Path(ruta).read_text(encoding="utf-8")
    except OSError as error:
        raise ErrorLLM(f"No pude leer la base de conocimiento en {ruta}: {error}") from error


def construir_prompt_sistema(conocimiento):
    """Arma el prompt del sistema insertando la base de conocimiento."""
    return PROMPT_SISTEMA.format(conocimiento=conocimiento)


def crear_cliente():
    """Crea el cliente de Gemini leyendo la API key del entorno."""
    if load_dotenv is not None:
        load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not clave:
        raise ErrorLLM(
            "Falta la API key. Crea una gratis en https://aistudio.google.com/apikey "
            "y guardala en la variable de entorno GEMINI_API_KEY "
            "(o en un archivo .env; ver .env.example)."
        )
    return genai.Client(api_key=clave)


def explicar_error(error):
    """Traduce un error de la API de Gemini a un mensaje claro."""
    if error.code == 429:
        return (
            "Se agoto la cuota gratuita (por minuto o por dia). "
            "Espera un momento e intenta de nuevo."
        )
    if error.code in (400, 401, 403):
        return f"La API rechazo la solicitud: revisa la API key. Detalle: {error.message}"
    if error.code == 404:
        return (
            f"El modelo no existe o no esta disponible: {error.message} "
            "Usa --modelos para ver los disponibles y GEMINI_MODEL para elegir uno."
        )
    return f"Error de la API de Gemini ({error.code}): {error.message}"


class ChatbotLLM:
    """Chatbot que responde preguntas usando Gemini y la base de conocimiento."""

    def __init__(self, modelo=None, ruta_conocimiento=ARCHIVO_CONOCIMIENTO,
                 cliente=None, espera_base=ESPERA_BASE_SEGUNDOS):
        if load_dotenv is not None:
            load_dotenv(RAIZ / ".env")
        self.modelo = modelo or os.getenv("GEMINI_MODEL") or MODELO_POR_DEFECTO
        self.ruta_conocimiento = ruta_conocimiento
        self.espera_base = espera_base
        self._cliente = cliente
        self.recargar_conocimiento()

    def recargar_conocimiento(self):
        """Vuelve a leer conocimiento.pl (util si se edita con el programa abierto)."""
        self.conocimiento = cargar_conocimiento(self.ruta_conocimiento)
        self.prompt_sistema = construir_prompt_sistema(self.conocimiento)

    def _obtener_cliente(self):
        if self._cliente is None:
            self._cliente = crear_cliente()
        return self._cliente

    def preparar(self):
        """Crea el cliente ahora, para detectar una API key faltante al iniciar."""
        self._obtener_cliente()

    def responder(self, pregunta):
        """Devuelve la respuesta del LLM a una pregunta (texto entra, texto sale).

        Cada pregunta es independiente: no se guarda historial, igual que en la
        version Prolog. Lanza ErrorLLM si no se pudo obtener respuesta.
        """
        pregunta = (pregunta or "").strip()
        if not pregunta:
            return "Escribe una pregunta sobre plantas de interior."

        cliente = self._obtener_cliente()
        configuracion = types.GenerateContentConfig(
            system_instruction=self.prompt_sistema,
            temperature=0,  # respuestas lo mas reproducibles posible
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        for intento in range(1, MAX_INTENTOS + 1):
            try:
                respuesta = cliente.models.generate_content(
                    model=self.modelo,
                    contents=pregunta,
                    config=configuracion,
                )
                break
            except errors.APIError as error:
                if error.code in CODIGOS_REINTENTABLES and intento < MAX_INTENTOS:
                    time.sleep(self.espera_base * 2 ** (intento - 1))
                    continue
                raise ErrorLLM(explicar_error(error)) from error
            except httpx.TransportError as error:  # sin internet, timeout, DNS...
                if intento < MAX_INTENTOS:
                    time.sleep(self.espera_base * 2 ** (intento - 1))
                    continue
                raise ErrorLLM(
                    "No pude conectar con Gemini. Revisa tu conexion a internet."
                ) from error

        texto = (respuesta.text or "").strip()
        if not texto:
            raise ErrorLLM("El modelo no devolvio texto (puede haber sido bloqueado).")
        return texto

    def listar_modelos(self):
        """Devuelve los nombres de modelos Gemini disponibles para la API key."""
        try:
            nombres = [m.name.removeprefix("models/") for m in self._obtener_cliente().models.list()]
        except errors.APIError as error:
            raise ErrorLLM(explicar_error(error)) from error
        return sorted(n for n in nombres if "gemini" in n)


def es_salida(texto):
    """Reconoce las formas basicas de terminar la conversacion."""
    palabras = texto.lower().replace("¿", " ").replace("?", " ").split()
    return any(p in ("salir", "adios", "adiós") for p in palabras)


def conversar(bot):
    """Bucle de conversacion por consola."""
    print("==============================================")
    print(" CHATBOT DE PLANTAS DE INTERIOR - LLM (Gemini)")
    print(f" Modelo: {bot.modelo}")
    print(' Escribe "ayuda" para ver ejemplos.')
    print(' Escribe "salir" para terminar.')
    print("==============================================")
    while True:
        try:
            entrada = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Hasta luego.")
            return
        if es_salida(entrada):
            print("Bot: Hasta luego.\n")
            return
        if entrada.lower() == "ayuda":
            print(f"Bot: {MENSAJE_AYUDA}\n")
            continue
        try:
            print(f"Bot: {bot.responder(entrada)}\n")
        except ErrorLLM as error:
            print(f"Bot: [error] {error}\n")


def main(argumentos=None):
    analizador = argparse.ArgumentParser(description="Chatbot de plantas con Gemini")
    analizador.add_argument("--modelo", help=f"modelo de Gemini (por defecto {MODELO_POR_DEFECTO})")
    analizador.add_argument("--modelos", action="store_true", help="lista los modelos disponibles y termina")
    analizador.add_argument("--ver-prompt", action="store_true", help="muestra el prompt del sistema y termina")
    opciones = analizador.parse_args(argumentos)

    try:
        bot = ChatbotLLM(modelo=opciones.modelo)
        if opciones.ver_prompt:  # no necesita API key
            print(bot.prompt_sistema)
        elif opciones.modelos:
            print("\n".join(bot.listar_modelos()))
        else:
            bot.preparar()
            conversar(bot)
    except ErrorLLM as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
