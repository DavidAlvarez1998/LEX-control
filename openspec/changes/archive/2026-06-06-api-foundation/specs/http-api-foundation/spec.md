# HTTP API Foundation Specification

## Purpose
Define the baseline behavior of the Express HTTP server in `lex-control-api`: bootstrap, configuration, health, CORS, and uniform error handling that all routes rely on.

## Requirements

### Requirement: Server Bootstrap
The system MUST expose an HTTP server that starts from a single entry point, listens on a configurable port, and parses JSON request bodies.

#### Scenario: Server starts on configured port
- GIVEN `PORT=4000` is set in the environment
- WHEN the server is started
- THEN it listens on port 4000
- AND logs a startup message

#### Scenario: Missing required config aborts startup
- GIVEN `JWT_SECRET` is not set
- WHEN the server starts
- THEN it exits with a non-zero code and a clear error message
- AND does not begin listening

### Requirement: Health Check
The system MUST provide a `GET /health` endpoint that requires no authentication and reports liveness.

#### Scenario: Health returns OK
- GIVEN the server is running
- WHEN a client sends `GET /health`
- THEN the response status is 200
- AND the body is JSON `{ "status": "ok" }`

### Requirement: CORS
The system MUST allow cross-origin requests from the configured frontend origins and MUST reject others.

#### Scenario: Allowed origin
- GIVEN `CORS_ORIGINS` includes `http://localhost:3000` and `http://localhost:3001`
- WHEN the admin frontend (`:3000`) calls the API
- THEN the response includes the matching `Access-Control-Allow-Origin` header
- AND credentials are allowed

#### Scenario: Disallowed origin
- GIVEN an origin not in `CORS_ORIGINS`
- WHEN it calls the API
- THEN the browser is not granted CORS access for that origin

### Requirement: Uniform Error Handling
The system MUST return errors in a consistent JSON shape and MUST NOT leak stack traces in production.

#### Scenario: Unknown route
- GIVEN the server is running
- WHEN a client requests an undefined route
- THEN the response status is 404
- AND the body is JSON `{ "error": { "message": "Not Found" } }`

#### Scenario: Validation failure
- GIVEN a request body that fails validation
- WHEN it reaches a validated route
- THEN the response status is 400
- AND the body lists the validation issues under `error`

#### Scenario: Unexpected error
- GIVEN a handler throws an unexpected error
- WHEN the error reaches the central handler
- THEN the response status is 500
- AND no stack trace is exposed when `NODE_ENV=production`
