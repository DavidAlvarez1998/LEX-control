# Comercial — Seguimientos Specification

> New capability introduced by change `comercial-funnel`. Adds the append-only contact-touch log `SeguimientoComercial` over the existing `Cliente`, the source for the `sin-seguimiento`/`tarea-vencida`/`cita-hoy` alerts and the `diasSinSeguimiento` computed field. `Cliente` is reused as the anchor and is NOT redefined.

## ADDED Requirements

### Requirement: SeguimientoComercial as an append-only contact-touch log
The system MUST store contact touches in `seguimientos_comerciales`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like `UsuarioRolEmpresa`), `clienteId` FK→`Cliente` (Cascade), `fechaContacto` (default now), `tipoGestion` `TipoGestionComercial`, optional `motivoContacto` (Text), optional `resultado` (Text), optional `proximaTarea`, optional `fechaProximaTarea`, `estadoSeguimiento` `EstadoSeguimiento` (default `PENDIENTE`), optional `observaciones` (Text), optional `registradoPorId` FK→`Usuario` (SetNull), `createdAt`, `updatedAt`. It MUST index `@@index([clienteId, fechaContacto])`, `@@index([empresaId, fechaProximaTarea])`, `@@index([empresaId, estadoSeguimiento])`. Only `Cliente` cascades in (denormalized `empresaId` has NO FK; an Empresa delete reaches rows via the Cliente cascade); `registradoPorId` MUST be `SetNull`.

#### Scenario: Log a contact touch
- GIVEN a user holding `comercial.seguimiento.crear` in despacho A
- WHEN they POST a seguimiento for a `Cliente` of A with `tipoGestion = LLAMADA`
- THEN it is created with `empresaId` of A (from token), the given `clienteId`, `estadoSeguimiento = PENDIENTE`, and `fechaContacto` defaulted to now

#### Scenario: Cross-tenant isolation
- GIVEN a seguimiento of despacho B
- WHEN a user of despacho A lists seguimientos
- THEN despacho B's seguimiento is NOT returned (hard WHERE `{ empresaId }`)

#### Scenario: Deleting the registrador nulls the link
- GIVEN a seguimiento whose `registradoPorId` points at a `Usuario`
- WHEN that `Usuario` is deleted
- THEN the seguimiento survives with `registradoPorId = null`

### Requirement: Enums TipoGestionComercial and EstadoSeguimiento
The system MUST define `TipoGestionComercial { LLAMADA, WHATSAPP, REUNION, VIDEOLLAMADA, CORREO, OTRO }` and `EstadoSeguimiento { PENDIENTE, EN_GESTION, CERRADO }`. These MUST be additive and MUST NOT modify existing enums.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoGestionComercial` and `EstadoSeguimiento` exist with the listed members AND no existing enum is changed

### Requirement: Tenancy and FK validation mirror the clientes router
Every seguimiento endpoint MUST take `empresaId` from the authenticated request (never the body), filter every query by a hard `WHERE { empresaId }`, and run `assertSameEmpresa` so that `clienteId` and `registradoPorId` belong to the SAME empresa. It MUST be gated by `requireAuth` + a CONCRETE `requirePermiso` clave per action (`comercial.seguimiento.ver` on reads, `comercial.seguimiento.crear` on create, `comercial.seguimiento.editar` on update/close). `requirePermiso` does NOT support wildcards (exact-clave lookup → 500 on a literal `*`); `comercial.seguimiento.*` here is shorthand for that concrete set.

#### Scenario: empresaId comes only from the token
- GIVEN an authenticated user of despacho A
- WHEN they POST a seguimiento with `empresaId = B` in the body
- THEN the body `empresaId` is ignored and the seguimiento is created in despacho A

#### Scenario: Cross-empresa cliente is rejected
- GIVEN a user of despacho A
- WHEN they POST a seguimiento whose `clienteId` belongs to despacho B
- THEN the write is rejected (cross-tenant reference) and no row is created