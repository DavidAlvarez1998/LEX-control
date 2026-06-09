# Tasks: foundations-roles-plans-clientes

> Decisions Q1–Q6 + Q8 CONFIRMED (see state.yaml). Revised for review blockers B1 (db-push DDL),
> B2 (seat-gate integration with existing endpoints), B3 (tightenings). DDL via `prisma db push`
> (repo has NO migrations dir) — never `prisma migrate dev` against the live DB.

## Review Workload Forecast
- **Changed-lines budget: High** (~700–1000 lines: ~11 models + 6 enums in `schema.prisma`, seed catalogs + 5 plans, backfill, entitlements engine, roles service, middleware additions, and the seat-gate hooks in two existing routers).
- **Chained PRs recommended: Yes** — split along the three capabilities plus the cross-cutting schema/seed.
- **Suggested split:** Phase 1 (schema + push + seed + backfill) → Phase 2 (`empresa-roles` enforcement + B2 endpoint integration) → Phase 3 (`planes-entitlements` engine) → Phase 4 (`clientes` data layer) → Phase 5 (verify). Phases 2 and 3 are interdependent (seat gate calls the engine); keep chained.

## Phase 0 — Confirm scope (mostly done)
- [x] 0.1 Q1 roles=closed-enum, Q2 cliente=single-row, Q3 seat freed on deactivation, Q4 esAdminEmpresa authoritative, Q5 grandfather=firma, Q6 pricing=frozen COP, Q8 baseline via esBaseline. (Recorded in state.yaml.)
- [ ] 0.2 Q7 — confirm permiso seed granularity (recommendation: minimal foundations set `usuarios.*`, `cliente.*` now; modules ship their own later). Non-blocking; can be fixed at 1.7.

## Phase 1 — Backend: schema, db push, seed, backfill ✅ DONE 2026-06-05
- [x] 1.1 `schema.prisma`: enums `RolEmpresa`, `EstadoSuscripcion`, `EstadoCliente`, `CanalIngreso`, `TipoCaso`, `Viabilidad`. (6 enums, validated.)
- [x] 1.2 `Modulo`/`Permiso`/`RolEmpresaPermiso`/`UsuarioRolEmpresa`. NOTE: `UsuarioRolEmpresa.empresaId` is a denormalized scalar WITHOUT a FK — having both `usuarioId` and `empresaId` as Cascade FKs would be a diamond from Empresa (errno-150 per project convention). Cleanup is via `usuarioId` Cascade. `asignadoPorId` also scalar (audit, no FK).
- [x] 1.3 `Plan`(precioMensual COP)/`PlanModulo`/`PlanCuota`/`Suscripcion`(@@unique empresaId)/`SuscripcionModulo`/`SuscripcionCuota`. No PlanFlag.
- [x] 1.4 `Cliente` — outgoing FKs SetNull, only `empresaId` Cascade; 5 indexes.
- [x] 1.5 back-refs on `Empresa`/`Usuario`/`Litigante`/`TipoProceso`; `@@unique([empresaId, tipoDocumento, numeroDocumento])` ADDED to `Litigante` (0 existing dups verified). `prisma format`+`validate` clean.
- [x] 1.6 `prisma db push --accept-data-loss` (only the Litigante unique warned; 0 dups → safe) + `prisma generate`. 11 tables created, no errno-150. Existing 98 tests still green.
- [x] 1.7 `src/seed-foundations.ts`: 12 módulos (6 baseline + 6 non-baseline incl. the 3 toggles), 4 permisos (`cliente.*` under comercial, Q7 minimal), 8 RolEmpresaPermiso rows. Idempotent upserts.
- [x] 1.8 5 Plans + 15 PlanModulo + 18 PlanCuota from the price card; frozen COP (bufete_pro=1.423.500); baseline NOT in PlanModulo. Matches spec.
- [x] 1.9 BACKFILL: 2 Empresas → Suscripción on firma (ACTIVA); 3 USUARIO → UsuarioRolEmpresa (esAdmin⇒ADMINISTRADOR else JURIDICO). 0 empresas without plan, 0 users without role.

