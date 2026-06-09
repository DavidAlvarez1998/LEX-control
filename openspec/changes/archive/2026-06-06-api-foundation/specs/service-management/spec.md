# Service Management Specification

## Purpose
Define CRUD behavior for the `Servicio` catalog (the platform's service catalog), used as the first vertical slice to prove the API layering. Authorization follows the authentication capability.

## Requirements

### Requirement: List Services
The system MUST expose `GET /servicios` returning the service catalog to any authenticated user.

#### Scenario: Authenticated list
- GIVEN a valid token
- WHEN the client sends `GET /servicios`
- THEN the response status is 200
- AND the body is a JSON array of services

#### Scenario: Unauthenticated list
- GIVEN no valid token
- WHEN the client sends `GET /servicios`
- THEN the response status is 401

### Requirement: Get Service
The system MUST expose `GET /servicios/:id` returning a single service.

#### Scenario: Existing service
- GIVEN a service with a known id and a valid token
- WHEN the client requests it by id
- THEN the response status is 200 and returns that service

#### Scenario: Missing service
- GIVEN an id that does not exist
- WHEN the client requests it
- THEN the response status is 404

### Requirement: Service billing model
A `Servicio` carries a usage-based billing model in addition to its name. The catalog
fields are: `nombre` (unique), optional `descripcion`, `precioBase` (fixed reference
cost), `precioPorUnidad` (cost per unit above the included allowance), `unidad` (what is
counted — e.g. "mensaje", "documento", "usuario"; `null` for fixed-cost services),
`incluidos` (units included in `precioBase`), and `activo`. Catalog prices are REFERENCE
values; the negotiated price per company lives on `EmpresaServicio`.

#### Scenario: Service exposes billing fields
- GIVEN a service in the catalog
- WHEN it is listed or fetched
- THEN it includes `precioBase`, `precioPorUnidad`, `unidad`, and `incluidos`

### Requirement: Create Service
The system MUST expose `POST /servicios` restricted to `ADMIN`, validating `nombre` and
`precioBase`. `precioPorUnidad`, `unidad`, `incluidos`, and `activo` are optional.

#### Scenario: Admin creates valid service
- GIVEN an `ADMIN` token and a body with valid `nombre` and `precioBase`
- WHEN the client POSTs it
- THEN the response status is 201 and returns the created service with an id

#### Scenario: Non-admin blocked
- GIVEN a `USUARIO` token
- WHEN the client POSTs a service
- THEN the response status is 403

#### Scenario: Invalid body
- GIVEN an `ADMIN` token and a body missing `precioBase`
- WHEN the client POSTs it
- THEN the response status is 400

### Requirement: Update Service
The system MUST expose `PUT /servicios/:id` (or PATCH) restricted to `ADMIN`.

#### Scenario: Admin updates service
- GIVEN an `ADMIN` token and an existing service
- WHEN the client updates an allowed field
- THEN the response status is 200 and returns the updated service

#### Scenario: Update missing service
- GIVEN an id that does not exist
- WHEN an `ADMIN` updates it
- THEN the response status is 404

### Requirement: Delete Service
The system MUST expose `DELETE /servicios/:id` restricted to `ADMIN`.

#### Scenario: Admin deletes service
- GIVEN an `ADMIN` token and an existing service
- WHEN the client deletes it
- THEN the response status is 204

#### Scenario: Non-admin blocked from delete
- GIVEN a `USUARIO` token
- WHEN the client deletes a service
- THEN the response status is 403
