# Design — layered architecture + non-breaking, agent-driven migration

## 1. Target layers and the dependency rule

Dependencies point inward only. The Service never imports Express (`req`/`res`); the
Repository never holds business rules; the Router never calls Prisma.

| Layer | File | Responsibility | Must NOT |
|---|---|---|---|
| Router | `<f>.router.ts` | routes, status codes, middleware (auth/validate), call service, map via DTO | business logic, Prisma |
| Service | `<f>.service.ts` | use cases, rules, orchestration, **transactions**, business authorization | touch `req`/`res`, raw Prisma |
| Repository | `<f>.repository.ts` | Prisma queries, **forced `empresaId` scoping**, pagination | business rules |
| DTO/mapper | `<f>.dto.ts` | response shape (model → API) | — |
| Domain | `domain/<area>/` | pure logic (proceso engine) | Express, Prisma |
| Shared | `shared/` | logger, errors, pagination, tenant, prisma | feature logic |

## 2. Folder layout (target)
```
src/
  shared/{prisma,logger,errors,pagination,tenant}.ts
  domain/procesos/{maquina-etapas,plazos,esquema}.ts   # esquema.ts/diasHabiles.ts already exist → move here
  modules/<feature>/{<f>.router,<f>.service,<f>.repository,<f>.schemas,<f>.dto}.ts
  middleware/ config/                                   # kept as-is
```

## 3. Three invariants (the actual value)

### 3.1 Forced tenant scoping in the repository
Today `empresaId` is repeated in 18 routers → omission risk. Repositories take a
`TenantContext` and apply `empresaId` centrally, so a query cannot forget it.
```ts
export class ClientesRepository {
  constructor(private readonly tenant: TenantContext) {}
  list(f: ClienteFilter) {
    return prisma.cliente.findMany({ where: { empresaId: this.tenant.empresaId, ...toWhere(f) } });
  }
}
```
Platform-ADMIN (no empresa) is modeled explicitly (`tenant.scope = 'platform'`), not by a
silent `null` — repos decide per query whether platform scope is allowed.

### 3.2 Thin router (coordinator only)
```ts
procesoRoutes.post("/:id/partes", requireAuth, requirePermiso("proceso.editar"), validate({ params, body }),
  asyncHandler(async (req, res) => {
    const proceso = await partesService(tenant(req)).agregar(req.params.id, req.body);
    res.status(201).json(toProcesoDetalleDTO(proceso));
  }));
```

### 3.3 Pure proceso domain
The stage machine / plazos / auto-advance (`siguienteEtapaAuto`, `terminalDecidido`,
`autoavanzarEtapas`, `recomputarTituloLaboral`) move to `domain/procesos/`, testable with
plain objects — no HTTP, no DB. The service wires the domain to the repository.

## 4. Cross-cutting conventions
- **Errors**: `shared/errors.ts` maps Prisma errors centrally (P2002→409, P2025→404,
  P2003→409) so routers stop hand-handling them; the existing `errorHandler` consumes it.
- **Logging**: `shared/logger.ts` (pino) + request-id middleware; `errorHandler` logs via it.
- **Pagination**: `shared/pagination.ts` — list endpoints accept `?page&pageSize` and return
  `{ items, total, page, pageSize }`. **Back-compatible**: when params are absent, behavior is
  the current one (a snapshot test pins this so the frontend does not break).
- **DTO**: explicit mappers; never spread a Prisma model into a response. The first DTOs MUST
  reproduce today's exact JSON (verified by the contract snapshot).
- **Transactions**: live in the Service (use-case boundary), never in the Router.

## 5. Non-breaking strategy (how we guarantee nothing breaks)
1. **Contract snapshot harness** (Phase 0): a test that hits every endpoint and records the
   response shape/status into committed snapshots. Any migration that changes a shape fails CI.
   Built from the existing supertest setup; complements (does not replace) the 424 tests.
2. **Strangler**: introduce service/repository/dto **alongside** the router and switch the
   router body to call them. Routes, paths, middleware order and payloads are untouched.
3. **One module per step**, PR-sized; gates = tests + tsc + build + zero snapshot diff.
4. **Frozen public surface**: no route renamed/moved; `app.ts` mounting unchanged. Internal
   file moves only.

## 6. Agent execution model (SDD agents)
The migration is a **pipeline of independent per-module jobs**, each runnable by one agent in
an isolated git worktree (so parallel module work cannot conflict), followed by a verifier.

