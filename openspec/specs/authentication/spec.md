# Authentication Specification

## Purpose
Define how users authenticate and how requests are authorized by role, over the existing `Usuario` model (`rol` = `ADMIN` | `USUARIO` | `COMERCIAL`).

> Consolidated source of truth. Base requirements originate in change `api-foundation`; the JWT lifetime, role-scoped login, and token-based `set-password` were merged from `client-auth`/`user-management`; server-side session revocation, account-state enforcement, and the token-version (`tv`) claim from `auth-session-revocation`; and empresa-active gating from `empresa-activo-login-block`.

## Requirements

### Requirement: Password Hashing
The system MUST store user passwords only as one-way hashes and MUST NOT store or log plaintext passwords.

#### Scenario: Password is hashed at creation
- GIVEN a new user is created with a plaintext password
- WHEN the record is persisted
- THEN the stored `password` is a bcrypt hash, not the plaintext

### Requirement: Login Issues JWT
The system MUST provide `POST /auth/login` that verifies credentials and returns a signed JWT on success. The JWT MUST have an **absolute lifetime of 8 hours** (`exp` = issued-at + 8h). Login MUST reject inactive users (`activo = false`) AND MUST reject users with a pending activation (`activationToken != null`) with the same generic 401. The issued JWT MUST include a token-version claim (`tv`) equal to the user's current `tokenVersion`.

#### Scenario: Valid credentials
- GIVEN an active user with a known email and password
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 200
- AND the body contains a JWT whose claims include the user id, `rol`, a `tv` equal to the user's current `tokenVersion`, and an `exp` 8 hours in the future
- AND the body contains the user `{ id, nombre, email, rol }`

#### Scenario: Invalid credentials
- GIVEN an email that does not exist OR a wrong password
- WHEN they POST to `/auth/login`
- THEN the response status is 401
- AND no token is returned
- AND the message does not reveal which field was wrong

#### Scenario: Inactive user
- GIVEN a user with `activo = false`
- WHEN they POST correct credentials
- THEN the response status is 401

#### Scenario: Pending user
- GIVEN a user with a pending activation (`activationToken != null`) and an otherwise-correct password
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 401
- AND no token is returned
- AND the message does not reveal that the credentials were otherwise valid

### Requirement: Role-Scoped Login
The login endpoint MUST support an optional `audience` (`ADMIN` | `USUARIO`) and MUST reject, with `401`, a user whose `rol` does not match the requested audience. When `audience` is omitted, login behaves as before (any rol).

#### Scenario: Audience matches role
- GIVEN an active `USUARIO` with correct credentials
- WHEN they POST to `/auth/login` with `audience = "USUARIO"`
- THEN the response status is 200 and a token is returned

#### Scenario: Audience does not match role
- GIVEN an active `ADMIN` with correct credentials
- WHEN they POST to `/auth/login` with `audience = "USUARIO"`
- THEN the response status is 401
- AND no token is returned
- AND the message does not reveal that the credentials were otherwise valid

#### Scenario: Audience omitted
- GIVEN an active user with correct credentials
- WHEN they POST to `/auth/login` without `audience`
- THEN the response status is 200 and a token is returned regardless of rol

### Requirement: Authentication Middleware
The system MUST protect non-public routes by requiring a valid JWT in the `Authorization: Bearer` header. In addition to verifying the JWT signature and expiry, the middleware MUST validate the token against current account state on every protected request. It MUST reject with 401 when the user no longer exists, is inactive (`activo = false`), has a pending activation (`activationToken != null`), or when the token's version claim (`tv`) does not match the user's current `tokenVersion`.

#### Scenario: Missing or invalid token
- GIVEN a protected route
- WHEN a request arrives without a valid Bearer token
- THEN the response status is 401

#### Scenario: Valid token
- GIVEN a protected route
- WHEN a request carries a valid, unexpired JWT whose `tv` matches the user's current `tokenVersion`, for an active non-pending user
- THEN the request proceeds and the authenticated user (id, rol) is available to handlers

