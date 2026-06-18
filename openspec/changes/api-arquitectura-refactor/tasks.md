# Tasks — API architecture refactor (agent-driven, non-breaking)

Each task is sized for one session / one agent. Gate for EVERY code task:
`pnpm test` green + `npx tsc --noEmit` clean + `pnpm build` green + **zero contract-snapshot diff**.
No route/path/payload/schema/frontend changes at any step.

## Phase 0 — Safety net + foundations (no behavior change)
- [ ] 0.1 Contract-snapshot harness: a vitest test that exercises every endpoint (reuse the
      supertest setup) and writes committed JSON snapshots of status + response shape per route.
- [ ] 0.2 Run it once to capture the **baseline** snapshots from the current code; commit them.
- [ ] 0.3 `shared/prisma.ts` — re-export the singleton (alias of `src/index`), no behavior change.
- [ ] 0.4 `shared/tenant.ts` — `TenantContext` type + `tenant(req)` helper (empresaId / platform scope).
- [ ] 0.5 `shared/errors.ts` — `AppError` + `mapPrismaError()` (P2002→409, P2025→404, P2003→409).
- [ ] 0.6 Wire `mapPrismaError` into `middleware/error.ts` (additive; existing HttpError path intact).
- [ ] 0.7 `shared/logger.ts` (pino) + request-id middleware; `errorHandler` logs through it.
- [ ] 0.8 `shared/pagination.ts` — parse `page/pageSize`, build `{ items, total, page, pageSize }`
      (used only where adopted; absent params = current behavior).
- [ ] 0.9 Verify: full suite + snapshot baseline still green. Commit foundations.

## Phase 1 — Pilot module `clientes` (locks the pattern)
- [ ] 1.1 `clientes.repository.ts` — move all `prisma.*` from router/service here; inject TenantContext.
- [ ] 1.2 `clientes.service.ts` — business logic + transactions; depend on the repository only.
- [ ] 1.3 `clientes.dto.ts` — mappers reproducing the exact current response shapes.
- [ ] 1.4 `clientes.router.ts` — thin coordinators (no `prisma.`, no rules).
- [ ] 1.5 Verify gate. Document the pattern in design.md "pilot notes". Commit.

## Phase 2 — Small/medium CRUD modules (replicate the pattern, parallelizable by agents)
- [ ] 2.1 `litigantes`  → repository + service + dto + thin router. Gate. Commit.
- [ ] 2.2 `servicios`   → same. Gate. Commit.
- [ ] 2.3 `planes`      → same. Gate. Commit.
- [ ] 2.4 `empresas`    → same. Gate. Commit.
- [ ] 2.5 `usuarios` (+ `usuarios.shared.ts`) → same. Gate. Commit.
- [ ] 2.6 `mi-empresa`  → same. Gate. Commit.
- [ ] 2.7 `catalog`     → same. Gate. Commit.

## Phase 3 — Larger rule-heavy modules
- [ ] 3.1 `contable` (+ `cartera.service.ts`) → repository + service split per sub-area; dto. Gate. Commit.
- [ ] 3.2 `facturacion` → same. Gate. Commit.
- [ ] 3.3 `comercial` (864 lines) → split into cohesive services (fases/cotización/seguimiento). Gate. Commit.
- [ ] 3.4 `ventas` (5 route groups) → service+repo per group; keep the 5 mount paths. Gate. Commit.
- [ ] 3.5 `buscar` → repository per searched entity; service composes by role. Gate. Commit.

## Phase 4 — `procesos` + domain extraction (biggest, done with pattern proven)
- [ ] 4.1 `domain/procesos/` — move pure logic: stage machine (`siguienteEtapaAuto`,
      `terminalDecidido`, `autoavanzarEtapas` core), `recomputarTituloLaboral` rule, `esquema.ts`,
      `diasHabiles.ts`/`plazos.ts`. No Express/Prisma. Add unit tests.
- [ ] 4.2 `procesos.repository.ts` — all Prisma (proceso/partes/documentos/historial), tenant-scoped.
- [ ] 4.3 `procesos.service.ts` — orchestrate domain + repository + transactions.
- [ ] 4.4 `procesos.dto.ts` — `toProcesoDetalleDTO` etc. reproducing current shapes (incl. partes).
- [ ] 4.5 `procesos.router.ts` — thin; target < ~250 lines, no `prisma.`. Gate. Commit.

## Phase 5 — Cross-cutting rollout
- [ ] 5.1 Remove remaining ad-hoc Prisma-error handling now covered by `mapPrismaError`.
- [ ] 5.2 Adopt pagination on the heavy list endpoints (procesos, clientes, contable) — additive.
- [ ] 5.3 Assert globally: 0 `prisma.` in `*.router.ts`; routers have no business logic.
- [ ] 5.4 Final full verify (tests + tsc + build + snapshot) across all modules.

## Phase 6 — Optional (deferred, separate decision)
- [ ] 6.1 Generate OpenAPI from the Zod schemas; publish shared types so the frontends stop
      re-declaring the API contract.

## Agent orchestration notes
- Per-module jobs follow the fixed recipe in design.md §6; run in **isolated worktrees** so
  parallel modules never conflict (modules are file-disjoint).
- A **verifier agent** runs the gate after each module; failure → discard worktree, do not merge.
- Suggested orchestration: `pipeline(modules, migrate, verify)` after Phase 0+1 land
  (foundations + pilot establish the pattern first). Requires opting into multi-agent orchestration.

## Archive checklist
- [ ] All phases verified green; 0 `prisma.` in routers; engine in `domain/` unit-tested.
- [ ] Merge delta to `openspec/specs/api-architecture`.
- [ ] state.yaml + move to `openspec/changes/archive/`.
