# Client Portal Auth Specification

> New capability introduced by change `client-auth`. Covers login, session storage, route protection, and role gating in the **client app** (`lex-control-client`, :3001).

## ADDED Requirements

### Requirement: Client Login Page
The client app MUST provide a `/login` page where a `USUARIO` user authenticates with email and password against `POST /auth/login` (with `audience = "USUARIO"`).

#### Scenario: Successful client login
- GIVEN a USUARIO with a set password
- WHEN they submit valid credentials at `/login`
- THEN a session (token + user) is stored and they are redirected into the dashboard

#### Scenario: Wrong credentials
- GIVEN any input that the API rejects with 401
- WHEN the form is submitted
- THEN an inline error "Credenciales inválidas" is shown
- AND no session is stored

### Requirement: Role Gate (USUARIO only)
The client app MUST refuse to establish a session for a non-`USUARIO` user, even if the credentials are otherwise valid.

#### Scenario: Admin attempts client login
- GIVEN valid ADMIN credentials
- WHEN submitted at the client `/login`
- THEN login is rejected (API returns 401 for the USUARIO audience)
- AND no session is stored and no dashboard access is granted

### Requirement: Session Storage
The client app MUST persist the session (JWT + user) in `localStorage` under client-specific keys (`lex_client_token`, `lex_client_user`) and MUST send the JWT as `Authorization: Bearer` on every API request.

#### Scenario: Token attached to requests
- GIVEN a stored client session
- WHEN the app calls the API
- THEN the request carries `Authorization: Bearer <token>`

### Requirement: Route Protection
The client `(dashboard)` routes MUST be protected: without a valid (unexpired) session the user is redirected to `/login`, and protected content is not rendered before the check completes.

#### Scenario: Unauthenticated access
- GIVEN no stored session
- WHEN a `(dashboard)` route is opened
- THEN the user is redirected to `/login`

#### Scenario: API rejects an in-flight request
- GIVEN a stored session that the API rejects with 401
- WHEN any API call returns 401
- THEN the session is cleared and the user is sent to `/login` (unless already there)
