# Modelado del conocimiento en lógica de primer orden

Dominio: **cuidado de plantas de interior**.

Este documento describe cómo se representa el conocimiento del dominio en
lógica de primer orden (FOL) y cómo esa representación se traduce
directamente a Prolog (`Chatbot/conocimiento.pl`).

## 1. Dominio y justificación

Se eligió el cuidado de plantas de interior porque:

- No está relacionado con la informática, como exige el enunciado.
- Las características de una planta (luz, riego, humedad, resistencia,
  seguridad para mascotas) se representan naturalmente como hechos.
- Las recomendaciones ("¿qué planta sirve para un baño?") se obtienen
  combinando hechos mediante reglas, lo que permite mostrar inferencia
  y no solo consulta de datos.
- La base es pequeña (8 plantas), fácil de verificar y de modificar en vivo.

## 2. Vocabulario

### Constantes

| Tipo | Constantes |
|---|---|
| Plantas | `sansevieria`, `zamioculca`, `potus`, `cinta`, `helecho`, `calathea`, `suculenta`, `ficus` |
| Niveles de luz y humedad | `baja`, `media`, `alta` |
| Niveles de riego | `bajo`, `medio`, `alto` |

### Predicados base (se declaran como hechos)

| FOL | Significado | Prolog |
|---|---|---|
| `Planta(x)` | x es una planta registrada | `planta/1` |
| `Luz(x, n)` | x necesita luz de nivel n | `luz/2` |
| `Riego(x, n)` | x necesita riego de nivel n | `riego/2` |
| `Humedad(x, n)` | x necesita humedad de nivel n | `humedad/2` |
| `Resistente(x)` | x es una planta resistente en general | `resistente/1` |
| `SeguraMascotas(x)` | x está registrada como segura para mascotas | `segura_mascotas/1` |

### Predicados derivados (se definen mediante reglas)

| FOL | Significado | Prolog |
|---|---|---|
| `AptaPocaLuz(x)` | x tolera lugares con poca luz | `apta_poca_luz/1` |
| `NecesitaPocoRiego(x)` | x requiere poca agua | `necesita_poco_riego/1` |
| `FacilCuidado(x)` | x es fácil de cuidar | `facil_cuidado/1` |
| `AptaPrincipiante(x)` | x es adecuada para principiantes | `apta_principiante/1` |
| `AptaAmbienteHumedo(x)` | x es adecuada para ambientes húmedos | `apta_ambiente_humedo/1` |
| `AptaMascotas(x)` | x puede ubicarse en hogares con mascotas | `apta_mascotas/1` |
| `AptaBano(x)` | x puede ubicarse en un baño | `apta_bano/1` |

## 3. Hechos (átomos básicos)

```
Planta(sansevieria)   Planta(zamioculca)   Planta(potus)    Planta(cinta)
Planta(helecho)       Planta(calathea)     Planta(suculenta) Planta(ficus)
```

| Planta | Luz | Riego | Humedad | Resistente | SeguraMascotas |
|---|---|---|---|---|---|
| sansevieria | baja | bajo | baja | sí | – |
| zamioculca | baja | bajo | baja | sí | – |
| potus | media | medio | media | sí | – |
| cinta | media | medio | media | sí | sí |
| helecho | media | alto | alta | – | sí |
| calathea | media | alto | alta | – | sí |
| suculenta | alta | bajo | baja | sí | – |
| ficus | alta | medio | media | – | – |

Cada celda con valor es un hecho. Por ejemplo, la fila de `cinta` representa:
`Luz(cinta, media)`, `Riego(cinta, medio)`, `Humedad(cinta, media)`,
`Resistente(cinta)` y `SeguraMascotas(cinta)`. Una celda con "–" significa
que el hecho **no está registrado** (ver sección 6).

## 4. Reglas

Todas las reglas son cláusulas de Horn: una conjunción de condiciones que
implica una única conclusión.

| N° | Fórmula en FOL |
|---|---|
| R1 | ∀x ( Planta(x) ∧ Luz(x, baja) → AptaPocaLuz(x) ) |
| R2 | ∀x ( Planta(x) ∧ Riego(x, bajo) → NecesitaPocoRiego(x) ) |
| R3 | ∀x ( Planta(x) ∧ Resistente(x) ∧ Riego(x, bajo) → FacilCuidado(x) ) |
| R4 | ∀x ( Planta(x) ∧ Resistente(x) → AptaPrincipiante(x) ) |
| R5 | ∀x ( Planta(x) ∧ Humedad(x, alta) → AptaAmbienteHumedo(x) ) |
| R6 | ∀x ( Planta(x) ∧ SeguraMascotas(x) → AptaMascotas(x) ) |
| R7 | ∀x ( Planta(x) ∧ Humedad(x, alta) ∧ Luz(x, media) → AptaBano(x) ) |

Traducción a Prolog (ejemplo con R3):

```prolog
% ∀x ( Planta(x) ∧ Resistente(x) ∧ Riego(x, bajo) → FacilCuidado(x) )
facil_cuidado(X) :- planta(X), resistente(X), riego(X, bajo).
```

La flecha `→` se invierte a `:-` (la conclusión va primero), la conjunción `∧`
pasa a ser la coma, y el cuantificador universal `∀x` queda implícito en la
variable `X`.

