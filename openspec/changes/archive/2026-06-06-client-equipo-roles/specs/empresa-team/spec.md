# Empresa Team Management — Delta (client-equipo-roles)

> Extends `empresa-team` (from `client-empresa-users`). Lets the empresa admin assign one or more
> `RolEmpresa` to a teammate from the client portal, honoring per-plan seats. Builds on the seat
> gate and `esAdminEmpresa` mirror from `foundations-roles-plans-clientes`. No schema/RBAC change.

## MODIFIED Requirements

### Requirement: Create Company Member
`POST /mi-empresa/usuarios` MUST create a `Usuario` in the requester's own empresa from
`{ nombre, email, roles }`, where `roles` is a non-empty array of `RolEmpresa` values, forcing
`rol = USUARIO` and `empresaId = req.empresaId`. The creation and the assignment of ALL chosen roles
MUST happen in a single transaction that seat-checks each role; if any role has no available seat
(including a role with cap 0 because the plan does not contract it), the whole operation MUST roll
back and no user MUST be created. `esAdminEmpresa` MUST be set to `true` iff `roles` includes
`ADMINISTRADOR`. The response MUST include the created user (with its `roles`) plus an `activationUrl`
for the client portal. A new member MUST NOT be able to log in until they set a password via the
activation link.

#### Scenario: Valid creation with multiple roles
- GIVEN an empresa admin, a unique email, and seats available for both roles
- WHEN they POST `{ nombre, email, roles: ["JURIDICO", "COMERCIAL"] }`
- THEN the response status is 201
- AND the user is created with `rol = USUARIO`, `empresaId` of the admin, and holds both `JURIDICO` and `COMERCIAL`
- AND `esAdminEmpresa = false`
- AND the body includes an `activationUrl` for the client portal `/activar`

#### Scenario: ADMINISTRADOR role mirrors esAdminEmpresa
- GIVEN an empresa admin
- WHEN they POST `{ nombre, email, roles: ["ADMINISTRADOR"] }`
- THEN the created member has `esAdminEmpresa = true` and holds `ADMINISTRADOR`

#### Scenario: Role not contracted by the plan is rejected atomically
- GIVEN an empresa on the `independiente` plan (no `COMERCIAL` seat)
- WHEN the admin POSTs `{ nombre, email, roles: ["COMERCIAL"] }`
- THEN the response status is 409 (sin cupo)
- AND no user is created (no orphan)

#### Scenario: Empty roles rejected
- GIVEN an empresa admin
- WHEN they POST `{ nombre, email, roles: [] }` (or omit `roles`)
- THEN the response status is 400 and no user is created

#### Scenario: Client cannot override rol or empresa
- GIVEN an empresa admin of company A
- WHEN they POST a body that also includes `rol = "ADMIN"` and `empresaId = "B"`
- THEN the created user still has `rol = USUARIO` and `empresaId = A` (the body values are ignored)

#### Scenario: Duplicate email
- GIVEN an email already used by another user
- WHEN the empresa admin POSTs it
- THEN the response status is 409 and no user is created

### Requirement: List Company Team
`GET /mi-empresa/usuarios` MUST return the users of the requester's own empresa, each with a derived
`estado` (`ACTIVO` | `PENDIENTE` | `INACTIVO`) AND its assigned `roles` (array of `RolEmpresa`), and
MUST NOT expose passwords or the activation-token hash.

#### Scenario: Admin lists their own company with roles
- GIVEN an empresa admin of company A
- WHEN they GET `/mi-empresa/usuarios`
- THEN the response contains only company A's users
- AND each user has an `estado` and a `roles` array
- AND no user object contains `password` or `activationToken`

## ADDED Requirements

### Requirement: Reconcile a Member's Roles
`PATCH /mi-empresa/usuarios/:id` MUST accept an optional `roles` array (`RolEmpresa[]`, non-empty when
present) that reconciles the member's role set: roles not in the array are removed, roles newly
present are assigned, all within a single transaction acting ONLY on a user of the requester's own
empresa (404 otherwise). Each added role MUST pass the seat gate (409 naming the role if full, with
no partial change). `esAdminEmpresa` MUST be kept in sync with whether `ADMINISTRADOR` is in the final
set. The existing optional `activo` toggle MUST keep working. An empresa admin MUST NOT remove
`ADMINISTRADOR` from their own account.

#### Scenario: Add a role
- GIVEN a member holding `JURIDICO` and a free `COMERCIAL` seat
- WHEN the admin PATCHes `{ roles: ["JURIDICO", "COMERCIAL"] }`
- THEN the member now holds both roles

#### Scenario: Remove a role and sync esAdminEmpresa
- GIVEN a member holding `ADMINISTRADOR` and `JURIDICO`
- WHEN the admin PATCHes `{ roles: ["JURIDICO"] }`
- THEN `ADMINISTRADOR` is removed AND the member's `esAdminEmpresa` becomes `false`

#### Scenario: Cannot remove own ADMINISTRADOR
- GIVEN an empresa admin holding `ADMINISTRADOR`
- WHEN they PATCH their own id with a `roles` array that omits `ADMINISTRADOR`
- THEN the response status is 400 and no change is made

#### Scenario: Seat full on add is atomic
- GIVEN a member and a `CONTABLE` cap that is already full
- WHEN the admin PATCHes a `roles` array adding `CONTABLE`
- THEN the response status is 409 naming `CONTABLE`
- AND the member's role set is unchanged

#### Scenario: Cannot target another company's user
- GIVEN an empresa admin of company A and a user of company B
- WHEN they PATCH that user's `roles`
- THEN the response status is 404

### Requirement: Report Role Seats
`GET /mi-empresa/cupos` MUST return, for each `RolEmpresa`, the plan `cap` (`number` or `null` for
unlimited; `0` when the plan does not contract the role) and `usados` (count of active holders in the
requester's empresa), restricted to an empresa admin acting on their own empresa.

#### Scenario: Cupos reflect the plan
- GIVEN an empresa on a plan with `COMERCIAL` cap 1, currently unused
- WHEN the admin GETs `/mi-empresa/cupos`
- THEN the entry for `COMERCIAL` has `cap = 1` and `usados = 0`
- AND a role not in the plan has `cap = 0`
