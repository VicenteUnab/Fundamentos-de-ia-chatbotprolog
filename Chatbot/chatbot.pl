% Codificacion explicita para que las tildes carguen bien en cualquier sistema.
:- encoding(utf8).

% CHATBOT EN PROLOG

:- consult('conocimiento.pl').

% NORMALIZACION Y TOKENIZACION


% Convierte la entrada a minusculas y separa las palabras.
tokenizar(Texto, Tokens) :-
    string_lower(Texto, Minusculas),
    split_string(Minusculas, " \t\n", "¿?¡!,.;:", Tokens).

% Comprueba si una lista contiene alguna de las palabras dadas.
tiene_palabra(Tokens, Palabras) :-
    member(Palabra, Tokens),
    member(Palabra, Palabras).

% Busca el nombre de una planta dentro de la pregunta.
encontrar_planta(Tokens, Planta) :-
    member(Palabra, Tokens),
    atom_string(Planta, Palabra),
    planta(Planta),
    !.

% Convierte una lista de atomos en una frase separada por comas.
lista_a_texto([], "ninguna") :- !.
lista_a_texto(Lista, Texto) :-
    atomic_list_concat(Lista, ', ', Texto).

% Articulo definido de una planta (por defecto femenino).
articulo(Planta, "el") :-
    member(Planta, [potus, helecho, ficus]),
    !.
articulo(_, "la").

% Escribe "la zamioculca" / "el potus" segun corresponda.
con_articulo(Planta, Texto) :-
    articulo(Planta, Art),
    format(string(Texto), "~w ~w", [Art, Planta]).

% Concordancia de genero: "registrado como seguro" / "registrada como segura".
registrada_segura(Planta, "registrado como seguro") :-
    articulo(Planta, "el"),
    !.
registrada_segura(_, "registrada como segura").

% Igual que con_articulo/2 pero con mayuscula inicial ("La cinta", "El potus").
con_articulo_mayus(Planta, Texto) :-
    con_articulo(Planta, Minuscula),
    sub_string(Minuscula, 0, 1, _, Inicial),
    sub_string(Minuscula, 1, _, 0, Resto),
    string_upper(Inicial, Mayuscula),
    string_concat(Mayuscula, Resto, Texto).

% ============================================================
% INTERFAZ PUBLICA DEL CHATBOT
% ============================================================

% responder_texto(+Entrada, -Respuesta)
% Recibe la pregunta como texto y devuelve la respuesta como string.
% No lee ni escribe en consola, por lo que puede ser llamado desde
% main.pl, desde scripts de prueba o desde otro programa (Python, web).
responder_texto(Entrada, Respuesta) :-
    tokenizar(Entrada, Tokens),
    once(responder(Tokens, Respuesta)).

% ============================================================
% RESPUESTAS GENERALES
% ============================================================

% Responde a un saludo.
responder(T, "Hola. Soy el chatbot de plantas de interior. Preguntame por luz, riego, humedad o cuidados.") :-
    tiene_palabra(T, ["hola", "buenas", "hey"]).

% Explica como usar el chatbot.
responder(T, "Puedes preguntar, por ejemplo: ¿que plantas necesitan poca luz?, ¿que plantas son faciles de cuidar?, ¿la zamioculca necesita poco riego? o ¿que necesita la calathea?") :-
    tiene_palabra(T, ["ayuda", "opciones", "menu", "preguntas"]).

% Responde que la planta existe en la base de conocimiento.
responder(T, Respuesta) :-
    tiene_palabra(T, ["existe", "conoces", "tienes"]),
    encontrar_planta(T, Planta),
    con_articulo(Planta, Nombre),
    format(string(Respuesta), "Si, conozco ~w y tengo informacion sobre sus cuidados.", [Nombre]).

% ============================================================
% CONSULTAS SOBRE UNA PLANTA
% ============================================================

% Responde si una planta esta registrada como segura para mascotas.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["mascota", "mascotas", "perro", "gato"]),
    con_articulo(Planta, Nombre),
    con_articulo_mayus(Planta, NombreMayus),
    registrada_segura(Planta, Registrada),
    (   apta_mascotas(Planta)
    ->  format(
            string(Respuesta),
            "Si, ~w esta ~w para mascotas.",
            [Nombre, Registrada]
        )
    ;   format(
            string(Respuesta),
            "~w no esta ~w para mascotas en esta base.",
            [NombreMayus, Registrada]
        )
    ).

% Responde si una planta necesita luz media o alta.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["luz", "iluminacion", "iluminación"]),
    member(Nivel, [media, alta]),
    atom_string(Nivel, Palabra),
    member(Palabra, T),
    luz(Planta, Registrado),
    (Registrado == Nivel -> Veredicto = "si" ; Veredicto = "no"),
    format(
        string(Respuesta),
        "~w: la respuesta es ~w, porque su nivel de luz registrado es ~w.",
        [Planta, Veredicto, Registrado]
    ).

