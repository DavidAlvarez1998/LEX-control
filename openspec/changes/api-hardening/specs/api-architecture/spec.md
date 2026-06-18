# API Architecture Specification — delta (api-hardening)

## ADDED Requirements

### Requirement: Security baseline middleware
The HTTP app MUST apply a security baseline: security headers (`helmet`), a request body size
limit on JSON parsing, and rate limiting on the unauthenticated surfaces (`/auth/login` and
`/publico/*`) to deter brute-force and spam. Rate limiting MAY be disabled under `NODE_ENV=test`
so the test suite (which performs many logins) is not throttled.

#### Scenario: Security headers are present
- GIVEN any HTTP response from the API
- WHEN inspected
- THEN it carries the standard security headers set by helmet

#### Scenario: Login is rate-limited in non-test environments
- GIVEN repeated `POST /auth/login` from one client beyond the configured window (outside tests)
- WHEN the limit is exceeded
- THEN further attempts receive HTTP 429 until the window resets

### Requirement: Consecutive codes are race-safe
Generating a sequential per-empresa code (`generarCodigoInterno`, factura `numero`) MUST derive
the next value from the LAST existing code (ordered desc + parsed), not from a `count`, so two
concurrent creates do not produce the same code. The `@@unique` remains the final backstop.

#### Scenario: Concurrent creates do not collide on the code
- GIVEN two procesos created concurrently in the same empresa/year
- WHEN both generate `codigoInterno`
- THEN they derive distinct consecutive values (the unique index is not violated under normal load)
