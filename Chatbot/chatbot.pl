
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
lista_a_texto([], "ninguna").
lista_a_texto(Lista, Texto) :-
    atomic_list_concat(Lista, ', ', Texto).

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
    format(string(Respuesta), "Si, conozco la ~w y tengo informacion sobre sus cuidados.", [Planta]).

% ============================================================
% CONSULTAS SOBRE UNA PLANTA
% ============================================================

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
    format(string(Respuesta), "La ~w necesita luz ~w, riego ~w y humedad ~w.", [Planta, Luz, Riego, Humedad]).

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
    tiene_palabra(T, ["regar", "riego", "agua"]),
    findall(P, necesita_poco_riego(P), Plantas),
    lista_a_texto(Plantas, Texto),
    format(string(Respuesta), "Si sueles olvidar el riego, las plantas de poco riego registradas son: ~w.", [Texto]).

% ============================================================
% CONSULTA INDEFINIDA
% ============================================================

% Mensaje mostrado cuando no existe una regla para la pregunta.
responder(_, "No encontre una regla para esa pregunta. Prueba con consultas sobre luz, riego, humedad, mascotas o cuidados de una planta.").