% Responde si una planta necesita poca luz.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["luz", "iluminacion"]),
    tiene_palabra(T, ["poca", "baja"]),
    luz(Planta, Nivel),
    (apta_poca_luz(Planta) -> Veredicto = "si" ; Veredicto = "no"),
    format(string(Respuesta), "~w: la respuesta es ~w, porque su nivel de luz registrado es ~w.", [Planta, Veredicto, Nivel]).

% Responde si una planta necesita poco riego.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["riego", "agua"]),
    tiene_palabra(T, ["poco", "poca", "bajo", "baja"]),
    riego(Planta, Nivel),
    (necesita_poco_riego(Planta) -> Veredicto = "si" ; Veredicto = "no"),
    format(string(Respuesta), "~w: la respuesta es ~w, porque su nivel de riego registrado es ~w.", [Planta, Veredicto, Nivel]).

% Responde si una planta es facil de cuidar.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["facil", "faciles", "fácil", "fáciles"]),
    tiene_palabra(T, ["cuidar", "cuidado"]),
    (facil_cuidado(Planta) -> Veredicto = "si" ; Veredicto = "no"),
    format(string(Respuesta), "Segun las reglas del chatbot, ~w es facil de cuidar: ~w.", [Planta, Veredicto]).

% Responde si una planta es adecuada para principiantes.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["principiante", "principiantes"]),
    (apta_principiante(Planta) -> Veredicto = "si" ; Veredicto = "no"),
    format(string(Respuesta), "Segun las reglas del chatbot, ~w es apta para principiantes: ~w.", [Planta, Veredicto]).

% Muestra un resumen de los cuidados de una planta.
responder(T, Respuesta) :-
    encontrar_planta(T, Planta),
    tiene_palabra(T, ["necesita", "cuidados", "cuidado", "caracteristicas", "características"]),
    luz(Planta, Luz),
    riego(Planta, Riego),
    humedad(Planta, Humedad),
    con_articulo_mayus(Planta, Nombre),
    format(string(Respuesta), "~w necesita luz ~w, riego ~w y humedad ~w.", [Nombre, Luz, Riego, Humedad]).

% ============================================================
% CONSULTAS POR CARACTERISTICA
% ============================================================

% Devuelve plantas que toleran poca luz.
responder(T, Respuesta) :-
    tiene_palabra(T, ["luz", "iluminacion"]),
    tiene_palabra(T, ["poca", "baja"]),
    findall(P, apta_poca_luz(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Las plantas que toleran poca luz son: ~w.", [Texto]).

% Devuelve plantas que necesitan poco riego.
responder(T, Respuesta) :-
    tiene_palabra(T, ["riego", "agua"]),
    tiene_palabra(T, ["poco", "poca", "bajo", "baja"]),
    findall(P, necesita_poco_riego(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Las plantas que necesitan poco riego son: ~w.", [Texto]).

% Devuelve plantas faciles de cuidar.
responder(T, Respuesta) :-
    tiene_palabra(T, ["faciles", "facil", "fáciles", "fácil"]),
    tiene_palabra(T, ["cuidar", "cuidado"]),
    findall(P, facil_cuidado(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Las plantas faciles de cuidar son: ~w.", [Texto]).

% Devuelve plantas recomendadas para principiantes.
responder(T, Respuesta) :-
    tiene_palabra(T, ["principiante", "principiantes"]),
    findall(P, apta_principiante(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Para principiantes sugiero revisar: ~w.", [Texto]).

% Devuelve plantas adecuadas para ambientes humedos.
responder(T, Respuesta) :-
    tiene_palabra(T, ["humedo", "humeda", "humedad", "húmedo", "húmeda"]),
    findall(P, apta_ambiente_humedo(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Las plantas que prefieren alta humedad son: ~w.", [Texto]).

% Devuelve plantas compatibles con hogares con mascotas.
responder(T, Respuesta) :-
    tiene_palabra(T, ["mascota", "mascotas", "perro", "gato"]),
    findall(P, apta_mascotas(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "En esta base, las plantas registradas como seguras para mascotas son: ~w.", [Texto]).

% Devuelve plantas que cumplen condiciones para un bano.
responder(T, Respuesta) :-
    tiene_palabra(T, ["bano", "baño"]),
    findall(P, apta_bano(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Para un bano con luz media, las plantas que cumplen las reglas son: ~w.", [Texto]).

% Devuelve plantas aptas si el usuario suele olvidar el riego.
responder(T, Respuesta) :-
    tiene_palabra(T, ["olvido", "olvidar", "olvidarme", "descuido"]),
    tiene_palabra(T, ["regar", "regarla", "regarlo", "regarlas", "regarlos", "riego", "agua"]),
    findall(P, necesita_poco_riego(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Si sueles olvidar el riego, las plantas de poco riego registradas son: ~w.", [Texto]).

% ============================================================
% CONSULTA INDEFINIDA
% ============================================================

% Mensaje mostrado cuando no existe una regla para la pregunta.
responder(_, "No encontre una regla para esa pregunta. Prueba con consultas sobre luz, riego, humedad, mascotas o cuidados de una planta.").
