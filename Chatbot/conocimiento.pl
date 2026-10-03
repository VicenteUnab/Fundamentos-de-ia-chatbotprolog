% ============================================================
% BASE DE CONOCIMIENTO: PLANTAS DE INTERIOR
% ============================================================

% -------------------------
% Plantas conocidas
% -------------------------
planta(sansevieria).
planta(zamioculca).
planta(potus).
planta(cinta).
planta(helecho).
planta(calathea).
planta(suculenta).
planta(ficus).

% -------------------------
% Caracteristicas de luz
% -------------------------
luz(sansevieria, baja).
luz(zamioculca, baja).
luz(potus, media).
luz(cinta, media).
luz(helecho, media).
luz(calathea, media).
luz(suculenta, alta).
luz(ficus, alta).

% -------------------------
% Necesidad de riego
% -------------------------
riego(sansevieria, bajo).
riego(zamioculca, bajo).
riego(potus, medio).
riego(cinta, medio).
riego(helecho, alto).
riego(calathea, alto).
riego(suculenta, bajo).
riego(ficus, medio).

% -------------------------
% Resistencia general
% -------------------------
resistente(sansevieria).
resistente(zamioculca).
resistente(potus).
resistente(cinta).
resistente(suculenta).

% -------------------------
% Necesidad de humedad
% -------------------------
humedad(sansevieria, baja).
humedad(zamioculca, baja).
humedad(potus, media).
humedad(cinta, media).
humedad(helecho, alta).
humedad(calathea, alta).
humedad(suculenta, baja).
humedad(ficus, media).

% -------------------------
% Compatibilidad con mascotas
% -------------------------
segura_mascotas(cinta).
segura_mascotas(helecho).
segura_mascotas(calathea).

% ============================================================
% REGLAS DE INFERENCIA
% ============================================================

% Una planta de poca luz tolera lugares con poca iluminacion.
apta_poca_luz(X) :- planta(X), luz(X, baja).

% Una planta de poco riego requiere poca agua.
necesita_poco_riego(X) :- planta(X), riego(X, bajo).

% Una planta resistente y de poco riego es facil de cuidar.
facil_cuidado(X) :- planta(X), resistente(X), riego(X, bajo).

% Una planta resistente es adecuada para principiantes.
apta_principiante(X) :- planta(X), resistente(X).

% Una planta de alta humedad es adecuada para ambientes humedos.
apta_ambiente_humedo(X) :- planta(X), humedad(X, alta).

% Una planta segura para mascotas puede ubicarse en hogares con mascotas.
apta_mascotas(X) :- planta(X), segura_mascotas(X).

% Una planta puede servir para un bano si tolera humedad alta y luz media.
apta_bano(X) :- planta(X), humedad(X, alta), luz(X, media).
