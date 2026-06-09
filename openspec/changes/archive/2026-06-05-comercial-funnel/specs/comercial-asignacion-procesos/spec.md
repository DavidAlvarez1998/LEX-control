# Comercial — Asignación de Procesos (Bridge) Specification

> New capability introduced by change `comercial-funnel`. Adds `SolicitudAsignacionProceso`, the bridge from Cliente(comercial) to Proceso(legal). The assign transaction is the ONE place comercial writes into the legal módulo: it materializes a `Proceso` + `Litigante` + `ParteProceso` using the existing legal-write rules. Snapshots preserve traceability after later `Cliente` edits.

## ADDED Requirements

### Requirement: SolicitudAsignacionProceso as the Cliente→Proceso bridge
The system MUST store assignment requests in `solicitudes_asignacion_proceso`: `id` (cuid), `empresaId` (denormalized, plain indexed column with NO FK — avoids the errno-150 diamond `Empresa→Cliente→here` AND `Empresa→here`, mirroring `UsuarioRolEmpresa`), `clienteId` FK→`Cliente` (Cascade — the SINGLE cascade root), optional `contratoId` `@unique` FK→`ContratoComercial` (SetNull — one solicitud per signed contract), optional `tipoProcesoId` FK→`TipoProceso` (SetNull, may be global), `estado` `EstadoSolicitud` (default `PENDIENTE`), optional `prioridad` `Prioridad?` (default `MEDIA`, reusing the existing enum), optional `jurisdiccionSugerida` `Jurisdiccion?`, optional `rolParteSugerido` `RolParte?`, optional `tituloPropuesto`, optional `resumenCaso` (Text, SNAPSHOT), optional `cobroSnapshot` (Json, frozen agreed terms), optional `notaComercial` (Text), optional `tareasDefinidas` (Text), optional `solicitadoPorId`/`asignadoPorId`/`abogadoAsignadoId` FK→`Usuario` (SetNull, three named relations), optional `procesoId` `@unique` FK→`Proceso` (SetNull, bidirectional traceability), optional `motivoRechazo` (Text), `fechaSolicitud` (default now), optional `fechaAsignacion`, `createdAt`, `updatedAt`. It MUST index `@@index([empresaId, estado])`, `@@index([clienteId])`, `@@index([abogadoAsignadoId, estado])`. Only `Cliente` cascades in (its Cascade cleans these rows; an `Empresa` delete reaches them via the `Cliente` cascade — the denormalized `empresaId` carries NO FK). Every cross-module FK (`contratoId`/`tipoProcesoId`/`procesoId`/the three `Usuario` FKs) MUST be `SetNull`. A NEW back-relation `solicitudComercial SolicitudAsignacionProceso?` MUST be added to `Proceso` (explicit 1:1 inverse for the `procesoId @unique` side; no column change to `tramites`). The existing enums `Prioridad`, `Jurisdiccion`, `RolParte` MUST be reused (not duplicated).

#### Scenario: Reusing existing enums
- GIVEN the pushed schema
- WHEN the solicitud columns are inspected
- THEN `prioridad`/`jurisdiccionSugerida`/`rolParteSugerido` use the existing `Prioridad`/`Jurisdiccion`/`RolParte` enums and no duplicate enum is created

#### Scenario: procesoId SetNull preserves the audit
- GIVEN an `ASIGNADA` solicitud whose `procesoId` points at a `Proceso`
- WHEN that `Proceso` is deleted
- THEN the solicitud survives with `procesoId = null` (audit not cascade-deleted)

### Requirement: Enum EstadoSolicitud and its state machine
The system MUST define `EstadoSolicitud { PENDIENTE, EN_REVISION, ASIGNADA, RECHAZADA, CANCELADA }` (additive). The lifecycle MUST be `PENDIENTE → EN_REVISION → ASIGNADA | RECHAZADA | CANCELADA`, with `CANCELADA` the comercial-side withdrawal.

#### Scenario: Enum available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `EstadoSolicitud` exists with the listed members AND no existing enum is changed

### Requirement: Create a solicitud only from a fully-signed engagement
`POST /comercial/solicitudes` (`comercial.solicitud.crear`) MUST require the cliente's `ContratoComercial` to have `estadoContrato = FIRMADO` AND `estadoPoder = FIRMADO`, enforce one solicitud per contract via `contratoId @unique`, snapshot `resumenCaso` and `cobroSnapshot` at request time, default `tipoProcesoId` from `Cliente.necesidadTipoProcesoId`, and set `estado = PENDIENTE`. It MUST take `empresaId` from the token and `assertSameEmpresa` on every FK.

#### Scenario: Unsigned contract blocks the request
- GIVEN a `ContratoComercial` with `estadoPoder = PENDIENTE`
- WHEN a solicitud is requested for it
- THEN the request is rejected (engagement not fully signed)

#### Scenario: Snapshot survives later Cliente edits
- GIVEN a solicitud created with a `resumenCaso` snapshot
- WHEN the underlying `Cliente.resumenCaso` is later edited
- THEN the solicitud's snapshot is unchanged (traceability preserved)

#### Scenario: One solicitud per contract
- GIVEN a `ContratoComercial` that already has a solicitud
- WHEN a second solicitud references the same `contratoId`
- THEN it is rejected by the `@unique` on `contratoId`

### Requirement: Admin inbox over the funnel data
`GET /comercial/solicitudes?estado=PENDIENTE` (`comercial.solicitud.ver`, ADMINISTRADOR) MUST list requests via `@@index([empresaId, estado])`, and the admin MUST be able to reach all related comercial data (`Cliente`, `ContratoComercial`, `Cotizacion`, `ConfiguracionCobro`) by FK plus the immutable snapshots — full traceability with zero duplication.

