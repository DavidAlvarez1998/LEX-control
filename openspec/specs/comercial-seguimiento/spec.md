# Comercial — Seguimientos Specification

> New capability introduced by change `comercial-funnel`. Adds the append-only contact-touch log `SeguimientoComercial` over the existing `Cliente`, the source for the `sin-seguimiento`/`tarea-vencida`/`cita-hoy` alerts and the `diasSinSeguimiento` computed field. `Cliente` is reused as the anchor and is NOT redefined.

## ADDED Requirements

### Requirement: SeguimientoComercial as an append-only contact-touch log
> MODIFIED by change `client-agenda-universal` — `clienteId` is now optional (`String?`, `SetNull`); an agenda/seguimiento activity MAY exist with no cliente.

The system MUST store contact touches in `seguimientos_comerciales`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like `UsuarioRolEmpresa`), optional `clienteId` FK→`Cliente` (`SetNull`), `fechaContacto` (default now), `tipoGestion` `TipoGestionComercial`, optional `motivoContacto` (Text), optional `resultado` (Text), optional `proximaTarea`, optional `fechaProximaTarea`, `estadoSeguimiento` `EstadoSeguimiento` (default `PENDIENTE`), optional `observaciones` (Text), optional `registradoPorId` FK→`Usuario` (SetNull), `createdAt`, `updatedAt`. It MUST index `@@index([clienteId, fechaContacto])`, `@@index([empresaId, fechaProximaTarea])`, `@@index([empresaId, estadoSeguimiento])`. `clienteId` and `registradoPorId` MUST be `SetNull`; tenant containment rests on the denormalized `empresaId` (no FK) which every query hard-filters. When `clienteId` is provided on create the system MUST validate same-empresa (`assertCliente`); when absent it MUST skip that check and store `clienteId = null`.

#### Scenario: Log a contact touch
- GIVEN a user holding `comercial.seguimiento.crear` in despacho A
- WHEN they POST a seguimiento for a `Cliente` of A with `tipoGestion = LLAMADA`
- THEN it is created with `empresaId` of A (from token), the given `clienteId`, `estadoSeguimiento = PENDIENTE`, and `fechaContacto` defaulted to now

#### Scenario: Agenda activity without a cliente
- GIVEN a firm user creating an agenda activity with no `clienteId`
- WHEN they POST `/comercial/seguimientos` with `tipoGestion`, `titulo`, `fechaProximaTarea`
- THEN the row is created (`clienteId = null`, `registradoPorId` = the user) with status 201

#### Scenario: cliente still validated when provided
- GIVEN a POST with a `clienteId` of another empresa
- WHEN it is processed
- THEN it is rejected 400 (same-empresa `assertCliente` still applies)

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

### Requirement: Typed disposition closes the contact loop
> MODIFIED by change `comercial-seguimiento-accionable`.

The system MUST define the additive enum `DisposicionGestion { CONTACTADO, NO_CONTESTA, INTERESADO, NO_VIABLE, OTRO }` and a nullable column `disposicion` on `seguimientos_comerciales` (additive, applied with `db push`, no backfill, no existing enum changed). The seguimiento create and update endpoints MUST accept and persist `disposicion` so the contact loop is closed with a measurable outcome (not free text only). The disposition feeds the pipeline's `ultimaDisposicion` frío/caliente signal. `NO_VIABLE` is the typed shortcut a UI uses to offer "mark fase PERDIDO" (which reuses `POST /clientes/:id/fase`, no new endpoint).

#### Scenario: Disposition persists on create
- GIVEN a user holding `comercial.seguimiento.crear`
- WHEN they POST a seguimiento with `disposicion = INTERESADO`
- THEN it is created with `disposicion = INTERESADO` and the value is returned

#### Scenario: Disposition is optional and additive
- GIVEN the pushed schema
- WHEN a seguimiento is created without `disposicion`
- THEN it is stored with `disposicion = null` AND no existing enum was modified

#### Scenario: Disposition surfaces as the pipeline signal
- GIVEN a cliente whose most recent disposed seguimiento is `INTERESADO`
- WHEN `GET /comercial/pipeline` is read
- THEN that cliente's `ultimaDisposicion = INTERESADO`

### Requirement: Agenda/seguimiento endpoints are baseline (any firm user)
> ADDED by change `client-agenda-universal`.

The endpoints `GET/POST/PATCH /comercial/seguimientos`, `GET /comercial/agenda`, and `POST /comercial/seguimientos/:id/{completar,cancelar,reabrir}` MUST be gated by `requireAuth` ONLY (no `requirePermiso`, no module gate), so ANY authenticated user of a despacho — including a regular `USUARIO` with no `RolEmpresa` and a despacho that has NOT contracted the comercial module — can use the agenda. Tenant scoping MUST remain enforced (`WHERE { empresaId }` from the token) and the owner logic MUST remain (`comercialId` defaults to the caller; only `esAdminEmpresa` may set another). The rest of the comercial module (clientes/fases/cotización/alertas) KEEPS its `requirePermiso` gate.

