:- consult('chatbot.pl').
:- use_module(library(http/json)).
:- initialization(main, main).

main :-
    set_stream(user_input, encoding(utf8)),
    set_stream(user_output, encoding(utf8)),
    json_read_dict(user_input, Datos),
    once(responder_texto(Datos.pregunta, Respuesta)),
    json_write_dict(user_output, _{respuesta: Respuesta}),
    nl.