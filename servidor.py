"""Servidor local para la web y los chatbots Prolog y Gemini."""

import json
import logging
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


RAIZ = Path(__file__).resolve().parent
WEB = RAIZ / "web"

ARCHIVOS_WEB = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
}

bot_gemini = None
bloqueo_gemini = threading.Lock()


class ErrorChat(Exception):
    """Error que puede mostrarse en la interfaz."""


def buscar_prolog():
    ejecutable = shutil.which("swipl")

    if ejecutable:
        return ejecutable

    ruta_windows = Path(r"C:\Program Files\swipl\bin\swipl.exe")

    if ruta_windows.is_file():
        return str(ruta_windows)

    raise ErrorChat(
        "No se encontró SWI-Prolog. Instálalo y reinicia VSCode."
    )


def responder_prolog(pregunta):
    entrada = json.dumps(
        {"pregunta": pregunta},
        ensure_ascii=False,
    )

    try:
        resultado = subprocess.run(
            [
                buscar_prolog(),
                "-q",
                "-s",
                str(RAIZ / "Chatbot" / "puente_web.pl"),
            ],
            input=entrada,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=RAIZ,
            timeout=15,
        )
    except subprocess.TimeoutExpired as error:
        raise ErrorChat(
            "Prolog tardó demasiado en responder."
        ) from error
    except OSError as error:
        raise ErrorChat(
            "No se pudo iniciar SWI-Prolog."
        ) from error

    if resultado.returncode != 0:
        logging.error("Error de Prolog: %s", resultado.stderr)
        raise ErrorChat(
            "Prolog no pudo responder. Revisa la terminal del servidor."
        )

    try:
        datos = json.loads(resultado.stdout)
        respuesta = datos["respuesta"]

        if not isinstance(respuesta, str) or not respuesta.strip():
            raise ValueError("Respuesta vacía")

        return respuesta
    except (ValueError, KeyError, TypeError) as error:
        logging.error("Salida inesperada de Prolog: %s", resultado.stdout)
        raise ErrorChat(
            "Prolog devolvió una respuesta con formato inesperado."
        ) from error


def responder_gemini(pregunta):
    global bot_gemini

    # La importación se hace aquí para que Prolog funcione
    # aunque todavía no estén instaladas las dependencias de Gemini.
    try:
        from LLM.chatbot_llm import ChatbotLLM, ErrorLLM
    except ImportError as error:
        raise ErrorChat(
            "Faltan las dependencias de Gemini. Ejecuta: "
            "python -m pip install -r LLM/requirements.txt"
        ) from error

    with bloqueo_gemini:
        try:
            if bot_gemini is None:
                bot_gemini = ChatbotLLM()

            bot_gemini.recargar_conocimiento()
            return bot_gemini.responder(pregunta)
        except ErrorLLM as error:
            raise ErrorChat(str(error)) from error


class Servidor(BaseHTTPRequestHandler):
    def enviar_json(self, datos, codigo=200):
        contenido = json.dumps(
            datos,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenido)

    def do_GET(self):
        ruta = urlsplit(self.path).path
        archivo = ARCHIVOS_WEB.get(ruta)

        if archivo is None:
            self.enviar_json({"error": "Página no encontrada."}, 404)
            return

        nombre, tipo = archivo

        try:
            contenido = (WEB / nombre).read_bytes()
        except OSError:
            self.enviar_json(
                {"error": f"No se encontró web/{nombre}."},
                404,
            )
            return

        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenido)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/chat":
            self.enviar_json({"error": "Ruta no encontrada."}, 404)
            return

        tipo = self.headers.get("Content-Type", "").split(";")[0].strip()

        if tipo != "application/json":
            self.enviar_json(
                {"error": "La solicitud debe enviarse como JSON."},
                415,
            )
            return

        try:
            longitud = int(self.headers.get("Content-Length", "0"))

            if not 0 < longitud <= 10000:
                self.enviar_json(
                    {"error": "El tamaño de la solicitud no es válido."},
                    413,
                )
                return

            datos = json.loads(
                self.rfile.read(longitud).decode("utf-8")
            )
        except (ValueError, UnicodeError):
            self.enviar_json({"error": "El JSON no es válido."}, 400)
            return

        if not isinstance(datos, dict):
            self.enviar_json({"error": "Se esperaba un objeto JSON."}, 400)
            return

        pregunta = datos.get("pregunta")
        modelo = datos.get("modelo")

        if not isinstance(pregunta, str) or not pregunta.strip():
            self.enviar_json({"error": "Escribe una pregunta."}, 400)
            return

        pregunta = pregunta.strip()

        if len(pregunta) > 1000:
            self.enviar_json(
                {"error": "La pregunta supera los 1000 caracteres."},
                400,
            )
            return

        if modelo not in ("prolog", "gemini"):
            self.enviar_json({"error": "Selecciona un modelo válido."}, 400)
            return

        try:
            if modelo == "prolog":
                respuesta = responder_prolog(pregunta)
            else:
                respuesta = responder_gemini(pregunta)

            self.enviar_json({
                "respuesta": respuesta,
                "modelo": modelo,
            })
        except ErrorChat as error:
            self.enviar_json({"error": str(error)}, 503)
        except Exception:
            logging.exception("Error inesperado al responder")
            self.enviar_json(
                {"error": "Ocurrió un error. Revisa la terminal del servidor."},
                500,
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    servidor = ThreadingHTTPServer(
        ("127.0.0.1", 8000),
        Servidor,
    )
    servidor.daemon_threads = True

    print("Botánica disponible en http://127.0.0.1:8000")
    print("Para detener el servidor, presiona Ctrl + C.")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()