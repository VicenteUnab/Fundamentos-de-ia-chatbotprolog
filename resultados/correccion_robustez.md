# Corrección de las preguntas de robustez

Respuesta esperada deducida de `Chatbot/conocimiento.pl` (no de la botánica real).
Respuestas completas en `resultados_prolog_robustez.txt` y `resultados_llm_robustez.md`.

| # | Pregunta | Esperado según la base | Prolog | Gemini |
|---|---|---|---|---|
| 1 | ¿La cinta es segura para gatos y necesita poco riego? | Segura: sí. Poco riego: no (riego medio). | Parcial: solo responde el riego | Acierta |
| 2 | ¿Qué plantas me sugieres para principiantes con mascotas? | cinta | Falla: lista los 5 de principiantes | Acierta |
| 3 | ¿Qué planta me recomiendas para un baño con mascotas? | helecho, calathea | Falla: incluye cinta | Acierta |
| 4 | ¿La zamioculca y el ficus necesitan poca luz? | zamioculca sí (baja); ficus no (alta) | Parcial: solo zamioculca | Acierta |
| 5 | hola, ¿qué necesita la calathea? | Luz media, riego alto, humedad alta | Falla: solo saluda | Acierta |
| 6 | ¿Qué plantas necesitan al menos luz media? | potus, cinta, helecho, calathea, suculenta, ficus (asumiendo media < alta) | Falla: sin regla | Acierta (*) |
| 7 | ¿Cuáles son las plantas que resisten la falta de sol? | sansevieria, zamioculca | Falla: sin regla | Acierta |
| 8 | ¿Qué necesita el aloe? | El aloe no está en la base | Falla: mensaje genérico | Acierta |
| 9 | ¿El potus es tóxico para mis gatos? | No está registrado como seguro; la base no dice que sea tóxico | Falla: sin regla | Acierta |

Conteo: Prolog 0/9 completas (2 parciales); Gemini 9/9.

(*) Conocimiento externo a la base: en la pregunta 6 Gemini supone el orden
baja < media < alta, que la base no define (los niveles son constantes sin
orden). Es la única respuesta que usa algo fuera de la base. En la 9 no afirma
que el potus sea tóxico y en la 8 no inventa datos del aloe.

Preguntas 3 y 12 a 20 (`resultados_llm_faltantes.md`): las 10 respuestas de
Gemini coinciden con la base y ninguna usa conocimiento externo.
