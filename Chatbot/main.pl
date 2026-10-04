:- encoding(utf8).

% ============================================================
% PUNTO DE ENTRADA DEL CHATBOT (CONSOLA)
% ============================================================
% Este archivo solo maneja la conversacion por consola.
% La logica de respuesta vive en chatbot.pl (responder_texto/2).

:- consult('chatbot.pl').
:- use_module(library(readutil)).

% Inicia el chatbot cuando se ejecuta este archivo.
:- initialization(iniciar, main).

% Muestra el mensaje inicial.
iniciar :-
    nl,
    writeln('=============================================='),
    writeln(' CHATBOT DE PLANTAS DE INTERIOR - PROLOG'),
    writeln(' Escribe "ayuda" para ver ejemplos.'),
    writeln(' Escribe "salir" para terminar.'),
    writeln('=============================================='),
    bucle.

% Mantiene la conversacion hasta que el usuario salga.
bucle :-
    write('Tu: '),
    flush_output,
    read_line_to_string(user_input, Entrada),
    procesar(Entrada).

% Fin de la entrada (Ctrl+D o stdin cerrado): termina sin error.
procesar(end_of_file) :-
    !,
    nl,
    writeln('Bot: Hasta luego.').
% El usuario pide salir.
procesar(Entrada) :-
    terminar(Entrada),
    !,
    writeln('Bot: Hasta luego.'),
    nl.
% Pregunta normal: responde y sigue conversando.
procesar(Entrada) :-
    responder_texto(Entrada, Respuesta),
    format('Bot: ~s~n~n', [Respuesta]),
    bucle.

% Reconoce las formas basicas de salida.
terminar(Entrada) :-
    tokenizar(Entrada, Tokens),
    member(Palabra, Tokens),
    member(Palabra, ["salir", "adios", "adiós"]),
    !.