## 5. Axiomas de integridad (parte del modelo, no forzados por Prolog)

Para que el modelo sea consistente se asume:

- **Unicidad de nivel:** cada planta tiene un único nivel por característica.
  ∀x ∀n ∀m ( Luz(x, n) ∧ Luz(x, m) → n = m ), y lo mismo para `Riego` y `Humedad`.
- **Nombres únicos:** `baja`, `media` y `alta` son constantes distintas entre sí,
  y también `bajo`, `medio` y `alto`.

Prolog no verifica estos axiomas: si alguien registrara dos niveles de luz para
la misma planta, el sistema no protestaría. Mantenerlos es responsabilidad de
quien edita la base.

## 6. Razonamiento y consultas

### Qué se puede concluir

Con la base de hechos y las reglas R1–R7, el motor de inferencia deriva:

| Predicado derivado | Plantas que lo cumplen |
|---|---|
| `AptaPocaLuz` | sansevieria, zamioculca |
| `NecesitaPocoRiego` | sansevieria, zamioculca, suculenta |
| `FacilCuidado` | sansevieria, zamioculca, suculenta |
| `AptaPrincipiante` | sansevieria, zamioculca, potus, cinta, suculenta |
| `AptaAmbienteHumedo` | helecho, calathea |
| `AptaMascotas` | cinta, helecho, calathea |
| `AptaBano` | helecho, calathea |

Ejemplo de derivación de `FacilCuidado(sansevieria)`: son hechos
`Planta(sansevieria)`, `Resistente(sansevieria)` y `Riego(sansevieria, bajo)`;
por R3 se concluye `FacilCuidado(sansevieria)`.

### Tipos de pregunta y su consulta lógica

| Tipo de pregunta | Ejemplo | Consulta lógica | Prolog |
|---|---|---|---|
| Sí/no sobre una planta | ¿La suculenta necesita poco riego? | ¿Se deduce `NecesitaPocoRiego(suculenta)`? | `necesita_poco_riego(suculenta)` |
| Lista | ¿Qué plantas necesitan poca luz? | Todos los x tales que `AptaPocaLuz(x)` | `findall(P, apta_poca_luz(P), L)` |
| Ficha de una planta | ¿Qué necesita la calathea? | `Luz(calathea,l) ∧ Riego(calathea,r) ∧ Humedad(calathea,h)` | `luz(calathea,L), riego(calathea,R), humedad(calathea,H)` |

### Mundo cerrado y negación

Prolog responde "no" cuando **no logra demostrar** una consulta (negación por
fallo). Esto equivale a la **hipótesis de mundo cerrado**: lo que no está en la
base se considera falso.

En lógica de primer orden pura esto no es válido. Que no se pueda deducir
`SeguraMascotas(potus)` **no** implica `¬SeguraMascotas(potus)`; solo indica
que la base no tiene esa información. Por eso el chatbot responde "no está
registrado como seguro" y no "es tóxico".

Una mejora posible es agregar un predicado `ToxicaMascotas(x)` para distinguir
tres estados: *sé que es segura*, *sé que es tóxica* y *no sé*.

## 7. Decisiones de diseño (para justificar en la defensa)

- **Resistente es un hecho separado de Riego.** Resistencia general y
  frecuencia de riego son propiedades distintas; `FacilCuidado` exige ambas.
- **`potus` es apta para principiantes (R4) pero no es fácil de cuidar (R3).**
  Es resistente, pero su riego es medio, y R3 exige riego bajo. Es una decisión
  de modelado defendible: "principiante" mide tolerancia a errores, "fácil de
  cuidar" mide además poca dedicación.
- **Los niveles son constantes sin orden.** El modelo no sabe que
  `baja < media < alta`. Por eso "poca luz" significa exactamente `Luz(x, baja)`.
  Extenderlo con un predicado `Menor(n, m)` permitiría preguntas como "al menos luz media".
- **Se separan hechos y reglas en el mismo archivo** pero en secciones distintas,
  para poder cambiar los datos de una planta sin tocar la lógica.
- **Los datos son una simplificación.** Los niveles asignados a cada especie
  deben respaldarse con fuentes. Ver sección 9.

## 8. Cómo agregar una planta y una regla

Agregar una planta nueva, por ejemplo `aloe`, implica añadir estas líneas
en `Chatbot/conocimiento.pl`:

```prolog
planta(aloe).
luz(aloe, alta).
riego(aloe, bajo).
humedad(aloe, baja).
resistente(aloe).
% segura_mascotas(aloe).   % solo si corresponde
```

Agregar una regla nueva, por ejemplo "planta de escritorio" (poca luz y poco riego):

```prolog
% ∀x ( Planta(x) ∧ Luz(x, baja) ∧ Riego(x, bajo) → AptaEscritorio(x) )
apta_escritorio(X) :- planta(X), luz(X, baja), riego(X, bajo).
```

Para que el chatbot la use en una pregunta, además hay que agregar una cláusula
`responder/2` en `Chatbot/chatbot.pl`.

## 9. Fuentes (pendiente)

Registrar aquí las fuentes usadas para cada planta (guías de jardinería,
viveros, listas de toxicidad como ASPCA). Cada característica de la tabla de la
sección 3 debería poder rastrearse a una fuente.
