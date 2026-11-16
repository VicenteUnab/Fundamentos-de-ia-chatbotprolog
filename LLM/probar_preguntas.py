"""Ejecuta las 20 preguntas de preguntas_prueba.txt con el chatbot LLM.

Sirve para llenar la columna "LLM" del informe de forma reproducible.

Uso (desde la carpeta principal del repositorio):
    python LLM/probar_preguntas.py
    python LLM/probar_preguntas.py --salida resultados/resultados_llm.md --pausa 8
    python LLM/probar_preguntas.py --numeros 3,12-20      # solo algunas preguntas
    python LLM/probar_preguntas.py --archivo preguntas_robustez.txt
"""

import argparse
import re
import sys
import time
from pathlib import Path

from chatbot_llm import RAIZ, ChatbotLLM, ErrorLLM

ARCHIVO_PREGUNTAS = RAIZ / "preguntas_prueba.txt"
PATRON_PREGUNTA = re.compile(r"^\s*(\d+)\.\s*(.+?)\s*$")


def leer_preguntas(ruta=ARCHIVO_PREGUNTAS):
    """Devuelve una lista de (numero, pregunta) a partir del archivo de preguntas."""
    preguntas = []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        coincidencia = PATRON_PREGUNTA.match(linea)
        if coincidencia:
            preguntas.append((int(coincidencia.group(1)), coincidencia.group(2)))
    return preguntas


def parsear_numeros(texto):
    """Convierte "3,12-20" en el conjunto {3, 12, 13, ..., 20}.

    Lanza ValueError si el texto no es una lista de numeros o rangos validos.
    """
    numeros = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        inicio, guion, fin = parte.partition("-")
        try:
            primero = int(inicio)
            ultimo = int(fin) if guion else primero
        except ValueError:
            raise ValueError(f"'{parte}' no es un numero ni un rango valido (ej. 3,12-20)") from None
        if primero < 1 or ultimo < primero:
            raise ValueError(f"rango invalido: '{parte}'")
        numeros.update(range(primero, ultimo + 1))
    if not numeros:
        raise ValueError("no se indico ningun numero de pregunta")
    return numeros


def filtrar_preguntas(preguntas, numeros):
    """Deja solo las preguntas cuyo numero esta en el conjunto dado."""
    return [(numero, pregunta) for numero, pregunta in preguntas if numero in numeros]


def ejecutar(bot, preguntas, pausa):
    """Pregunta una por una y devuelve (numero, pregunta, respuesta)."""
    resultados = []
    for posicion, (numero, pregunta) in enumerate(preguntas):
        if posicion > 0:
            time.sleep(pausa)  # evita pasar el limite de solicitudes por minuto
        try:
            respuesta = bot.responder(pregunta)
        except ErrorLLM as error:
            respuesta = f"[ERROR] {error}"
        print(f"{numero}. {pregunta}\n   -> {respuesta}\n")
        resultados.append((numero, pregunta, respuesta))
    return resultados


def guardar_markdown(resultados, modelo, ruta):
    """Guarda los resultados como Markdown."""
    lineas = [f"# Respuestas del chatbot LLM ({modelo})", ""]
    for numero, pregunta, respuesta in resultados:
        lineas += [f"**{numero}. {pregunta}**", "", respuesta, ""]
    Path(ruta).write_text("\n".join(lineas), encoding="utf-8")


def main(argumentos=None):
    analizador = argparse.ArgumentParser(description="Prueba las preguntas con el LLM")
    analizador.add_argument("--pausa", type=float, default=6.0, help="segundos entre preguntas (por defecto 6)")
    analizador.add_argument("--salida", help="archivo .md donde guardar las respuestas")
    analizador.add_argument("--modelo", help="modelo de Gemini a usar")
    analizador.add_argument("--numeros", help='preguntas a ejecutar, ej. "3,12-20" (por defecto todas)')
    analizador.add_argument("--archivo", default=str(ARCHIVO_PREGUNTAS),
                            help="archivo de preguntas numeradas (por defecto preguntas_prueba.txt)")
    opciones = analizador.parse_args(argumentos)

    try:
        preguntas = leer_preguntas(opciones.archivo)
    except OSError as error:
        print(f"Error: no pude leer {opciones.archivo}: {error}", file=sys.stderr)
        return 1
    if opciones.numeros:
        try:
            preguntas = filtrar_preguntas(preguntas, parsear_numeros(opciones.numeros))
        except ValueError as error:
            analizador.error(f"--numeros: {error}")
    if not preguntas:
        print("Error: no hay preguntas que ejecutar.", file=sys.stderr)
        return 1

    try:
        bot = ChatbotLLM(modelo=opciones.modelo)
        bot.preparar()  # falla de inmediato si falta la API key
        resultados = ejecutar(bot, preguntas, opciones.pausa)
    except ErrorLLM as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if opciones.salida:
        guardar_markdown(resultados, bot.modelo, opciones.salida)
        print(f"Resultados guardados en {opciones.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