#### Scenario: Pending inbox
- GIVEN three solicitudes of despacho A, two `PENDIENTE`
- WHEN an ADMINISTRADOR of A lists `?estado=PENDIENTE`
- THEN exactly the two pending solicitudes of A are returned

### Requirement: Assign materializes Proceso + Litigante + ParteProceso in one transaction
`POST /comercial/solicitudes/:id/asignar` (`comercial.solicitud.asignar`, ADMINISTRADOR ONLY) MUST, in one `$transaction`, compare-and-set `estado` from `PENDIENTE`/`EN_REVISION` to `ASIGNADA`; `assertSameEmpresa` on `contratoId`/`tipoProcesoId`/`abogadoAsignadoId` AND assert `abogadoAsignadoId` holds `RolEmpresa.JURIDICO`; resolve the tipo: `tipoProcesoId = adminOverride ?? Cliente.necesidadTipoProcesoId` (DECISION Q4: the ADMINISTRADOR MAY override the comercial-proposed tipo at assign time) — if STILL null, or if the resolved `TipoProceso` defines no `etapas`, return 400 (a Proceso cannot be materialized without a tipo and an entry stage); find-or-create the `Litigante` via a SHARED service fn `findOrCreateLitiganteByDoc(tx, empresaId, cliente)` **extracted from** the current `/convertir` handler (it is NOT exported today → `clientes.router.ts` is Modified to expose it), and set `Cliente.litiganteId` if unset; create `Proceso` with ALL its REQUIRED fields: `{ empresaId from Cliente, tipoProcesoId resolved, titulo = tituloPropuesto, estado = ABIERTO, prioridad, responsableId = abogadoAsignadoId, creadoPorId = asignadoPorId, datos = {} (no funnel field maps onto the dynamic esquema), etapaActual = etapaEntrada(tipoProceso.etapas).key, codigoInterno = "COM-<YYYY>-<NNNN>" (DECISION Q3: comercial-origin prefix; sequence per empresa), tipoEsquemaVersion = snapshot of tipoProceso.esquemaVersion, jurisdiccion = tipoProceso.jurisdiccion (NOT jurisdiccionSugerida — that field is only a UI hint for picking the tipo) }`; create `ParteProceso { procesoId, litiganteId, rol = rolParteSugerido ?? DEMANDANTE (default when unset), esNuestroCliente = true }` (idempotent via its `@@unique([procesoId, litiganteId, rol])`); and stamp `solicitud.{ procesoId @unique, abogadoAsignadoId, asignadoPorId, tareasDefinidas, fechaAsignacion }`. NOTE: the `codigoInterno` generator and `etapaEntrada` are INLINE in `procesos.router.ts` today and MUST be extracted into shared legal helpers both that router and this bridge import (`procesos.router.ts` is Modified). This is the one place comercial writes into the legal módulo and MUST be flagged.

#### Scenario: Successful assignment
- GIVEN a `PENDIENTE` solicitud of despacho A with an `abogadoAsignadoId` holding `JURIDICO`
- WHEN an ADMINISTRADOR of A assigns it
- THEN in one transaction the solicitud becomes `ASIGNADA`, a `Proceso` is created (`estado = ABIERTO`, `codigoInterno` unique per empresa, `tipoEsquemaVersion` snapshotted), a `ParteProceso` with `esNuestroCliente = true` is created, and `solicitud.procesoId` is stamped

#### Scenario: Abogado must hold JURIDICO
- GIVEN a solicitud whose `abogadoAsignadoId` does NOT hold `RolEmpresa.JURIDICO`
- WHEN an ADMINISTRADOR attempts to assign it
- THEN the assignment is rejected and no `Proceso` is created

#### Scenario: Compare-and-set guards double assignment
- GIVEN a solicitud already `ASIGNADA`
- WHEN a second assign is attempted
- THEN the compare-and-set fails and no second `Proceso` is created

#### Scenario: COMERCIAL cannot self-assign
- GIVEN a user holding only `RolEmpresa.COMERCIAL`
- WHEN they call `/asignar`
- THEN `requirePermiso("comercial.solicitud.asignar")` returns 403 (assign/rechazar are ADMINISTRADOR-only)

### Requirement: Reject and cancel
`POST /comercial/solicitudes/:id/rechazar` (`comercial.solicitud.rechazar`, ADMINISTRADOR ONLY) MUST set `estado = RECHAZADA` and record `motivoRechazo`. The comercial-side withdrawal MUST set `estado = CANCELADA` (covered by `comercial.solicitud.crear`-owner scope). Neither MUST create a `Proceso`.

#### Scenario: Reject records motivo
- GIVEN a `PENDIENTE` solicitud
- WHEN an ADMINISTRADOR rejects it with a `motivoRechazo`
- THEN `estado = RECHAZADA`, `motivoRechazo` is stored, and no `Proceso` exists

### Requirement: Bidirectional traceability for the abogado
The `JURIDICO` view MUST be filterable by `abogadoAsignadoId` via `@@index([abogadoAsignadoId, estado])`, and the chain `Cliente → ContratoComercial → SolicitudAsignacionProceso → Proceso` MUST be walkable both ways via the `@unique` FKs. The live `Proceso` MUST be reachable from the solicitud while the immutable `resumenCaso`/`cobroSnapshot`/`notaComercial` show exactly what comercial registered.

#### Scenario: Abogado finds assigned procesos
- GIVEN an abogado holding `JURIDICO`
- WHEN they query their assigned solicitudes
- THEN solicitudes with their `abogadoAsignadoId` and `estado = ASIGNADA` are returned, each linking to its live `Proceso` and frozen snapshots