## Phase 2 — empresa-roles: enforcement + B2 endpoint integration ✅ DONE 2026-06-05
- [x] 2.1 `auth.ts`: `requireAuth` resolves `req.rolesEmpresa` (defensive `?? []` so mocks/tokens without the relation don't break). Existing auth unchanged (98 tests green).
- [x] 2.2 `auth.ts`: `requirePermiso(clave)` — module gate (403 `Módulo no contratado`) → RBAC gate (403); `esAdminEmpresa` short-circuits RBAC; `empresaId` only from `empresaIdRequerido(req)`. Unit-tested.
- [x] 2.3 `src/modules/roles/roles.service.ts`: `assertSeatAvailable` (FOR UPDATE on `suscripciones` row, count `activo=true` holders `< cap`, NULL=∞), `assignRole`/`removeRole` (idempotent, `esAdminEmpresa`↔ADMINISTRADOR sync). Unit-tested.
- [x] 2.4 **B2**: `usuarios.router` POST (tx: seat-check+create+role; ADMIN-platform skips), PATCH (esAdminEmpresa→assign/remove ADMINISTRADOR before update); `mi-empresa.router` POST `/usuarios` (tx: seat-check+create+role). Existing contracts unchanged; tests' mocks updated. **Verified live**: 2nd ADMINISTRADOR on firma→409, abogado→201 with JURIDICO seat.

## Phase 3 — planes-entitlements: engine ✅ DONE 2026-06-05
- [x] 3.1 `src/modules/entitlements/entitlements.service.ts`: `resolveEntitlements(empresaId)` → `{ modulosHabilitados:Set, cuotas:Map<RolEmpresa,number> }`. Plan+overrides+baseline always-on, NULL⇒Infinity, non-active sub ⇒ baseline + caps 0. Unit-tested (4 cases).
- [x] 3.2 Module gate (2.2) and seat gate (2.3) call `resolveEntitlements`.
- [~] 3.3 Plan/Suscripcion CRUD endpoints — OUT OF SCOPE (later admin module); foundations only seeds + backfills.

## Phase 4 — clientes: data layer ✅ DONE 2026-06-05
- [x] 4.1 `src/modules/clientes/clientes.schemas.ts` + `clientes.router.ts` (mounted `/clientes` in app.ts): tenant-scoped list/read/create/update (empresaId from `req`, never body), defaults PROSPECTO / EN_ESTUDIO, pure-lead creation. Guarded by `requireAuth` + `requirePermiso("cliente.*")`.
- [x] 4.2 `assertSameEmpresa` (B3): rejects cross-empresa `responsableComercialId`/`litiganteId`/`necesidadTipoProcesoId` (the last allows global TipoProceso). Tested.
- [x] 4.3 `POST /clientes/:id/convertir`: PROSPECTO→CLIENTE, links Litigante via atomic upsert on `(empresaId,tipoDocumento,numeroDocumento)` (else create if no doc), sets `litiganteId`/`convertidoEn`. Tested + verified live.
- [x] 4.4 `responsableComercial`/`comercial` role expectation noted; permiso seeded under `comercial` module. (Abogado=JURIDICO expectation deferred to comercial→procesos bridge change.)

## Phase 5 — Verify ✅ DONE 2026-06-05
- [x] 5.1 `tsc --noEmit` clean after `prisma generate` (build proxy).
- [x] 5.2 `pnpm test` — 120 green: existing 98 + foundations (12: entitlements/seat-gate/requirePermiso) + clientes (10: isolation/pure-lead/conversion-link/same-empresa-FK/module-gate).
- [~] 5.3 Applied to the live DEMO DB (not a separate copy): `db push` + seed + backfill; every Empresa has a Suscripcion (firma), every USUARIO ≥1 role; existing auth endpoints still work (98 tests + live login).
- [x] 5.4 Live: seat cap enforced (firma 2nd ADMINISTRADOR→409, abogado→201+JURIDICO); clientes CRUD + module gate + conversion→Litigante verified live.

## Notes
- DDL: repo uses `prisma db push` (no `prisma/migrations/`). Rollback = manual DROP of new tables/enums (see proposal Rollback). Test on a non-prod copy first; `db push` can warn on data loss.
- Env/perms: `lex-control-api/.env` (DATABASE_URL) is write-blocked per repo memory — push/seed use the existing connection without editing `.env`.
- `esAdminEmpresa` stays AUTHORITATIVE (`requireEmpresaAdmin` unchanged); `ADMINISTRADOR` is its synced mirror — do NOT deprecate `esAdminEmpresa`.
- New gates fail CLOSED only on NEW endpoints; never mount `requirePermiso` on an existing endpoint in this change.
