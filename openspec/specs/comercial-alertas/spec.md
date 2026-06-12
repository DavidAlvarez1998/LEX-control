# Comercial — Alertas (Derived) Specification

> New capability introduced by change `comercial-funnel`. Adds `GET /comercial/alertas`, a typed bucketed list computed from seven indexed derived queries. There are NO stored alert rows and NO scheduler (none exists in the system); the same query functions are the durable contract a future scheduler would consume.

## ADDED Requirements

### Requirement: Alerts are derived queries, never stored rows
The system MUST expose `GET /comercial/alertas` returning a typed bucketed list of `{ tipo, clienteId, referenciaId, vencidoDesde }`, computed on read and scoped by `empresaId` from the token. It MUST NOT persist any alert row and MUST NOT require a scheduler/cron. The 3-día thresholds MUST be service constants. It MUST be gated by `requireAuth` + `requirePermiso("comercial.alertas.ver")`.

#### Scenario: No alert table
- GIVEN the pushed schema
- WHEN the tables are inspected
- THEN there is no alerts table; alerts are produced only by the read endpoint

#### Scenario: Scoped by token empresaId
- GIVEN a user of despacho A
- WHEN they GET `/comercial/alertas`
- THEN only despacho A's data produces buckets (every underlying query hard-filters `{ empresaId }`)

### Requirement: Seven alert triggers
The endpoint MUST compute these seven buckets: (1) `prospecto-sin-seguimiento-3d` = `Cliente.estado = PROSPECTO` AND (`MAX(SeguimientoComercial.fechaContacto) < now-3d` OR none); (2) `propuesta-sin-respuesta-3d` = `Cotizacion.estadoPropuesta = ENVIADA` AND `fechaEnvio < now-3d`; (3) `contrato-enviado-sin-firmar-3d` = `estadoContrato = ENVIADO` AND `fechaEnvio < now-3d`; (4) `poder-pendiente` = `estadoPoder IN (PENDIENTE, ENVIADO)` AND `estadoContrato = FIRMADO`; (5) `cuota-inicial-no-pagada` = `ConfiguracionCobro.fechaPrimerPago < now` (date-passed heuristic ONLY, provisional until contable supplies payment fact); (6) `cita-hoy` = `SeguimientoComercial.fechaProximaTarea` within today (`REUNION`/`VIDEOLLAMADA`); (7) `tarea-vencida` = `SeguimientoComercial.fechaProximaTarea < now` AND `estadoSeguimiento != CERRADO`. Each MUST use the indexes added by the other comercial capabilities.

#### Scenario: Prospecto with no recent seguimiento
- GIVEN a `PROSPECTO` `Cliente` whose latest `fechaContacto` is 5 days ago
- WHEN the alerts are computed
- THEN it appears in the `prospecto-sin-seguimiento-3d` bucket with `vencidoDesde` set

#### Scenario: Tarea vencida only when not cerrado
- GIVEN a seguimiento with `fechaProximaTarea` yesterday and `estadoSeguimiento = CERRADO`
- WHEN the alerts are computed
- THEN it does NOT appear in `tarea-vencida`

#### Scenario: Cuota-inicial is a date-passed heuristic
- GIVEN a `ConfiguracionCobro` with `fechaPrimerPago` in the past
- WHEN the alerts are computed
- THEN it appears in `cuota-inicial-no-pagada` regardless of any payment fact (which comercial does not store)

### Requirement: Computed fields live in the serializer layer
`saldoPendiente` (placeholder), `diasSinSeguimiento`, `conversionACliente`, and `diasEnFase` MUST be computed in the read/serializer layer and MUST NEVER be persisted.

#### Scenario: diasEnFase computed not stored
- GIVEN a `Cliente` with an open `fases_comerciales` row
- WHEN its `diasEnFase` is read
- THEN it is computed as `(fechaCierreFase ?? now) - fechaInicioFase` and is not a stored column

### Requirement: Alert items are actionable (carry the cliente identity)
> MODIFIED by change `comercial-seguimiento-accionable`.

Every alert item returned by `GET /comercial/alertas` MUST carry the cliente identity needed to act directly from the list — `clienteId` plus `nombre`, and `telefono` for the buckets where a call/WhatsApp is the action (`prospecto-sin-seguimiento-3d`, `cita-hoy`, `tarea-vencida`). The `Inicio` panel is therefore no longer dead counts: each alert links to the cockpit / `/clientes` filtered. This MUST remain a derived read (no stored alert rows, no scheduler) and the buckets/triggers are unchanged.

#### Scenario: Prospecto-sin-seguimiento item is actionable
- GIVEN a `PROSPECTO` with no recent seguimiento
- WHEN `/comercial/alertas` is read
- THEN its `prospecto-sin-seguimiento-3d` item carries `clienteId`, `nombre`, and `telefono`

#### Scenario: Cita-hoy / tarea-vencida items carry contact data
- GIVEN a seguimiento producing a `cita-hoy` or `tarea-vencida` alert
- WHEN the alerts are read
- THEN the item carries the cliente's `nombre` and `telefono` (resolved via the seguimiento's `cliente` relation)