#### Scenario: Stale token version
- GIVEN a protected route
- WHEN a request carries a valid, unexpired JWT whose `tv` is older than the user's current `tokenVersion`
- THEN the response status is 401

#### Scenario: User became inactive after token was issued
- GIVEN a user who was set to `activo = false` after their token was issued
- WHEN a request carries that user's still-unexpired JWT
- THEN the response status is 401

#### Scenario: User became pending after token was issued
- GIVEN a user who was put into a pending state (`activationToken != null`, e.g. via password reset) after their token was issued
- WHEN a request carries that user's still-unexpired JWT
- THEN the response status is 401

### Requirement: Role Authorization
The system MUST enforce role-based access so that routes can require a specific `rol`.

#### Scenario: Insufficient role
- GIVEN a route that requires `ADMIN`
- WHEN a `USUARIO` token calls it
- THEN the response status is 403

#### Scenario: Sufficient role
- GIVEN a route that requires `ADMIN`
- WHEN an `ADMIN` token calls it
- THEN the request is authorized and proceeds

### Requirement: Session Revocation on Credential Change
The system MUST invalidate all previously issued tokens for a user when that user's credentials or active state change. Specifically, resetting a user's password (issuing a new activation link), completing activation (`set-password`), and deactivating a user (`activo` true→false) MUST each increment the user's `tokenVersion` so that prior tokens are rejected on their next request.

#### Scenario: Password reset revokes existing sessions
- GIVEN an ADMIN resets a user's password, issuing a new activation link
- WHEN a request arrives bearing that user's pre-reset token
- THEN the response status is 401

#### Scenario: Completing set-password revokes existing sessions
- GIVEN a user completes `set-password` to activate their account
- WHEN a request arrives bearing any token issued before activation
- THEN the response status is 401

#### Scenario: Deactivation revokes existing sessions
- GIVEN an ADMIN deactivates a user (`activo` true→false)
- WHEN a request arrives bearing that user's existing token
- THEN the response status is 401

### Requirement: Account State Is Authoritative
The three derived states — ACTIVO (`activo = true`, no `activationToken`), PENDIENTE (`activationToken != null`), and INACTIVO (`activo = false`) — MUST govern authentication, not merely the UI. A user not in the ACTIVO state MUST NOT be able to obtain or use a session.

#### Scenario: PENDIENTE user cannot log in
- GIVEN a user in the PENDIENTE state (`activationToken != null`)
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 401

#### Scenario: INACTIVO user cannot log in
- GIVEN a user in the INACTIVO state (`activo = false`)
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 401

#### Scenario: ACTIVO user can log in
- GIVEN a user in the ACTIVO state (`activo = true`, no `activationToken`)
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 200 and a token is returned

### Requirement: Inactive Empresa Blocks Its Users
A user who belongs to an `Empresa` with `activo = false` MUST be denied authentication and request authorization, with the same generic `401` used for other invalid-credential cases. Platform `ADMIN` users (who have no empresa) MUST NOT be affected. Setting the empresa back to `activo = true` MUST restore access with no further action.

#### Scenario: Login blocked for a user of an inactive empresa
- GIVEN an active user with correct credentials whose `Empresa.activo = false`
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 401
- AND no token is returned
- AND the message does not reveal that the credentials were otherwise valid

#### Scenario: Platform ADMIN is unaffected
- GIVEN an active `ADMIN` (no empresa) with correct credentials
- WHEN they POST to `/auth/login`
- THEN the response status is 200 and a token is returned

#### Scenario: Live session revoked when empresa is deactivated
- GIVEN a user holding a valid, unexpired JWT
- AND their `Empresa` is then set to `activo = false`
- WHEN their token calls any protected route
- THEN the response status is 401

#### Scenario: Reactivation restores access
- GIVEN a user previously blocked because their `Empresa.activo = false`
- WHEN the empresa is set back to `activo = true`
- THEN the same user can log in (200) and their requests are authorized again
