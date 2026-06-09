# Authentication Specification

## Purpose
Define how users authenticate and how requests are authorized by role, over the existing `Usuario` model (`rol` = `ADMIN` | `USUARIO`).

## Requirements

### Requirement: Password Hashing
The system MUST store user passwords only as one-way hashes and MUST NOT store or log plaintext passwords.

#### Scenario: Password is hashed at creation
- GIVEN a new user is created with a plaintext password
- WHEN the record is persisted
- THEN the stored `password` is a bcrypt hash, not the plaintext

### Requirement: Login Issues JWT
The system MUST provide `POST /auth/login` that verifies credentials and returns a signed JWT on success.

#### Scenario: Valid credentials
- GIVEN an active user with a known email and password
- WHEN they POST correct credentials to `/auth/login`
- THEN the response status is 200
- AND the body contains a JWT whose claims include the user id and `rol`

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

### Requirement: Authentication Middleware
The system MUST protect non-public routes by requiring a valid JWT in the `Authorization: Bearer` header.

#### Scenario: Missing or invalid token
- GIVEN a protected route
- WHEN a request arrives without a valid Bearer token
- THEN the response status is 401

#### Scenario: Valid token
- GIVEN a protected route
- WHEN a request carries a valid, unexpired JWT
- THEN the request proceeds and the authenticated user (id, rol) is available to handlers

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
