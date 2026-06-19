# Public Marketing API Specification (delta)

## ADDED Requirements

### Requirement: Endpoint público de contacto comercial
El sistema MUST exponer `POST /publico/contacto` **sin autenticación**, bajo el mismo rate-limit
y honeypot que el resto de `/publico`. Al recibir un contacto válido MUST crear un `Prospecto`
con `canalEntrada = WEB`, **sin comercial asignado** (`comercialId = null`), `estado = NUEVO`, y el
mensaje del visitante guardado en `notas` (con un prefijo que lo identifique como contacto de
landing). Campos requeridos: `nombreContacto` y al menos uno de (`email`, `telefono`);
`nombreEmpresa` y `mensaje` son opcionales.

#### Scenario: Contacto válido crea un prospecto sin asignar
- **GIVEN** un visitante de la landing que envía nombre + correo (y un mensaje)
- **WHEN** hace `POST /publico/contacto`
- **THEN** se crea un `Prospecto` con `canalEntrada = WEB`, `comercialId = null`, `estado = NUEVO`
- **AND** el mensaje queda en `notas`
- **AND** la respuesta es 201 sin exponer datos internos

#### Scenario: Falta el medio de contacto
- **GIVEN** un envío sin `email` ni `telefono`
- **WHEN** hace `POST /publico/contacto`
- **THEN** se rechaza con 400 (validación)

#### Scenario: Honeypot descarta el bot
- **GIVEN** un envío con el campo trampa (honeypot) lleno
- **WHEN** hace `POST /publico/contacto`
- **THEN** la API responde ok pero NO crea ningún prospecto

#### Scenario: Rate limit
- **GIVEN** demasiados envíos desde un mismo origen en la ventana
- **THEN** se aplica el límite de `/publico` (no crea más prospectos)
