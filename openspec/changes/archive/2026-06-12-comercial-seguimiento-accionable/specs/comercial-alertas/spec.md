# Comercial — Alertas (delta)

## MODIFIED Requirements

### Requirement: Alert items are actionable (carry the cliente identity)
Every alert item returned by `GET /comercial/alertas` MUST carry the cliente identity needed to act directly from the list — `clienteId` plus `nombre`, and `telefono` for the buckets where a call/WhatsApp is the action (`prospecto-sin-seguimiento-3d`, `cita-hoy`, `tarea-vencida`). The `Inicio` panel is therefore no longer dead counts: each alert links to the cockpit / `/clientes` filtered. This MUST remain a derived read (no stored alert rows, no scheduler) and the buckets/triggers are unchanged.

#### Scenario: Prospecto-sin-seguimiento item is actionable
- GIVEN a `PROSPECTO` with no recent seguimiento
- WHEN `/comercial/alertas` is read
- THEN its `prospecto-sin-seguimiento-3d` item carries `clienteId`, `nombre`, and `telefono`

#### Scenario: Cita-hoy / tarea-vencida items carry contact data
- GIVEN a seguimiento producing a `cita-hoy` or `tarea-vencida` alert
- WHEN the alerts are read
- THEN the item carries the cliente's `nombre` and `telefono` (resolved via the seguimiento's `cliente` relation)
