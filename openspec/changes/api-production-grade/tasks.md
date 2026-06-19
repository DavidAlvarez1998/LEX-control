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

## Track 3 — Pagination + OpenAPI  ◑ MAYORMENTE HECHO
- [x] OpenAPI 3 generado desde Zod (`@asteasolutions/zod-to-openapi@7`) + Swagger UI en `/docs` y doc en `/openapi.json` (`src/openapi/`). Cubre auth/procesos/clientes/facturación + componentes Error/Paginado + JWT. Verificado en vivo.
- [x] Helper de paginación compartido (`src/shared/pagination.ts`, `parsePage`/`paginated`) cableado: `/procesos` (obligatorio, ya existía) + `/clientes` (OPT-IN retrocompatible: `?page` → sobre, sin params → array). count+skip/take en repo. +1 test.
- [ ] (Pendiente) Extender el opt-in a los listados de `contable` (ingresos/egresos/cartera) — mismo patrón.
- [ ] (Diferido) Tipos generados desde OpenAPI consumidos por admin+client — cross-repo; coordinar con el trabajo paralelo de front sin commitear.

## Track 4 — Data integrity + observability  ✅ DONE
- [x] Transaction boundaries: `registrarPago` (read-check-write atómico en `$transaction`); parte+recompute atómico (agregar/editar/eliminar parte + `recomputarTituloLaboral` en una sola tx). `autoavanzarEtapas` ya era atómico por paso (createEtapa+update por avance).
- [x] Idempotency: `registrarPago` no duplica el Ingreso ante reintento con el mismo `numeroComprobante` (no-op idempotente). +1 test.
- [x] Observability: propagación de request-id con AsyncLocalStorage (`src/shared/request-context.ts`; el logger inyecta `reqId` solo); access-log por request (método/ruta/status/durationMs); graceful shutdown (SIGTERM/SIGINT → server.close + `prisma.$disconnect`). Verificado en vivo.
- [ ] (Diferido) Modernizar a fondo los mocks acoplados a Prisma — el `proceso.count` del consecutivo sigue pendiente (api-hardening).
- [x] Verified: build exit 0 + 444/444 tests

## Program close
- [ ] PUSH (4 repos) — all committed locally, not pushed
- [ ] Archive this umbrella + fold spec deltas into `openspec/specs/api-architecture` when all tracks done
