# API Architecture Specification

## Purpose
Define the internal architecture of `lex-control-api`: a modular, layered structure
(router → service → repository → dto) with tenant scoping enforced in the data layer, a
pure proceso domain, and shared cross-cutting concerns. The HTTP contract is independent
of this internal structure (frontends are unaffected by it). Established by change
`api-arquitectura-refactor` (2026-06-18): 18/18 routers migrated, 0 direct `prisma.` calls
in routers.

## Requirements

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
`empresaId` filter; platform scope (no empresa) MUST be modeled explicitly. The TenantContext
carries `userId`, `rol`, `empresaId`, `esAdminEmpresa` and `rolesEmpresa`.

#### Scenario: Tenant-owned query is scoped centrally
- GIVEN a repository method listing a tenant-owned entity
- WHEN it builds the Prisma query
- THEN the `empresaId` filter comes from the injected tenant
- AND it is impossible for a caller to omit it

### Requirement: One Prisma instance; transactions via the repository
The application MUST use a single `PrismaClient` singleton (re-exported from `shared/prisma`).
What is injected per request is the `TenantContext`, NOT a new Prisma instance. A service that
needs a transaction MUST open `prisma.$transaction` and construct the repository with the `tx`
client so every write in the use-case participates in the same transaction.

#### Scenario: Multi-write use-case is atomic
- GIVEN a service use-case with several writes
- WHEN it runs
- THEN they execute inside one `prisma.$transaction` via repositories constructed with `tx`

### Requirement: Responses are mapped through explicit DTOs
API responses MUST be produced by explicit DTO mappers; raw Prisma models MUST NOT be spread
into responses where a DTO defines the shape. During the refactor every DTO reproduced the
pre-refactor JSON shape and status code exactly (contract preserved; frontends unaffected).

#### Scenario: Refactor preserves the response contract
- GIVEN an endpoint migrated to the layered structure
- WHEN it responds
- THEN the response shape and status code match the pre-refactor behavior

### Requirement: Central error and Prisma-error mapping
HTTP error mapping MUST be centralized: known Prisma errors (P2002→409, P2025→404, P2003→409)
that reach the central handler unhandled MUST be translated by a shared mapper. Modules MAY
still throw `HttpError` with a specific message where the wording matters (those take priority).

#### Scenario: An unhandled unique-constraint violation maps to 409 centrally
- GIVEN a write that hits a Prisma P2002 not handled in the module
- WHEN the error propagates to the central handler
- THEN the response is HTTP 409 with the uniform `{ error: { message } }` shape

### Requirement: A back-compatible pagination contract is available
A shared pagination helper MUST exist that parses optional `page`/`pageSize` and produces
`{ items, total, page, pageSize }`. List endpoints MAY adopt it; when adopted it MUST remain
back-compatible (absent params → prior behavior) so existing frontend calls keep working.

#### Scenario: Paginated list returns the envelope
- GIVEN a list endpoint that adopted pagination, called with `page`/`pageSize`
- WHEN it responds
- THEN the payload is `{ items, total, page, pageSize }`

### Requirement: The proceso engine is pure domain
The proceso stage-machine logic (auto-advance / terminal decision) MUST live as pure
functions with no Express or Prisma dependency, and MUST be unit-testable in isolation. The
proceso service wires the domain to the repository.

#### Scenario: Engine is testable without HTTP or DB
- GIVEN the stage-machine logic (`maquina-etapas.ts`)
- WHEN it is unit-tested
- THEN the tests run against plain inputs without starting Express or touching the database
