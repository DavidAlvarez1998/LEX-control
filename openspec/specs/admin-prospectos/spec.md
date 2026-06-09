# Admin — Prospectos (sales pipeline) Specification

> New capability introduced by change `admin-comercial-ventas`. The platform's own lead pipeline:
> LEX Control staff capture prospect companies and sell them a Plan. Platform-level data (no
> `empresaId` tenancy); scoped by the assigned COMERCIAL. Introduces the `COMERCIAL` platform role.

## ADDED Requirements

### Requirement: COMERCIAL platform role
The system MUST add `COMERCIAL` to the `Rol` enum. A COMERCIAL is platform staff (`empresaId = null`)
who sells Planes. `Usuario` MUST gain an optional `porcentajeComision` `Decimal(5,2)` used as that
person's default commission rate. The addition MUST be additive and MUST NOT change existing `Rol`
values or other models beyond this column.

#### Scenario: Create a COMERCIAL user
- GIVEN an ADMIN on the Usuarios screen
- WHEN they create a user with `rol = COMERCIAL` and `porcentajeComision = 10`
- THEN the user is stored as platform staff (`empresaId = null`) with that rate

### Requirement: Prospecto entity with entry channel and funnel state
The system MUST store prospects in `prospectos`: `id` (cuid), `nombreEmpresa`, `nombreContacto`,
optional `email`/`telefono`/`cargo`, `canalEntrada` `CanalEntrada` (default `DIRECTO`), `estado`
`EstadoProspecto` (default `NUEVO`), optional scalar `planInteresId` and `comercialId` (no FK,
app-validated), sale-snapshot fields (`planVendidoId`, `precioVenta` `Decimal(10,2)`, `fechaCierre`,
`empresaId` unique FK→`Empresa` `SetNull`), optional `motivoPerdida`/`notas`, `createdAt`,
`updatedAt`. Enums: `CanalEntrada { WEB, WHATSAPP, DIRECTO, REFERIDO, LLAMADA, REDES_SOCIALES, OTRO }`
and `EstadoProspecto { NUEVO, CONTACTADO, COTIZADO, NEGOCIACION, GANADO, PERDIDO }`.

#### Scenario: Capture a lead with its channel
- GIVEN a COMERCIAL
- WHEN they POST a prospecto with `canalEntrada = WHATSAPP` and a `planInteresId`
- THEN it is created with `estado = NUEVO`, `comercialId = ` the creator, and that channel

#### Scenario: Channel and plan-of-interest are validated
- WHEN a prospecto is created with a `planInteresId` that is not an existing Plan
- THEN the API responds 400 and does not create the prospecto

### Requirement: Per-salesperson visibility
A COMERCIAL MUST only list/read/edit prospectos where `comercialId` equals their own user id; the API
MUST hard-scope reads with `where: { comercialId }` and respond 404 for writes to others'. ADMIN MUST
see all prospectos, MAY filter by `comercialId`/`estado`/`canalEntrada`, and is the only role that MAY
set or change `comercialId` (assignment/reassignment).

#### Scenario: COMERCIAL cannot see another's prospecto
- GIVEN prospecto P assigned to comercial B
- WHEN comercial A lists or fetches prospectos
- THEN P is not returned to A (and `GET /prospectos/P` → 404 for A)

#### Scenario: Only ADMIN assigns
- GIVEN a COMERCIAL editing their prospecto
- WHEN they try to PATCH `comercialId` to another user
- THEN the change is rejected (the field is ignored/forbidden for COMERCIAL)

### Requirement: Advancing the funnel
The system MUST allow moving a prospecto between non-terminal estados (`NUEVO`/`CONTACTADO`/
`COTIZADO`/`NEGOCIACION`) via PATCH. `GANADO` MUST be reachable only through the win action and
`PERDIDO` only through the lose action.

#### Scenario: Advance to NEGOCIACION
- WHEN a comercial PATCHes their prospecto `estado = NEGOCIACION`
- THEN it is updated

#### Scenario: Cannot jump straight to GANADO via PATCH
- WHEN a PATCH sets `estado = GANADO` directly
- THEN it is rejected (use `POST /prospectos/:id/ganar`)

### Requirement: Win converts to Empresa + Suscripcion in one transaction
`POST /prospectos/:id/ganar` MUST, atomically: create an `Empresa` from the prospecto data, create a
`Suscripcion` for the chosen plan (default `planInteresId`), set the prospecto to `GANADO` with the
sale snapshot (`planVendidoId`, `precioVenta` defaulting to the plan's `precioMensual`, `fechaCierre`,
`empresaId`), and generate the `Comision`. It MUST require an assigned `comercialId`. A prospecto
already `GANADO` MUST respond 409.

#### Scenario: Win creates firm, subscription and commission
- GIVEN a prospecto with an assigned comercial and a plan of interest
- WHEN ADMIN/COMERCIAL POSTs `/prospectos/:id/ganar` with `precioVenta = 100000`
- THEN an Empresa and its Suscripcion (that plan) exist, the prospecto is GANADO linked to that
  Empresa, and one Comision (PENDIENTE) is created for the comercial

#### Scenario: Double win is blocked
- GIVEN a prospecto already GANADO
- WHEN `/prospectos/:id/ganar` is called again
- THEN the API responds 409 and creates nothing

### Requirement: Losing a prospecto
`POST /prospectos/:id/perder` with `motivoPerdida` MUST set `estado = PERDIDO` and store the reason.

#### Scenario: Mark lost with reason
- WHEN a comercial posts `/prospectos/:id/perder { motivoPerdida: "Precio" }`
- THEN the prospecto is PERDIDO with that reason
