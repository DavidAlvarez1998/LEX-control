# Spec: Empresa Team Management (Client Portal)

> Q1 = ALLOW esAdminEmpresa on create; Q2 = ALL (list + create + activate/deactivate + resend).

## ADDED Requirements

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
`GET /mi-empresa/usuarios` MUST return the users of the requester's own empresa, each with a
derived `estado` (`ACTIVO` | `PENDIENTE` | `INACTIVO`), and MUST NOT expose passwords or the
activation-token hash.

#### Scenario: Admin lists only their own company
- GIVEN an empresa admin of company A
- WHEN they GET `/mi-empresa/usuarios`
- THEN the response contains only company A's users
- AND no user object contains `password` or `activationToken`
- AND each user has an `estado` of ACTIVO, PENDIENTE, or INACTIVO

### Requirement: Create Company Member
`POST /mi-empresa/usuarios` MUST create a `Usuario` in the requester's own empresa from
`{ nombre, email, esAdminEmpresa? }`, forcing `rol = USUARIO` and `empresaId = req.empresaId`,
and MUST return the created user plus an `activationUrl` pointing to the client portal. A new
member MUST NOT be able to log in until they set a password via the activation link.

#### Scenario: Valid creation
- GIVEN an empresa admin and a unique email
- WHEN they POST `{ nombre, email }`
- THEN the response status is 201
- AND the user is created with `rol = USUARIO` and `empresaId` equal to the admin's empresa
- AND the body includes an `activationUrl` for the client portal `/activar`

#### Scenario: Client cannot override rol or empresa
- GIVEN an empresa admin of company A
- WHEN they POST a body that also includes `rol = "ADMIN"` and `empresaId = "B"`
- THEN the created user still has `rol = USUARIO` and `empresaId = A` (the body values are ignored)

#### Scenario: Missing required fields
- GIVEN an empresa admin
- WHEN they POST without `nombre` or with an invalid `email`
- THEN the response status is 400 and no user is created

#### Scenario: Duplicate email
- GIVEN an email already used by another user
- WHEN the empresa admin POSTs it
- THEN the response status is 409 and no user is created

#### Scenario: Grant company-admin on create
- GIVEN an empresa admin
- WHEN they POST `{ nombre, email, esAdminEmpresa: true }`
- THEN the created member has `esAdminEmpresa = true` (and still `rol = USUARIO`)

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
