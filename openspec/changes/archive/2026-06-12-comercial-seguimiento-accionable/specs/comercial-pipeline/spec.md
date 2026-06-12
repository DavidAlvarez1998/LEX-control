# Comercial — Pipeline & Cockpit (Derived) Specification

> New capability introduced by change `comercial-seguimiento-accionable`. Adds two read-only endpoints over the existing `Cliente` + `SeguimientoComercial` + `FaseComercialHistorial` data: `GET /comercial/pipeline` (per-cliente derived signals to read the funnel at a glance) and `GET /comercial/hoy` (the daily "¿a quién contacto hoy?" cockpit). Every field is computed on read; NOTHING is stored. Reuses the on-read derivation pattern of `comercial-alertas` and the `soloMisClientes` scoping. No new permissions, no scheduler.

## ADDED Requirements

### Requirement: Pipeline returns per-cliente derived signals, never stored
The system MUST expose `GET /comercial/pipeline` returning the despacho's clientes with signals computed on read: `faseActual` + `diasEnFase`, `ultimaGestionEn` + `diasSinGestion`, `ultimaDisposicion`, `proximaTareaEn` + `proximaTarea` + `tareaVencida`, plus identity fields (`id`, `nombre`, `telefono`, `estado`, `viabilidad`, `canalIngreso`). It MUST include only clientes with `estado IN (PROSPECTO, CLIENTE)`, hard-filter `WHERE { empresaId }` from the token, and MUST NOT persist any of the derived fields. It MUST be gated by `requireAuth` + `requirePermiso("cliente.ver")`.

#### Scenario: Signals computed on read
- GIVEN a `PROSPECTO` whose latest `SeguimientoComercial.fechaContacto` is 10 days ago
- WHEN a user of that despacho GETs `/comercial/pipeline`
- THEN the cliente carries `diasSinGestion = 10` and `ultimaGestionEn` set, computed (not stored)

#### Scenario: Open fase drives faseActual / diasEnFase
- GIVEN a cliente with an open `fases_comerciales` row in `NEGOCIACION` started 5 days ago
- WHEN the pipeline is read
- THEN that cliente carries `faseActual = NEGOCIACION` and `diasEnFase = 5`

#### Scenario: Next open task marks tareaVencida
- GIVEN a cliente whose earliest non-completed, non-cancelled `fechaProximaTarea` is in the past
- WHEN the pipeline is read
- THEN that cliente carries `tareaVencida = true` with `proximaTareaEn`/`proximaTarea` set; a future or absent task yields `tareaVencida = false`

#### Scenario: ultimaDisposicion is the most recent typed disposition
- GIVEN a cliente whose latest seguimiento bearing a `disposicion` is `INTERESADO`
- WHEN the pipeline is read
- THEN `ultimaDisposicion = INTERESADO`

#### Scenario: Only mine when scoped
- GIVEN a user passing `?mios=true`
- WHEN they read the pipeline
- THEN only clientes whose `responsableComercialId` is the requesting user are returned

#### Scenario: Cross-tenant isolation
- GIVEN clientes of despacho B
- WHEN a user of despacho A reads the pipeline
- THEN despacho B's clientes are NOT returned (hard `WHERE { empresaId }`)

### Requirement: Cockpit "hoy" buckets the day into vencidas / hoy / fríos
The system MUST expose `GET /comercial/hoy` returning three actionable buckets, each item carrying what is needed to act (`clienteId`, `nombre`, `telefono`, and for task items `tipoGestion` + `tarea` + `fechaProximaTarea`): (1) `vencidas` = open seguimiento tasks (`completada = false`, `canceladaEn = null`) with `fechaProximaTarea` before the start of today; (2) `hoy` = the same with `fechaProximaTarea` within today (start ≤ x < start+1d); (3) `frios` = `PROSPECTO` clientes with NO seguimiento in the last 3 days AND no open future task. It MUST hard-filter `WHERE { empresaId }`, honor `?mios`, compute everything on read, and be gated by `requireAuth` + `requirePermiso("cliente.ver")`.

#### Scenario: Overdue task lands in vencidas
- GIVEN an open task with `fechaProximaTarea` yesterday
- WHEN `/comercial/hoy` is read
- THEN that task appears in `vencidas` with the cliente's `nombre`/`telefono`

#### Scenario: Today's task lands in hoy
- GIVEN an open task with `fechaProximaTarea` today
- WHEN `/comercial/hoy` is read
- THEN that task appears in `hoy`

#### Scenario: Untouched prospect lands in fríos
- GIVEN a `PROSPECTO` with no seguimiento in the last 3 days and no open future task
- WHEN `/comercial/hoy` is read
- THEN it appears in `frios` (task fields null, `clienteId`/`nombre`/`telefono` present)

#### Scenario: Completed or cancelled tasks are excluded
- GIVEN a task whose `completada = true` OR `canceladaEn` is set
- WHEN `/comercial/hoy` is read
- THEN it appears in neither `vencidas` nor `hoy`
