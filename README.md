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
- `preguntas_prueba.txt`: 20 preguntas para evaluar el chatbot.

## Requisitos y ejecución

Tener instalado SWI-Prolog.

Desde la carpeta principal del repositorio, ejecutar:

```bash
swipl -q -s Chatbot/main.pl
```

Escribir una pregunta y presionar Enter.
Usar `ayuda` para ver ejemplos y `salir` para terminar.

## Ejemplos

- ¿Qué plantas necesitan poca luz?
- ¿La cinta es segura para mascotas?
- ¿La suculenta necesita luz alta?
- ¿Qué necesita la calathea?

## Limitaciones actuales

El chatbot reconoce preguntas mediante palabras clave. No interpreta
de forma general negaciones ni consultas con varias condiciones.

Sus respuestas dependen del conocimiento registrado. Que una planta
no esté registrada como segura para mascotas no demuestra que sea tóxica.

Las características de las plantas son una simplificación y requieren
documentación de fuentes y revisión por especie.

## Desarrollo pendiente

- Documentar el modelado en lógica de primer orden.
- Implementar la versión con LLM y Python.
- Desarrollar la interfaz web.
- Elaborar el informe comparativo de las 20 preguntas, con análisis,
  conclusiones, fortalezas, debilidades y propuestas de mejora.