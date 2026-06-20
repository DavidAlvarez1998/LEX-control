# Integraciones Externas (delta) — capacidad: notificaciones

Añade la integración del microservicio API_NOTIFICAR (correo/SMS/llamadas) cumpliendo la convención
canónica [[convencion-integraciones-externas]]. Solo capacidad backend (sin router ni front).

## ADDED Requirements

### Requirement: Capacidad de notificación por correo, SMS y llamada
El sistema DEBE poder enviar correo (`enviarCorreo`), SMS (`enviarSms`) y disparar/consultar llamadas
TTS (`llamar`, `consultarEstadoLlamada`) contra el microservicio API_NOTIFICAR, aislando todo `fetch`
en el módulo `src/modules/notificaciones/` y normalizando cada respuesta a un DTO propio. El host y el
timeout salen de `env.notificaciones`. Estas funciones son la capacidad backend; aún NO se exponen por
HTTP ni se consumen desde los frontends.

#### Scenario: Envío de correo normalizado
- GIVEN parámetros `{ to, subject, html }`
- WHEN se llama `enviarCorreo`
- THEN hace POST a `/email/enviar` y devuelve `{ enviado, messageId }`

#### Scenario: SMS con fallo lógico en respuesta 200
- GIVEN el proveedor responde `200 { message: "Falló" }`
- WHEN se llama `enviarSms`
- THEN NO lanza y devuelve `{ enviado: false, mensajeProveedor: "Falló" }`

#### Scenario: Llamada en dos pasos
- GIVEN un `telefono`
- WHEN se llama `llamar` y luego `consultarEstadoLlamada(campaignId)`
- THEN el primero devuelve `campaignId` y el segundo el estado, marcando `termino` cuando es definitivo

#### Scenario: Proveedor caído o lento
- GIVEN el microservicio no responde a tiempo o devuelve error
- WHEN se invoca cualquier canal
- THEN se lanza `HttpError(502)` (no cuelga la request)

### Requirement: Las pruebas no envían contra el proveedor real en el gate
Por ser canales de COBRO, las pruebas automatizadas (`tests/notificaciones.test.ts`) DEBEN mockear
`fetch` y no realizar envíos reales. El envío real solo ocurre mediante un script de smoke explícito
(`scripts/smoke-notificaciones.ts`) que exige confirmación (`--confirmar`) y NO forma parte del gate
ni de CI.

#### Scenario: Gate sin costo
- GIVEN la suite de tests corre en el gate/CI
- WHEN se ejecutan los tests de notificaciones
- THEN ningún correo/SMS/llamada real se envía (todo `fetch` está mockeado)
