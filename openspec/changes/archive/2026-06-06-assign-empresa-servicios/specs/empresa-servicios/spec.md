# Empresa Services Specification

## Purpose
Define how an ADMIN assigns services from the catalog to a company and sets the negotiated price
for that company, through the empresa create and edit endpoints. The negotiated price lives on
`EmpresaServicio`; catalog values on `Servicio` are reference defaults.

## Requirements

### Requirement: Assignment shape
An assignment item provided to the empresa endpoints carries `servicioId` (required) and the
optional per-company price fields `precioBase`, `precioPorUnidad`, `incluidos`, and `activo`.
Any omitted price field MUST default to the corresponding value on the catalog `Servicio`
(`activo` defaults to `true`). Each `servicioId` MUST be unique within the array.

#### Scenario: Defaults from catalog
- GIVEN a catalog service with `precioBase` 100, `precioPorUnidad` 5, `incluidos` 10
- WHEN an assignment provides only its `servicioId`
- THEN the stored `EmpresaServicio` has `precioBase` 100, `precioPorUnidad` 5, `incluidos` 10, `activo` true

#### Scenario: Per-company override
- GIVEN the same catalog service
- WHEN an assignment provides `precioBase` 80
- THEN the stored `EmpresaServicio` has `precioBase` 80 and the remaining fields defaulted from the catalog

#### Scenario: Duplicate service in payload
- GIVEN an `ADMIN` token
- WHEN the array contains the same `servicioId` twice
- THEN the response status is 400

#### Scenario: Unknown service id
- GIVEN an `ADMIN` token
- WHEN an assignment references a `servicioId` not in the catalog
- THEN the response status is 400 AND no empresa or assignment is created

### Requirement: Create empresa with assignments
`POST /empresas` (ADMIN-only) MUST accept an optional `servicios` array. When present, the
empresa and all its assignments MUST be created atomically; if any assignment is invalid, the
whole operation MUST fail with no partial write. The response MUST include the created empresa
with its `servicios`, each embedding the catalog `servicio`.

#### Scenario: Create with services
- GIVEN an `ADMIN` token and a body with a valid `nombre` and two valid assignments
- WHEN the client POSTs it
- THEN the response status is 201 AND the body includes the empresa with two `servicios`

#### Scenario: Create without services
- GIVEN an `ADMIN` token and a body with only `nombre`
- WHEN the client POSTs it
- THEN the response status is 201 AND the empresa has no assignments

#### Scenario: Atomic failure
- GIVEN an `ADMIN` token and a body with one valid and one unknown `servicioId`
- WHEN the client POSTs it
- THEN the response status is 400 AND the empresa is not created

### Requirement: Reconcile assignments on update
`PATCH /empresas/:id` (ADMIN-only) MUST accept an optional `servicios` array. When the field is
present it defines the company's complete set of assignments (replace-set): services in the array
MUST be created or updated, and existing assignments whose `servicioId` is absent from the array
MUST be removed — all within one transaction. When the field is absent, existing assignments MUST
be left untouched.

#### Scenario: Add and update
- GIVEN an empresa with service A assigned at `precioBase` 100
- WHEN the client PATCHes `servicios` = [A at `precioBase` 90, B at defaults]
- THEN A's `precioBase` becomes 90 AND B is created AND the response shows both

#### Scenario: Remove omitted
- GIVEN an empresa with services A and B assigned
- WHEN the client PATCHes `servicios` = [A]
- THEN B's assignment is removed AND only A remains

#### Scenario: Field absent leaves assignments
- GIVEN an empresa with services A and B assigned
- WHEN the client PATCHes only `nombre` (no `servicios` field)
- THEN A and B remain assigned unchanged

#### Scenario: Non-admin blocked
- GIVEN a non-ADMIN token
- WHEN the client PATCHes empresa `servicios`
- THEN the response status is 403

### Requirement: Read assignments
`GET /empresas/:id` (ADMIN-only) MUST return the empresa with its `servicios`, each embedding the
catalog `servicio`, so the admin form can pre-populate the services section when editing.

#### Scenario: Fetch for edit
- GIVEN an empresa with one assignment and an `ADMIN` token
- WHEN the client requests `GET /empresas/:id`
- THEN the response includes `servicios[0].servicio` with the catalog fields
