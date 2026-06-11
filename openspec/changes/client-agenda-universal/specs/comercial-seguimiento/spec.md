# Comercial — Seguimientos · delta (agenda universal)

> Change `client-agenda-universal`. The agenda (built on `SeguimientoComercial`) becomes a baseline
> feature for every firm user, the cliente link becomes optional, and agenda items expose their creator.

## MODIFIED Requirements

### Requirement: clienteId is optional on SeguimientoComercial
`SeguimientoComercial.clienteId` MUST be optional (`String?`) with relation `cliente Cliente?`
(`onDelete: SetNull`). A seguimiento/agenda activity MAY exist with NO cliente. When `clienteId` is
provided on create, the system MUST still validate same-empresa (`assertCliente`); when absent, it
MUST skip that check and create the row with `clienteId = null`.

#### Scenario: Agenda activity without a cliente
- GIVEN a firm user creating an agenda activity with no `clienteId`
- WHEN they POST `/comercial/seguimientos` with `tipoGestion`, `titulo`, `fechaProximaTarea`
- THEN the row is created (`clienteId = null`, `registradoPorId` = the user) with status 201

#### Scenario: cliente still validated when provided
- GIVEN a POST with a `clienteId` of another empresa
- WHEN it is processed
- THEN it is rejected 400 (same-empresa `assertCliente` still applies)

## ADDED Requirements

### Requirement: Agenda/seguimiento endpoints are baseline (any firm user)
The endpoints `GET/POST/PATCH /comercial/seguimientos`, `GET /comercial/agenda`, and
`POST /comercial/seguimientos/:id/{completar,cancelar,reabrir}` MUST be gated by `requireAuth` ONLY
(no `requirePermiso`, no module gate), so ANY authenticated user of a despacho — including a regular
`USUARIO` with no `RolEmpresa` and a despacho that has NOT contracted the comercial module — can use
the agenda. Tenant scoping MUST remain enforced (`WHERE { empresaId }` from the token) and the owner
logic MUST remain (`comercialId` defaults to the caller; only `esAdminEmpresa` may set another). The
rest of the comercial module (clientes/fases/cotización/alertas) KEEPS its `requirePermiso` gate.

#### Scenario: Role-less user without the comercial module can use the agenda
- GIVEN a despacho whose comercial module is NOT contracted and a user with no `RolEmpresa` and `esAdminEmpresa = false`
- WHEN they GET `/comercial/seguimientos` (or `/comercial/agenda`)
- THEN they get 200 (not 403 "Módulo no contratado", not 403 "No autorizado")

#### Scenario: Module gate still applies elsewhere
- GIVEN the comercial module is NOT contracted
- WHEN any user GETs `/comercial/alertas`
- THEN it is rejected 403 "Módulo no contratado"

### Requirement: Agenda items expose their creator (name + roles)
`GET /comercial/agenda` MUST attach to each item (and each `vencida`) a `registradoPor` object
`{ nombre, roles: string[], esAdminEmpresa }` resolved from the scalar `registradoPorId` (NO FK) in a
single batched query scoped by `empresaId`, or `null` when there is no creator. This powers the firm
admin view showing who created each activity and their role.

#### Scenario: Admin sees creator and role per item
- GIVEN agenda items created by a user named "Ana" with role JURIDICO
- WHEN the firm admin GETs `/comercial/agenda`
- THEN each of Ana's items carries `registradoPor = { nombre: "Ana", roles: ["JURIDICO"], esAdminEmpresa: false }`

#### Scenario: Creator with no role
- GIVEN an item created by a role-less, non-admin USUARIO
- WHEN the agenda is read
- THEN `registradoPor.roles` is `[]` and `esAdminEmpresa` is `false` (UI renders "Usuario")
