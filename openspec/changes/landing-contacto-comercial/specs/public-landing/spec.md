# Public Landing Specification (delta)

## ADDED Requirements

### Requirement: Formulario de contacto comercial en la landing
La landing del portal cliente MUST ofrecer un formulario **"Habla con un asesor"** que envíe a
`POST /publico/contacto`. Campos: nombre (requerido), correo y/o teléfono (al menos uno), mensaje
(opcional) y empresa (opcional); MUST incluir un campo honeypot oculto. MUST mostrar estado de
éxito y de error, sin exponer información interna ni requerir sesión.

#### Scenario: Envío exitoso
- **GIVEN** un visitante que completa nombre + correo (y un mensaje)
- **WHEN** envía el formulario
- **THEN** se llama `POST /publico/contacto` y se muestra confirmación ("te contactaremos")

#### Scenario: Validación mínima en el cliente
- **GIVEN** un envío sin correo ni teléfono
- **THEN** el formulario pide al menos un medio de contacto antes de enviar

#### Scenario: Honeypot oculto
- **GIVEN** el formulario renderizado
- **THEN** existe un campo trampa oculto a usuarios reales que se envía a la API
