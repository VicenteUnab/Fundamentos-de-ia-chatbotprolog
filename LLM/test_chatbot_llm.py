"""Pruebas del chatbot LLM con un cliente falso (no usan red ni API key).

Ejecutar desde la carpeta principal del repositorio:
    python -m unittest discover -s LLM -v
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import httpx
from google.genai import errors

import chatbot_llm
from chatbot_llm import ChatbotLLM, ErrorLLM
from probar_preguntas import leer_preguntas


class RespuestaFalsa:
    def __init__(self, text):
        self.text = text


class ModelosFalsos:
    """Imita client.models: devuelve, en orden, lo que se le indique."""

    def __init__(self, resultados):
        self.resultados = list(resultados)
        self.llamadas = []

    def generate_content(self, **kwargs):
        self.llamadas.append(kwargs)
        resultado = self.resultados.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return RespuestaFalsa(resultado)


class ClienteFalso:
    def __init__(self, resultados):
        self.models = ModelosFalsos(resultados)


def error_api(codigo):
    return errors.APIError(codigo, {"error": {"code": codigo, "message": "detalle", "status": "X"}})


def crear_bot(resultados):
    cliente = ClienteFalso(resultados)
    return ChatbotLLM(modelo="modelo-prueba", cliente=cliente, espera_base=0), cliente


class PruebasPrompt(unittest.TestCase):
    def test_prompt_incluye_la_base_de_conocimiento(self):
        bot, _ = crear_bot([])
        self.assertIn("planta(zamioculca).", bot.prompt_sistema)
        self.assertIn("apta_bano(X)", bot.prompt_sistema)
        self.assertIn("<base_de_conocimiento>", bot.prompt_sistema)

    def test_cambios_en_el_conocimiento_llegan_al_prompt(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "conocimiento.pl"
            ruta.write_text("planta(aloe).\nluz(aloe, alta).\n", encoding="utf-8")
            bot = ChatbotLLM(modelo="m", ruta_conocimiento=ruta, cliente=ClienteFalso([]))
            self.assertIn("planta(aloe).", bot.prompt_sistema)
            ruta.write_text("planta(bonsai).\n", encoding="utf-8")
            bot.recargar_conocimiento()
            self.assertIn("planta(bonsai).", bot.prompt_sistema)
            self.assertNotIn("aloe", bot.prompt_sistema)

    def test_falta_el_archivo_de_conocimiento(self):
        with self.assertRaises(ErrorLLM):
            ChatbotLLM(modelo="m", ruta_conocimiento="/no/existe.pl", cliente=ClienteFalso([]))


class PruebasResponder(unittest.TestCase):
    def test_devuelve_el_texto_y_envia_los_parametros_correctos(self):
        bot, cliente = crear_bot(["  Sansevieria y zamioculca.  "])
        self.assertEqual(bot.responder("¿Qué plantas necesitan poca luz?"), "Sansevieria y zamioculca.")
        llamada = cliente.models.llamadas[0]
        self.assertEqual(llamada["model"], "modelo-prueba")
        self.assertEqual(llamada["contents"], "¿Qué plantas necesitan poca luz?")
        self.assertEqual(llamada["config"].temperature, 0)
        self.assertEqual(llamada["config"].system_instruction, bot.prompt_sistema)

    def test_pregunta_vacia_no_llama_a_la_api(self):
        bot, cliente = crear_bot([])
        self.assertIn("Escribe una pregunta", bot.responder("   "))
        self.assertIn("Escribe una pregunta", bot.responder(None))
        self.assertEqual(cliente.models.llamadas, [])

    def test_reintenta_ante_errores_temporales(self):
        bot, cliente = crear_bot([error_api(429), error_api(503), "Listo."])
        self.assertEqual(bot.responder("hola"), "Listo.")
        self.assertEqual(len(cliente.models.llamadas), 3)

    def test_cuota_agotada_da_mensaje_claro_despues_de_los_reintentos(self):
        bot, cliente = crear_bot([error_api(429)] * chatbot_llm.MAX_INTENTOS)
        with self.assertRaises(ErrorLLM) as contexto:
            bot.responder("hola")
        self.assertIn("cuota", str(contexto.exception))
        self.assertEqual(len(cliente.models.llamadas), chatbot_llm.MAX_INTENTOS)

    def test_error_de_clave_no_se_reintenta(self):
        bot, cliente = crear_bot([error_api(403)])
        with self.assertRaises(ErrorLLM) as contexto:
            bot.responder("hola")
        self.assertIn("API key", str(contexto.exception))
        self.assertEqual(len(cliente.models.llamadas), 1)

    def test_sin_internet_da_mensaje_claro(self):
        bot, cliente = crear_bot([httpx.ConnectError("sin red")] * chatbot_llm.MAX_INTENTOS)
        with self.assertRaises(ErrorLLM) as contexto:
            bot.responder("hola")
        self.assertIn("conexion", str(contexto.exception))
        self.assertEqual(len(cliente.models.llamadas), chatbot_llm.MAX_INTENTOS)

    def test_respuesta_vacia_lanza_error(self):
        bot, _ = crear_bot([None])
        with self.assertRaises(ErrorLLM):
            bot.responder("hola")


class PruebasEntorno(unittest.TestCase):
    def test_sin_api_key_lanza_error_explicativo(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(chatbot_llm, "load_dotenv", None):
            with self.assertRaises(ErrorLLM) as contexto:
                chatbot_llm.crear_cliente()
        self.assertIn("GEMINI_API_KEY", str(contexto.exception))

    def test_modelo_se_puede_elegir_por_variable_de_entorno(self):
        with mock.patch.dict(os.environ, {"GEMINI_MODEL": "otro-modelo"}):
            bot = ChatbotLLM(cliente=ClienteFalso([]))
        self.assertEqual(bot.modelo, "otro-modelo")

    def test_es_salida(self):
        self.assertTrue(chatbot_llm.es_salida("salir"))
        self.assertTrue(chatbot_llm.es_salida("Adiós"))
        self.assertFalse(chatbot_llm.es_salida("¿qué plantas necesitan poca luz?"))


class PruebasPreguntas(unittest.TestCase):
    def test_se_leen_las_20_preguntas(self):
        preguntas = leer_preguntas()
        self.assertEqual(len(preguntas), 20)
        self.assertEqual(preguntas[0], (1, "¿Qué plantas necesitan poca luz?"))
        self.assertEqual(preguntas[-1][0], 20)


if __name__ == "__main__":
    unittest.main()
