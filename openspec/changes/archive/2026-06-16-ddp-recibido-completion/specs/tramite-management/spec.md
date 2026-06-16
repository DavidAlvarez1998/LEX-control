# Tramite Management — delta: Derecho de Petición Recibido response

## ADDED Requirements

### Requirement: Send channel and proof when answering a received petition
For `Derecho de Petición Recibido`, when we record that the petition was answered, the "Respuesta" stage
MUST require the send channel `medioRespuesta` for `contestada = SI` and `contestada = PARCIAL` (alongside
`fechaContestacion` and the `respuesta.pdf` document). The system MUST offer an optional proof-of-sending
document that depends on the channel: `acuse-correo.pdf` when `medioRespuesta = "Correo electrónico"`, and
`constancia-envio.pdf` when `medioRespuesta = "Físico"`. The proof document MUST NOT block stage advance.

#### Scenario: Answer by email
- GIVEN a `Derecho de Petición Recibido` at the "Respuesta" stage
- WHEN `contestada = SI` and `medioRespuesta = "Correo electrónico"`
- THEN `fechaContestacion`, `medioRespuesta` and `respuesta.pdf` are required to complete the stage
- AND `acuse-correo.pdf` is offered as an optional document

#### Scenario: Answer physically
- GIVEN a `Derecho de Petición Recibido` at the "Respuesta" stage
- WHEN `contestada = SI` and `medioRespuesta = "Físico"`
- THEN `constancia-envio.pdf` is offered as an optional document

#### Scenario: Channel is mandatory to complete the response
- GIVEN `contestada = SI` with `fechaContestacion` and `respuesta.pdf` provided
- WHEN `medioRespuesta` is empty
- THEN the stage cannot be completed until `medioRespuesta` is set