**Per-module agent recipe** (deterministic, identical for every module):
1. Read `<f>.router.ts` + `<f>.schemas.ts` (+ existing `<f>.service.ts` if any).
2. Create `<f>.repository.ts`: move every `prisma.*` call here, inject `TenantContext`.
3. Create/extend `<f>.service.ts`: move business logic + transactions; depend on the repo.
4. Create `<f>.dto.ts`: mappers reproducing today's exact response shapes.
5. Rewrite `<f>.router.ts` to thin coordinators (no `prisma.`, no rules).
6. Keep routes/paths/middleware/payloads identical.

**Verifier agent** (runs after each module): `pnpm test` + `npx tsc --noEmit` + build +
contract-snapshot diff. Pass → keep; fail → discard the worktree, report, do not merge.

This can be orchestrated as a Workflow: `pipeline(modules, migrate, verify)` — each module
flows migrate→verify independently. Run order respects dependencies (foundations first, then
`clientes` pilot to fix the pattern, then the rest). Requires the user to opt into multi-agent
orchestration at execution time.

## 7. Module migration order (low-risk first)
1. `shared/` foundations + contract snapshot (no behavior change).
2. **Pilot: `clientes`** (medium, already has a service) — locks the pattern.
3. `litigantes`, `servicios`, `planes`, `empresas`, `usuarios` (small/medium CRUD).
4. `contable`, `facturacion`, `comercial`, `ventas` (larger, more rules).
5. **`procesos`** + extract engine to `domain/procesos/` (biggest impact, done last with the
   pattern proven).
6. Cross-cutting cleanup (central Prisma-error mapping, logging, pagination rollout).
7. (Optional, deferred) OpenAPI generation + shared types for the frontends.

## 7b. Prisma instance, injection and transactions
- **One singleton `PrismaClient`** for the whole process (already the case via `src/index.ts`;
  re-exported from `shared/prisma.ts`). Never `new PrismaClient()` per module — multiple clients
  exhaust the DB connection pool.
- **What gets injected per request is the `TenantContext` (empresaId/scope), NOT a new Prisma
  instance.** Repositories read the singleton; they are constructed per-request with the tenant.
- **Transactions**: a service opens `prisma.$transaction(async (tx) => …)` and passes the scoped
  `tx` client into repository methods, so every write in the use-case participates in the same
  transaction. Therefore repository methods accept an optional client:
  ```ts
  class ClientesRepository {
    constructor(private readonly tenant: TenantContext, private readonly db: PrismaLike = prisma) {}
    withTx(tx: PrismaLike) { return new ClientesRepository(this.tenant, tx); }
    create(data) { return this.db.cliente.create({ data: { ...data, empresaId: this.tenant.empresaId } }); }
  }
  // service:
  await prisma.$transaction(async (tx) => {
    const repo = clientesRepo.withTx(tx);
    await repo.create(...); await otroRepo.withTx(tx).create(...);
  });
  ```
  This keeps the singleton AND lets repositories run inside a transaction. Full constructor DI of a
  mock client is optional — current tests run against a real test DB (integration style), so a DI
  container is not needed.

## 7c. Middleware placement — at the router, never per service
Middleware is an Express/HTTP concern, so it lives in the **router layer only**; services and
repositories are transport-agnostic and have no middleware.
- **Shared middleware** (`requireAuth`, `requireRole`/`requirePermiso`, `validate`, `asyncHandler`,
  request-id, error handler) is applied globally or per-router-group (`router.use(...)`), not
  duplicated per module — this is already the pattern and is kept.
- **Per-module middleware** only when a module genuinely needs it (e.g. `multer` upload in the
  procesos documents routes) — declared in that module's router.
- **Tenant resolution** happens once in `requireAuth` (it already loads `empresaId`); the router
  reads it via `tenant(req)` and passes the `TenantContext` into the service. No "middleware per
  service".
- **Business authorization** that is a domain rule (not a coarse HTTP guard) lives in the service;
  coarse guards (is-authenticated, has-role, has-permiso) stay as router middleware.

## 8. Risks & mitigations
- *Hidden behavior in a fat router* → contract snapshot + characterization before refactor.
- *Tenant scope regressions* → repository is the single choke point; tests per role already exist.
- *Parallel agents clobbering files* → worktree isolation; modules are file-disjoint.
- *Scope creep* → no schema/route/frontend changes allowed in this change.
