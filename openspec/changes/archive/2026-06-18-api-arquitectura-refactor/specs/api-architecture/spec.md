# API Architecture Specification — delta (api-arquitectura-refactor)

## ADDED Requirements

### Requirement: Layered module structure
Each feature module under `src/modules/<feature>/` MUST separate concerns across a router
(HTTP only), a service (business/use-cases), a repository (data access), and a DTO/mapper
(response shape). Dependencies MUST point inward only: the service MUST NOT import Express
(`req`/`res`); the repository MUST NOT contain business rules; the router MUST NOT call Prisma.

#### Scenario: Router contains no data access or business logic
- GIVEN any `<feature>.router.ts`
- WHEN it is inspected
- THEN it contains no direct `prisma.*` calls and no business rules
- AND each handler validates input, calls a service, and maps the result via a DTO

#### Scenario: Service is transport-agnostic
- GIVEN any `<feature>.service.ts`
- WHEN it is inspected
- THEN it does not reference Express `req`/`res`
- AND it owns the use-case logic and any multi-write transaction

### Requirement: Tenant scoping is enforced in the repository
Multi-tenant isolation MUST be applied in the repository layer from a `TenantContext`, not
repeated per query in routers. A repository query for a tenant-owned entity MUST include the
`empresaId` filter; platform-ADMIN (no empresa) scope MUST be modeled explicitly, not via a
silent null.

#### Scenario: Tenant-owned query is scoped centrally
- GIVEN a repository method listing a tenant-owned entity
- WHEN it builds the Prisma query
- THEN the `empresaId` filter comes from the injected `TenantContext`
- AND it is impossible for a caller to omit it

### Requirement: Responses are mapped through explicit DTOs
API responses MUST be produced by explicit DTO mappers; raw Prisma models MUST NOT be spread
into responses. During this refactor, every DTO MUST reproduce the pre-refactor JSON shape and
status code exactly (verified by a committed contract snapshot).

#### Scenario: Refactor preserves the response contract
- GIVEN an endpoint migrated to the layered structure
- WHEN the contract-snapshot test runs against it
- THEN the response shape and status code match the pre-refactor snapshot with zero diff

### Requirement: Central error and Prisma-error mapping
HTTP error mapping MUST be centralized: known Prisma errors (P2002→409, P2025→404, P2003→409)
MUST be translated by a shared mapper consumed by the central error handler, rather than handled
ad-hoc inside individual routers.

#### Scenario: A unique-constraint violation maps to 409 centrally
- GIVEN a service write that hits a Prisma P2002 unique violation
- WHEN the error propagates to the central handler
- THEN the response is HTTP 409 with the uniform `{ error: { message } }` shape
- AND no router contains bespoke P2002 handling for that case

### Requirement: List endpoints support a back-compatible pagination contract
List endpoints MUST accept optional `page` and `pageSize` query params and, when provided,
return `{ items, total, page, pageSize }`. When the params are absent, the endpoint MUST behave
exactly as before the refactor so existing frontend calls keep working.

#### Scenario: Absent pagination params preserve current behavior
- GIVEN a list endpoint called without `page`/`pageSize`
- WHEN it responds
- THEN the payload matches the pre-refactor contract snapshot (no breaking change)

### Requirement: The proceso engine is pure domain
The proceso stage machine, plazos and form-schema logic MUST live under `domain/procesos/` as
pure functions with no Express or Prisma dependency, and MUST be unit-testable in isolation. The
proceso service wires the domain to the repository.

#### Scenario: Engine is testable without HTTP or DB
- GIVEN the stage-machine/plazos logic in `domain/procesos/`
- WHEN it is unit-tested
- THEN the tests run against plain inputs without starting Express or touching the database
