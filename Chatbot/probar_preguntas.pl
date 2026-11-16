:- encoding(utf8).

% ============================================================
% PRUEBA DE LAS 20 PREGUNTAS (versión Prolog)
% ============================================================
% Lee preguntas_prueba.txt y muestra la respuesta del chatbot a cada una.
% Sirve para llenar la tabla del informe de forma reproducible.
%
% Ejecutar desde la carpeta principal del repositorio:
%   swipl -q -s Chatbot/probar_preguntas.pl -g probar,halt
%
% Para usar otro archivo de preguntas numeradas:
%   swipl -q -s Chatbot/probar_preguntas.pl -g "probar('preguntas_robustez.txt'),halt"

:- consult('chatbot.pl').

archivo_preguntas('preguntas_prueba.txt').

% Muestra "N. pregunta" y la respuesta correspondiente (archivo por defecto).
probar :-
    archivo_preguntas(Archivo),
    probar(Archivo).

% Igual que probar/0, pero con el archivo de preguntas indicado.
probar(Archivo) :-
    % Salida en UTF-8 aunque la terminal use otro locale (p. ej. LANG=C).
    set_stream(user_output, encoding(utf8)),
    read_file_to_string(Archivo, Contenido, [encoding(utf8)]),
    split_string(Contenido, "\n", "\r ", Lineas),
    forall(
        (   member(Linea, Lineas),
            split_string(Linea, ".", "", [Numero, Resto]),
            number_string(_, Numero)
        ),
        (   split_string(Resto, "", " ", [Pregunta]),
            responder_texto(Pregunta, Respuesta),
            format("~w.~w~n   -> ~s~n~n", [Numero, Resto, Respuesta])
        )
    ).
