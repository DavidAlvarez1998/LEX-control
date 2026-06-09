# Authentication Specification (Delta)

> Delta for change `client-auth`. Modifies the `authentication` capability defined in `api-foundation`.

## MODIFIED Requirements

### Requirement: Login Issues JWT
The system MUST provide `POST /auth/login` that verifies credentials and returns a signed JWT on success. The JWT MUST have an **absolute lifetime of 8 hours** (`exp` = issued-at + 8h).

#### Scenario: Valid credentials
- GIVEN an active user with a known email and password
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 200
- AND the body contains a JWT whose claims include the user id, `rol`, and an `exp` 8 hours in the future
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

## ADDED Requirements

### Requirement: Role-Scoped Login
The login endpoint MUST support an optional `audience` (`ADMIN` | `CLIENTE`) and MUST reject, with `401`, a user whose `rol` does not match the requested audience. When `audience` is omitted, login behaves as before (any rol).

#### Scenario: Audience matches role
- GIVEN an active `CLIENTE` with correct credentials
- WHEN they POST to `/auth/login` with `audience = "CLIENTE"`
- THEN the response status is 200 and a token is returned

#### Scenario: Audience does not match role
- GIVEN an active `ADMIN` with correct credentials
- WHEN they POST to `/auth/login` with `audience = "CLIENTE"`
- THEN the response status is 401
- AND no token is returned
- AND the message does not reveal that the credentials were otherwise valid

#### Scenario: Audience omitted
- GIVEN an active user with correct credentials
- WHEN they POST to `/auth/login` without `audience`
- THEN the response status is 200 and a token is returned regardless of rol
