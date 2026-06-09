# Comercial — Fases (Pipeline) Specification

> New capability introduced by change `comercial-funnel`. Adds the `FaseComercial` sales pipeline as an append-only `FaseComercialHistorial` over the existing `Cliente`. The fase axis is fine-grained and ORTHOGONAL to the coarse `Cliente.estado`. No fase columns are added to `Cliente` (that would redefine it).

## ADDED Requirements

### Requirement: FaseComercialHistorial as an append-only pipeline log
The system MUST store the pipeline as append-only rows in `fases_comerciales`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like `UsuarioRolEmpresa`), `clienteId` FK→`Cliente` (Cascade), `fase` `FaseComercial`, `fechaInicioFase` (default now), optional `fechaCierreFase` (NULL = current/open), optional `motivoPerdida` (Text), optional `responsableComercialId` FK→`Usuario` (SetNull), optional `registradoPorId` FK→`Usuario` (SetNull), `createdAt`. It MUST index `@@index([empresaId])`, `@@index([clienteId, fechaCierreFase])`, `@@index([fase])`. The CURRENT fase MUST be the single row per `cliente` with `fechaCierreFase IS NULL`. `días-en-fase` MUST be computed at query time as `(fechaCierreFase ?? now) - fechaInicioFase` and MUST NOT be stored.

#### Scenario: Current fase is the open row
- GIVEN a `Cliente` with two `fases_comerciales` rows, one closed and one with `fechaCierreFase = null`
- WHEN the current fase is queried
- THEN the open row (`fechaCierreFase IS NULL`) is returned via the `@@index([clienteId, fechaCierreFase])`

#### Scenario: No fase columns on Cliente
- GIVEN the pushed schema
- WHEN `clientes` is inspected
- THEN it has NO `fase`/`faseDesde`/`motivoPerdida` columns AND `Cliente` exposes only a virtual `faseHistorial` back-relation

### Requirement: Enum FaseComercial
The system MUST define `FaseComercial { LEAD, CONTACTO, EVALUACION, PROPUESTA, NEGOCIACION, CONTRATO, PODERES, FIRMADO, PERDIDO }`, additive and not modifying existing enums. `FIRMADO` and `PERDIDO` MUST be terminal.

#### Scenario: Enum available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `FaseComercial` exists with the listed members AND no existing enum is changed

### Requirement: Fase transition is validated and atomic (close-then-open)
`POST /comercial/clientes/:id/fase` MUST validate the target against an allowed-edges map (forward `LEAD → … → FIRMADO`; `PERDIDO` reachable from any non-terminal fase; `FIRMADO`/`PERDIDO` terminal). It MUST require `motivoPerdida` when the target is `PERDIDO`. The transition MUST run in one `$transaction` that closes the prior open row (`fechaCierreFase = now()`) and inserts the new open row, holding a lock on the `clientes` row so at most one open row per cliente exists. It MUST be gated by `requireAuth` + `requirePermiso("comercial.fase.mover")`; reads by `comercial.fase.ver`.

#### Scenario: Valid forward transition
- GIVEN a `Cliente` whose current fase is `CONTACTO`
- WHEN a user moves it to `EVALUACION`
- THEN the `CONTACTO` row is closed (`fechaCierreFase = now`) and a new open `EVALUACION` row is inserted in the same transaction

#### Scenario: PERDIDO requires motivo
- GIVEN a `Cliente` in a non-terminal fase
- WHEN a user moves it to `PERDIDO` without `motivoPerdida`
- THEN the transition is rejected

#### Scenario: Disallowed edge rejected
- GIVEN a `Cliente` whose current fase is `FIRMADO` (terminal)
- WHEN a user attempts any transition
- THEN it is rejected by the allowed-edges map

### Requirement: Terminal fases couple to Cliente.estado in the same transaction
When the target fase is `FIRMADO`, the same transaction MUST drive the existing conversion machinery (`Cliente.estado → CLIENTE`, find-or-create `Litigante` by `(empresaId, tipoDocumento, numeroDocumento)`, set `convertidoEn`). When the target is `PERDIDO`, the same transaction MUST set `Cliente.estado → DESCARTADO`. `Cliente.estado` MUST NOT be edited independently for these transitions, so the two state machines cannot drift. The `Cliente.estado` (PROSPECTO/CLIENTE/DESCARTADO) axis MUST remain orthogonal to the `FaseComercial` axis for all non-terminal fases.

#### Scenario: FIRMADO converts the cliente
- GIVEN a `PROSPECTO` `Cliente` with `tipoDocumento = CC`, `numeroDocumento = 123` in despacho A
- WHEN it is moved to fase `FIRMADO`
- THEN in one transaction the open `FIRMADO` row is created AND `Cliente.estado = CLIENTE`, `convertidoEn` is set, and a `Litigante` is upserted on `(empresaId, CC, 123)` and linked

#### Scenario: PERDIDO discards the cliente
- GIVEN a `PROSPECTO` `Cliente`
- WHEN it is moved to fase `PERDIDO` with a `motivoPerdida`
- THEN in one transaction the open `PERDIDO` row is created AND `Cliente.estado = DESCARTADO`

#### Scenario: Non-terminal fase does not touch estado
- GIVEN a `PROSPECTO` `Cliente` in fase `LEAD`
- WHEN it is moved to `PROPUESTA`
- THEN `Cliente.estado` remains `PROSPECTO`