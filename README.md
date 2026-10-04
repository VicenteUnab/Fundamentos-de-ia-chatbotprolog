## Descripción

Chatbot sobre el cuidado de plantas de interior, desarrollado en Prolog.
Responde consultas sobre luz, riego, humedad, facilidad de cuidado y
compatibilidad con mascotas a partir de hechos y reglas de inferencia.

## Dominio seleccionado

Se escogió el cuidado de plantas de interior porque permite representar
características mediante hechos y obtener recomendaciones mediante reglas.
Además, corresponde a un dominio no relacionado con la informática.

La base actual incluye ocho plantas: sansevieria, zamioculca, potus,
cinta, helecho, calathea, suculenta y ficus.

## Archivos

- `Chatbot/conocimiento.pl`: hechos y reglas del dominio.
- `Chatbot/chatbot.pl`: reconocimiento de preguntas y respuestas.
- `Chatbot/main.pl`: inicio y conversación por consola.
- `Chatbot/probar_preguntas.pl`: ejecuta las 20 preguntas de prueba y muestra las respuestas.
- `docs/modelado_fol.md`: modelado del conocimiento en lógica de primer orden.
- `LLM/chatbot_llm.py`: chatbot con LLM (Gemini) que usa `conocimiento.pl` como base de conocimiento.
- `LLM/probar_preguntas.py`: ejecuta las 20 preguntas con el chatbot LLM.
- `LLM/test_chatbot_llm.py`: pruebas automáticas (no usan red ni API key).
- `LLM/requirements.txt`: dependencias de Python.
- `.env.example`: plantilla para guardar la API key (se copia como `.env`, que no se sube al repo).
- `preguntas_prueba.txt`: 20 preguntas para evaluar el chatbot.

## Requisitos y ejecución

Tener instalado SWI-Prolog.

Desde la carpeta principal del repositorio, ejecutar:

```bash
swipl -q -s Chatbot/main.pl
```

Escribir una pregunta y presionar Enter.
Usar `ayuda` para ver ejemplos y `salir` para terminar.

Para ejecutar las 20 preguntas de prueba de una vez:

```bash
swipl -q -s Chatbot/probar_preguntas.pl -g probar,halt
```

Desde otro programa, la función `responder_texto/2` de `chatbot.pl`
recibe una pregunta como texto y devuelve la respuesta como texto.

## Versión con LLM (Gemini)

El chatbot en Python envía la pregunta a Gemini junto con el contenido de
`Chatbot/conocimiento.pl` dentro del prompt del sistema. El modelo debe
responder solo con ese conocimiento. Como lee el mismo archivo que Prolog,
un cambio en la base (nueva planta, nueva regla) afecta a ambas versiones.
Cada pregunta es independiente: no hay historial de conversación.

Requisitos: Python 3.9 o superior y una API key gratuita de
https://aistudio.google.com/apikey

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r LLM/requirements.txt
cp .env.example .env             # y pegar la API key dentro de .env
python LLM/chatbot_llm.py
```

Otros comandos útiles:

```bash
python LLM/chatbot_llm.py --modelos        # lista los modelos disponibles para tu key
python LLM/chatbot_llm.py --ver-prompt     # muestra el prompt que recibe el modelo
python LLM/probar_preguntas.py --salida resultados_llm.md   # las 20 preguntas
python -m unittest discover -s LLM -v      # pruebas automáticas
```

El modelo por defecto es `gemini-2.5-flash`. Si Google lo retira, se cambia con
la variable `GEMINI_MODEL` (en `.env`) sin tocar el código.

## Ejemplos

- ¿Qué plantas necesitan poca luz?
- ¿La cinta es segura para mascotas?
- ¿La suculenta necesita luz alta?
- ¿Qué necesita la calathea?

## Limitaciones actuales

El chatbot reconoce preguntas mediante palabras clave. No interpreta
de forma general negaciones ni consultas con varias condiciones.

La versión LLM puede equivocarse aunque el conocimiento sea correcto, y sus
respuestas pueden variar entre ejecuciones. Depende de internet y de la cuota
gratuita de la API.

Sus respuestas dependen del conocimiento registrado. Que una planta
no esté registrada como segura para mascotas no demuestra que sea tóxica.

Las características de las plantas son una simplificación y requieren
documentación de fuentes y revisión por especie.

## Desarrollo pendiente

- Completar las fuentes del modelado (sección 9 de `docs/modelado_fol.md`).
- Desarrollar la interfaz web.
- Elaborar el informe comparativo de las 20 preguntas, con análisis,
  conclusiones, fortalezas, debilidades y propuestas de mejora.