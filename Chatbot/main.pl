% ============================================================
% PUNTO DE ENTRADA DEL CHATBOT
% ============================================================

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
    read_line_to_string(user_input, Entrada),
    (   terminar(Entrada)
    ->  writeln('Bot: Hasta luego.'), nl
    ;   tokenizar(Entrada, Tokens),
        responder(Tokens, Respuesta),
        format('Bot: ~s~n~n', [Respuesta]),
        bucle
    ).

% Reconoce las formas basicas de salida.
terminar(Entrada) :-
    tokenizar(Entrada, Tokens),
    member(Palabra, Tokens),
    member(Palabra, ["salir", "adios", "adiós"]),
    !.
