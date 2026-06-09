# Empresa Team Management Specification

> New capability introduced by change `client-empresa-users` (archived 2026-06-05). An empresa admin
> (`USUARIO` + `esAdminEmpresa`) manages their own company's team from the client portal (:3001):
> list + create + activate/deactivate + resend activation link. Empresa is always resolved from the
> token (`req.empresaId`), never from the client. Multi-role assignment + seat reporting merged from
> `client-equipo-roles`; portal password-reset + in-app confirmations from `equipo-reset-ui-fixes`.

## Requirements

### Requirement: Empresa Admin Authorization
The team endpoints MUST be restricted to an authenticated `USUARIO` with `esAdminEmpresa = true`,
acting only on their own `Empresa` (resolved from the token, never from a client-supplied id).

#### Scenario: Non-admin USUARIO is rejected
- GIVEN an authenticated `USUARIO` with `esAdminEmpresa = false`
- WHEN they call any `/mi-empresa/usuarios` endpoint
- THEN the response status is 403

#### Scenario: Platform ADMIN does not use this surface
- GIVEN an authenticated platform `ADMIN`
- WHEN they call `/mi-empresa/usuarios`
- THEN they are rejected (no empresa) — platform admins use `/usuarios`

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

### Requirement: Activate / Deactivate a Member
`PATCH /mi-empresa/usuarios/:id` MUST toggle a teammate's `activo` flag, acting ONLY on a user of
the requester's own empresa, and MUST revoke that user's live sessions when deactivating (bumping
`tokenVersion`). An empresa admin MUST NOT deactivate their own account.

#### Scenario: Deactivate revokes sessions
- GIVEN an empresa admin and an active teammate of the same empresa
- WHEN they PATCH `{ activo: false }` for that teammate
- THEN the teammate is deactivated AND their `tokenVersion` is incremented (live sessions revoked)

#### Scenario: Cannot deactivate self
- GIVEN an empresa admin
- WHEN they PATCH `{ activo: false }` on their own id
- THEN the response status is 400 and no change is made

#### Scenario: Cannot target another company's user
- GIVEN an empresa admin of company A and a user of company B
- WHEN they PATCH that user's id
- THEN the response status is 404 (scoped by `empresaId`; existence not revealed)

### Requirement: Resend Activation Link
`POST /mi-empresa/usuarios/:id/activation` MUST regenerate a teammate's activation token (returning
a fresh client-portal `activationUrl`) and MUST revoke the teammate's live sessions, acting ONLY on
a user of the requester's own empresa.

#### Scenario: Regenerate link for a teammate
- GIVEN an empresa admin and a teammate of the same empresa
- WHEN they POST `/mi-empresa/usuarios/:id/activation`
- THEN the response includes a fresh `activationUrl` for the client portal `/activar`
- AND the teammate's `tokenVersion` is incremented (previous link and session no longer valid)

#### Scenario: Cannot resend for another company's user
- GIVEN an empresa admin of company A and a user of company B
- WHEN they POST `/mi-empresa/usuarios/:id/activation` for that user
- THEN the response status is 404

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

### Requirement: Reset Member Password from the Portal
The Equipo screen MUST let an empresa admin reset the password of an **already-activated**
teammate by regenerating their activation link (reusing `POST /mi-empresa/usuarios/:id/activation`),
in addition to resending the link to a `PENDIENTE` member. The admin MUST NOT be offered this
action on their own account.

#### Scenario: Reset shown for an activated teammate
- GIVEN an empresa admin viewing the Equipo list
- AND a teammate whose `estado` is ACTIVO or INACTIVO (already set a password)
- WHEN the admin opens the row actions
- THEN a "Restablecer contraseña" action is available
- AND confirming it regenerates the activation link and revokes the teammate's live session
- AND the fresh link is shown for the admin to share manually

#### Scenario: Pending member still shows resend, not reset
- GIVEN a teammate whose `estado` is PENDIENTE (never activated)
- WHEN the admin opens the row actions
- THEN the action shown is "Reenviar enlace" (not "Restablecer contraseña")

#### Scenario: No reset on self
- GIVEN an empresa admin viewing their own row in the list
- WHEN they open the row actions
- THEN no "Restablecer contraseña" action is offered for their own account

### Requirement: In-App Confirmation Modals
Destructive or session-revoking actions on the Equipo screen (deactivate, resend link, reset
password) MUST be confirmed with the portal's in-app `ConfirmDialog` modal rather than the
browser's native `window.confirm`. Activating a member (non-destructive) MAY proceed without a
confirmation.

#### Scenario: Deactivate asks via modal
- GIVEN an empresa admin
- WHEN they click "Desactivar" on a teammate
- THEN an in-app modal asks for confirmation (styled as destructive)
- AND the action runs only after confirming