#### Scenario: Role-less user without the comercial module can use the agenda
- GIVEN a despacho whose comercial module is NOT contracted and a user with no `RolEmpresa` and `esAdminEmpresa = false`
- WHEN they GET `/comercial/seguimientos` (or `/comercial/agenda`)
- THEN they get 200 (not 403 "Módulo no contratado", not 403 "No autorizado")

#### Scenario: Module gate still applies elsewhere
- GIVEN the comercial module is NOT contracted
- WHEN any user GETs `/comercial/alertas`
- THEN it is rejected 403 "Módulo no contratado"

### Requirement: Agenda items expose their creator (name + roles)
> ADDED by change `client-agenda-universal`.

`GET /comercial/agenda` MUST attach to each item (and each `vencida`) a `registradoPor` object `{ nombre, roles: string[], esAdminEmpresa }` resolved from the scalar `registradoPorId` (NO FK) in a single batched query scoped by `empresaId`, or `null` when there is no creator. This powers the firm admin view showing who created each activity and their role.

#### Scenario: Admin sees creator and role per item
- GIVEN agenda items created by a user named "Ana" with role JURIDICO
- WHEN the firm admin GETs `/comercial/agenda`
- THEN each of Ana's items carries `registradoPor = { nombre: "Ana", roles: ["JURIDICO"], esAdminEmpresa: false }`

#### Scenario: Creator with no role
- GIVEN an item created by a role-less, non-admin USUARIO
- WHEN the agenda is read
- THEN `registradoPor.roles` is `[]` and `esAdminEmpresa` is `false` (UI renders "Usuario")

### Requirement: SeguimientoComercial carries agenda fields and an activity lifecycle
> ADDED by change `comercial-rol-portal`.

`SeguimientoComercial` MUST gain agenda columns (additive, `db push`, no existing column changed): `comercialId` (scalar, NO FK — the OWNER of the activity; backfilled from `registradoPorId`), `titulo`, `completada` `Boolean @default(false)`, `fechaCompletada?`, `canceladaEn?`, `motivoCancelacion?` (Text), and the index `@@index([empresaId, comercialId, fechaProximaTarea])`. The owner defaults to the caller; only an `esAdminEmpresa` caller may act on another `comercialId`.

#### Scenario: Owner defaults to the caller
- GIVEN a non-admin user creates an agenda activity
- WHEN it is stored
- THEN `comercialId` = that user (they cannot set another owner)

### Requirement: GET /comercial/agenda is a month-scoped, owner-aware calendar feed
> ADDED by change `comercial-rol-portal`.

`GET /comercial/agenda` MUST return the activities whose `fechaProximaTarea` falls in the requested month window plus, optionally, the overdue `vencidas` (`fechaProximaTarea < desde`, still pending). It MUST honor `incluirCompletadas` (default: only pending) and the owner rule: a non-admin caller is scoped to their own `comercialId`; an `esAdminEmpresa` caller may pass `comercialId` to view a member's agenda (or all). Tenant scope (`WHERE { empresaId }`) always applies. Each item MUST carry its `registradoPor` (resolved in batch from the scalar `registradoPorId`, scoped by empresa).

#### Scenario: Comercial sees only their own slots
- GIVEN agenda activities of U1 and U2 in despacho A
- WHEN U1 (non-admin) GETs `/comercial/agenda` for a month
- THEN only U1's activities (and U1's vencidas) are returned

#### Scenario: Admin can view a member's agenda
- GIVEN a firm ADMINISTRADOR
- WHEN they GET `/comercial/agenda?comercialId=U1`
- THEN U1's activities are returned

### Requirement: Activities can be completed, cancelled, and reopened
> ADDED by change `comercial-rol-portal`.

The system MUST expose `POST /comercial/seguimientos/:id/{completar,cancelar,reabrir}` (each `requireAuth`, tenant-scoped): `completar` sets `completada = true` + `fechaCompletada` (optionally a `resultado`); `cancelar` sets `canceladaEn` + `motivoCancelacion` (the activity stays visible, NOT deleted); `reabrir` clears the completion/cancellation marks. A cancelled or completed activity is distinguishable from a deleted one (it is never hard-deleted).

#### Scenario: Cancel keeps the row visible
- GIVEN a pending agenda activity
- WHEN it is cancelled with a motivo
- THEN `canceladaEn`/`motivoCancelacion` are set, the row persists and is not returned among pending slots

#### Scenario: Reopen restores a completed activity
- GIVEN a completed activity
- WHEN `reabrir` is called
- THEN `completada = false` and `fechaCompletada` is cleared