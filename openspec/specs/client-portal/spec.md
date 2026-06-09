# Client Portal Specification

## Purpose
Define portal separation at login and scoped, ownership-safe access to a client's own
company data from the tenant portal.

## Requirements

### Requirement: Portal separation at login
`POST /auth/login` MUST accept an optional `audience` field (`ADMIN` or `USUARIO`). When
`audience` is present, the authenticated user's `rol` MUST equal it; otherwise the request
MUST be rejected. The rejection MUST be indistinguishable from invalid credentials (same
401 status and generic message). When `audience` is absent, login behavior is unchanged.

#### Scenario: Role matches the portal
- GIVEN active credentials for an `ADMIN`
- WHEN the client POSTs `{ email, password, audience: "ADMIN" }`
- THEN the response status is 200 and returns a token

#### Scenario: Role does not match the portal
- GIVEN active credentials for an `ADMIN`
- WHEN the client POSTs `{ email, password, audience: "USUARIO" }`
- THEN the response status is 401

#### Scenario: No audience supplied
- GIVEN active credentials
- WHEN the client POSTs `{ email, password }`
- THEN login succeeds on valid credentials regardless of role

### Requirement: Read own company
The system MUST expose `GET /mi-empresa`, restricted to `USUARIO`, returning the caller's
own `Empresa` together with its active contracted services. The company MUST be resolved
from the authenticated user's identity (token `sub`), never from a client-supplied id.

#### Scenario: Client reads its company
- GIVEN a valid `USUARIO` token whose user belongs to a company
- WHEN the client sends `GET /mi-empresa`
- THEN the response status is 200
- AND the body is that company with a `servicios` array of contracted services

#### Scenario: Non-client blocked
- GIVEN a valid `ADMIN` token
- WHEN it sends `GET /mi-empresa`
- THEN the response status is 403

#### Scenario: Unauthenticated
- GIVEN no token
- WHEN the client sends `GET /mi-empresa`
- THEN the response status is 401

#### Scenario: Client without a company
- GIVEN a valid `USUARIO` token whose user has no `empresaId`
- WHEN it sends `GET /mi-empresa`
- THEN the response status is 404

### Requirement: Session exposes the company-admin flag
The `user` object returned by `POST /auth/login` MUST include `esAdminEmpresa`, so the
portal can present the access level (Administrador vs Usuario) from the session without an
extra request. The portal MUST NOT show the raw `rol` value to end users.

#### Scenario: Login returns the flag for a company admin
- GIVEN active credentials for a `USUARIO` who administers their company
- WHEN they log in
- THEN the `user` in the response includes `esAdminEmpresa: true`
