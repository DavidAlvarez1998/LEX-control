# Tasks — API production-grade

## Track 1 — Migrations baseline + CI  ✅ DONE
- [x] Baseline `0_init` (migrate diff --from-empty, 50 tables) + `migration_lock.toml`
- [x] `migrate resolve --applied 0_init` (no SQL executed, no data touched); `migrate status` = up to date
- [x] `MIGRATIONS.md` (safe flow: never `migrate dev` on shared DB; diff offline + `migrate:deploy`)
- [x] CI on 3 repos (api: build + ephemeral MySQL tests; fronts: lint + build)
- [x] Verified: build exit 0 + 442/442 tests
- [x] Committed: api `510ae2b`, client `589a2ae`, admin `8cebf54`, super `2c8affb`
- Detail change: `ops-migraciones-ci`

## Track 2 — Type-safe data layer  ✅ DONE
- [x] Migrate 95 `as never` in 17 `*.repository.ts` → `Prisma.*Input` (Unchecked variants / enums)
- [x] Migrate 8 `as never` in services (clientes/cartera/procesos/ventas) → enums
- [x] Verified: build exit 0 + 442/442 tests (mocks intact — compile-time-only change)
- [x] Committed: api `c00a38b` + `b0283bc`, super `f201027`
- [ ] (Left: 3 hard casts — `n()` money helper + 2 DTO-boundary — tracked in design.md)

## Track 3 — Pagination + OpenAPI  ⏳ PENDING (touches frontend)
- [ ] Unified `{items,total,page,pageSize}` envelope across heavy listings (clientes, contable, …)
- [ ] OpenAPI generated from Zod (`@asteasolutions/zod-to-openapi`) + Swagger at `/docs`
- [ ] Shared generated types consumed by admin + client (stop re-declaring the contract)

## Track 4 — Data integrity + observability  ⏳ PENDING
- [ ] Transaction boundaries: `autoavanzarEtapas`, parte+recompute atomic
- [ ] Idempotency: `registrarPago` (no duplicate Ingreso on retry)
- [ ] Modernize Prisma-coupled test mocks → unblock deferred method fixes (api-hardening)
- [ ] Observability: request-id propagation (AsyncLocalStorage), metrics, error tracking, graceful shutdown

## Program close
- [ ] PUSH (4 repos) — all committed locally, not pushed
- [ ] Archive this umbrella + fold spec deltas into `openspec/specs/api-architecture` when all tracks done
