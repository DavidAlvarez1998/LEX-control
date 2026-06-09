# Spec Delta: Authentication — Empresa-Active Gating

## ADDED Requirements

### Requirement: Inactive Empresa Blocks Its Users
A user who belongs to an `Empresa` with `activo = false` MUST be denied authentication and request
authorization, with the same generic `401` used for other invalid-credential cases. Platform
`ADMIN` users (who have no empresa) MUST NOT be affected. Setting the empresa back to
`activo = true` MUST restore access with no further action.

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
