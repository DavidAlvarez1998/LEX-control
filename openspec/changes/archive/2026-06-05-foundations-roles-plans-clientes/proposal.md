> STATUS 2026-06-05: user decisions CONFIRMED (see `state.yaml` → `decisions`/`confirmed_questions`)
> and this proposal REVISED for the adversarial-review blockers (B1 db-push DDL, B2 seat-gate
> integration with existing endpoints, B3 tightenings). Still a PROPOSAL — not applied. The model is
> sound; remaining open item is only Q7 (permiso seed granularity). See `REVIEW.md` for the full
> adversarial pass.

# Proposal: Foundations — Empresa Roles, Plans/Entitlements, and Clientes/Prospectos

## Intent
LEX Control's roadmap (contable, comercial, contratos modules; tiered pricing; a sales
funnel) needs three foundational data layers that do not exist yet: a canonical **per-company
role + permission** system, a **plan/entitlement** layer that gates which módulos a despacho
contracts and how many seats each role gets, and a **Cliente/Prospecto** CRM identity distinct
from the procedural `Litigante`. This change introduces those three layers **additively** on top
of the current schema and middleware — nothing existing is dropped, renamed, or re-typed — so the
later feature modules have a stable spine to build on.

## Background / Current State
Today authorization is a single axis: `Usuario.rol` (`ADMIN` | `USUARIO`) plus the boolean
`Usuario.esAdminEmpresa` flag (enforced by `requireEmpresaAdmin`). There is no notion of a
finer-grained role *within* a despacho, no concept of which feature módulos a company has paid
for, and no seat limits. Billing is modeled only at the `Servicio` / `EmpresaServicio` level
(per-company negotiated price), which the codebase treats as its core idiom (catalog default +
per-empresa override). The legal module already established the precedent of a **seeded catalog
table** (`AreaPractica`) rather than enums for extensible vocabularies. There is a `Litigante`
(procedural party) but no commercial CRM entity: a lead that never becomes a case, or a
counterparty that is not "our client", cannot be cleanly modeled.

The pricing tiers (Canva price card) make two enforcement questions load-bearing: "is módulo X
enabled for this empresa?" and "does assigning role R exceed the seat cap?". Foundations answers
both with one `resolveEntitlements(empresaId)` resolver.

**DDL reality:** this repo manages its MySQL schema with `prisma db push` — there is no
`prisma/migrations/` directory (CLAUDE.md documents `push` as the schema-sync path). This change is
applied additively with `prisma db push` + `prisma generate`, NOT `prisma migrate dev` (running
`migrate dev` against the push-managed DB would try to baseline the entire existing schema and can
prompt a destructive reset).

## Scope

### In Scope
- **Roles / authorization (second, orthogonal axis)**
  - New `RolEmpresa` enum (closed set: `ADMINISTRADOR`, `JURIDICO`, `CONTABLE`, `COMERCIAL`) — the 4 seat slots plans quote. (DECISION Q1: closed enum, no custom roles this phase.)
  - Seeded catalogs: `Modulo` (with `esBaseline`), `Permiso` (namespaced under a `Modulo`), `RolEmpresaPermiso` (default RBAC matrix).
  - `UsuarioRolEmpresa` — per-user role assignment, denormalized `empresaId` for O(1) seat counting; this row is the seat unit. (DECISION Q3: a seat counts only while `Usuario.activo = true`, so deactivation frees it.)
  - Middleware extension: `requireAuth` also resolves `req.rolesEmpresa` from DB; new `requirePermiso(clave)` (module gate + RBAC gate); a transactional seat gate at role assignment. `empresaId` is ALWAYS taken from `req` (DB-resolved via `empresaIdRequerido(req)`), never from client input.
- **Integration with the EXISTING user-management endpoints (B2)** — the seat gate is only real if every
  write path goes through it:
  - `usuarios.router.ts` `POST /` and `PATCH /:id` (platform ADMIN) and `mi-empresa.router.ts`
    `POST /usuarios` (empresa admin) MUST route member creation / `esAdminEmpresa` toggles through the
    seat-gated role-assignment path: creating a member assigns ≥1 `UsuarioRolEmpresa` (counting against
    the cap), and setting `esAdminEmpresa = true/false` adds/removes the `ADMINISTRADOR` assignment so the
    flag and the mirror role never drift.
  - `mi-empresa.router.ts` deactivate/activate already toggles `activo`; no change needed there for seats
    (the cap COUNT filters `activo = true`), but the same flag-sync rule applies if it ever toggles
    `esAdminEmpresa`.
- **Plans / entitlements (packaging layer above Servicio, never gating billing)**
  - `Plan` catalog (ADMIN-created, mirrors `Servicio`), with `PlanModulo`, `PlanCuota`. Non-baseline feature toggles (`logo_personalizado`, `ia_redaccion`, `automatizacion_contratos`) are modeled as **non-baseline `Modulo` rows** — NOT as a separate `PlanFlag` table (B3: one source of truth; `resolveEntitlements` already returns `modulosHabilitados`).
  - `Suscripcion` (one current plan per empresa, `@@unique([empresaId])`) with `EstadoSuscripcion`, plus per-empresa overrides `SuscripcionModulo` / `SuscripcionCuota` (parallel to `EmpresaServicio`).
  - `resolveEntitlements(empresaId)` engine: plan defaults + overrides + always-on baseline módulos; `limite NULL ⇒ Infinity`. For a non-active suscripción (`SUSPENDIDA`/`CANCELADA`) it returns baseline módulos only and **all role caps = 0** (B3: blocks new seats for suspended firms; existing active members keep working until reactivation).
- **Cliente / Prospecto CRM identity**
  - `Cliente` (single-row lifecycle: `EstadoCliente` PROSPECTO → CLIENTE → DESCARTADO), with CRM enums (`CanalIngreso`, `TipoCaso`, `Viabilidad`, reusing `TipoPersona`/`TipoDocumento`).
  - Bridge columns to the procedural world: nullable `litiganteId` FK→`Litigante` (set on conversion) and `necesidadTipoProcesoId` FK→`TipoProceso`; `responsableComercialId` FK→`Usuario`.
  - All outgoing FKs `SetNull`; only `Empresa` cascades into `Cliente` (errno-150 discipline). Application code MUST validate that `responsableComercialId`, `litiganteId`, and `necesidadTipoProcesoId` belong to the SAME empresa as the `Cliente` (B3: no cross-tenant FK references).
- **Schema apply / seed / backfill** — single `prisma db push` + `pnpm generate`: 6 enums, ~11 tables, seed Modulo/Permiso/RolEmpresaPermiso/5 Plans, backfill every `Empresa`→`Suscripcion` (grandfathered onto `firma`) and every `USUARIO`→≥1 `UsuarioRolEmpresa`.
- **Existing-model back-references** (relation fields only, no column changes) on `Empresa`, `Usuario`, `Litigante`, `TipoProceso`. NOTE: a `@@unique([empresaId, tipoDocumento, numeroDocumento])` on `Litigante` is added IF the conversion match must be an atomic upsert (B3); otherwise conversion is an application-level find-or-create (documented as best-effort).

### Out of Scope
- Admin/client UI screens for managing plans, subscriptions, roles, or the CRM funnel (later module changes consume these foundations).
- The full per-module `Permiso` catalog for contable/comercial/contratos (this change seeds only a minimal foundations set; each module ships its own permissions later — Q7).
- Billing/invoice generation from `Plan` / `Suscripcion`. (Prices are stored as frozen COP — DECISION Q5=B — so there is no SMMLV→COP resolution to defer.)
- The "Solicitud de Asignación de Procesos" bridge entity (foundations only makes it FK-ready via stable `Cliente.id`).
- The contratos-module write that stamps `convertidoEn` / promotes a `Cliente` to `CLIENTE` (foundations only provides the columns + lifecycle states).
- Changing the BEHAVIOR of the existing auth gates themselves (`requireAuth`/`requireRole`/`requireEmpresaAdmin`), the JWT shape, `Rol`, or `tokenVersion`. (The existing user-management ENDPOINTS are extended to assign roles/seats per B2, but the auth gates and token are untouched.)

## Capabilities

### New Capabilities
- `empresa-roles`: the second authorization axis — `RolEmpresa` enum, seeded `Modulo`/`Permiso`/`RolEmpresaPermiso` catalogs, per-user `UsuarioRolEmpresa` assignments, and the `requirePermiso` (module + RBAC) and seat-gate enforcement (integrated into the existing user-management endpoints).
- `planes-entitlements`: the `Plan` catalog and per-empresa `Suscripcion` with módulo/seat overrides, plus the `resolveEntitlements(empresaId)` engine that the module and seat gates consume.
- `clientes`: the commercial `Cliente`/Prospecto lifecycle entity, distinct from `Litigante`, bridged by a nullable `litiganteId`.

### Modified Capabilities
- `authentication` middleware is *extended* (additive `req.rolesEmpresa`, new `requirePermiso`, new seat gate), but every existing requirement (`requireAuth`/`requireRole`/`requireEmpresaAdmin`, JWT, tokenVersion) is unchanged and keeps working.
- The existing user-management endpoints (`usuarios`, `mi-empresa`) gain role/seat side-effects (B2) without changing their current request/response contracts.

## Approach
Adopt the entitlements-driven design as the spine, mirroring the codebase's core "catalog default +
per-empresa override" idiom: `Plan`→`Suscripcion` parallels `Servicio`→`EmpresaServicio`, and
`SuscripcionModulo`/`SuscripcionCuota` parallel the negotiated-price override. Roles stay a **closed
enum** (stable join key for seat quotas and plan tiers), while permissions are a **seeded table**
(extensible without migration, like `AreaPractica`), namespaced under a `Modulo` so disabling a
módulo short-circuits all its permisos at once. `Cliente` is a **single row** whose `estado`
transitions across its lifecycle, preserving lead identity through conversion and giving the future
assignment bridge one stable anchor. Everything is additive and applied via `prisma db push`; new
fine-grained gates **fail closed only on new endpoints**, so a missed backfill never bricks existing
auth. The seat gate is wired into the existing member-creation paths so plan caps are actually
enforced rather than bypassable.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/prisma/schema.prisma` | Modified | 6 new enums, ~11 new models, back-reference relation fields on `Empresa`/`Usuario`/`Litigante`/`TipoProceso` (+ optional `@@unique` on `Litigante` per B3) |
| `lex-control-api` schema apply | Run | Single `prisma db push` + `pnpm generate` (NO `prisma migrate dev` — repo has no migrations dir) |
| `lex-control-api/src/seed-foundations.ts` | New | Seed Modulo/Permiso/RolEmpresaPermiso catalogs + 5 Plan rows with PlanModulo/PlanCuota; backfill every Empresa→Suscripcion(firma) and every USUARIO→≥1 UsuarioRolEmpresa |
| `lex-control-api/src/modules/entitlements/entitlements.service.ts` | New | `resolveEntitlements(empresaId)` engine (plan + overrides + baseline; NULL⇒Infinity; non-active sub ⇒ caps 0) |
| `lex-control-api/src/modules/roles/roles.service.ts` | New | Transactional seat-gated `assignRole`/`removeRole` (+ `esAdminEmpresa`↔`ADMINISTRADOR` sync) used by the user-management routers |
| `lex-control-api/src/middleware/auth.ts` | Modified | `requireAuth` resolves `req.rolesEmpresa`; add `requirePermiso(clave)`; `empresaId` only from `empresaIdRequerido(req)` |
| `lex-control-api/src/modules/usuarios/usuarios.router.ts` | Modified | POST/PATCH route role assignment + `esAdminEmpresa` sync through the seat gate (B2) |
| `lex-control-api/src/modules/mi-empresa/mi-empresa.router.ts` | Modified | `POST /usuarios` assigns ≥1 seat-gated role; `esAdminEmpresa` toggle syncs `ADMINISTRADOR` (B2) |
| `lex-control-api/src/index.ts` | Regen | Re-exports stay correct after `prisma generate` |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Seat/quota enforcement race (two concurrent first-assignments both pass) | Med | Transactional count-then-insert with `SELECT ... FOR UPDATE` on a STABLE parent row — the empresa's `Suscripcion` row — so the lock exists even when the role currently has zero `UsuarioRolEmpresa` rows |
| Seat cap bypassable via existing endpoints (B2) | High→Mitigated | Member creation / `esAdminEmpresa` toggles in `usuarios` + `mi-empresa` routers go through the seat-gated assignment service; no write path sets roles or the flag outside it |
| `esAdminEmpresa` vs `RolEmpresa.ADMINISTRADOR` drift | Med | `esAdminEmpresa` stays AUTHORITATIVE; every flag-write site (both routers) syncs the `ADMINISTRADOR` row atomically; no code sets one without the other |
| Cross-tenant reference via `Cliente` FKs or client-supplied `empresaId` | Med | `empresaId` only from `req` (`empresaIdRequerido`); app validates `responsableComercialId`/`litiganteId`/`necesidadTipoProcesoId` are same-empresa on write |
| MySQL errno-150 (multiple cascade paths to one table) | Med | `UsuarioRolEmpresa` cascades from `Usuario` and `Empresa` only (no shared cascade target); all `Cliente` outgoing FKs are `SetNull` |
| Suspended firm locked out (caps→0 blocks even reactivation) | Low | Non-active sub sets new-seat caps to 0 but existing active members keep working; reactivation restores plan caps before any new assignment |
| Conversion `Cliente`→`Litigante` duplicates parties | Low | Either add `@@unique([empresaId,tipoDocumento,numeroDocumento])` on `Litigante` for an atomic upsert, or spec conversion as app-level find-or-create (best-effort, dedupe handled explicitly) — see B3 |
| Missed/partial backfill leaves users with no role or empresa with no plan | Med | New gates fail closed ONLY on new endpoints; existing auth keeps working; backfill runs in the same deploy as the push |

## Rollback Plan
The schema change is additive and applied with `prisma db push` (no migration history). Rollback is
manual and safe because no existing table's columns are altered (the back-reference relation fields
are virtual in Prisma and produce no column changes): `DROP TABLE` the ~11 new tables and `DROP TYPE`
the 6 new enums (or `git revert` the schema and re-run `prisma db push`, which drops the now-absent
tables — verify on a non-prod copy first, as `db push` can warn about data loss). Remove the new
`entitlements`/`roles` services, the `seed-foundations` script, the `requirePermiso` additions in
`auth.ts`, and revert the seat-gate hooks in the two user-management routers. Because every new
fine-grained gate is mounted on new endpoints only, removal leaves all current behavior intact.
Re-run `pnpm generate`.

## Dependencies
- Existing `Empresa`, `Usuario`, `Litigante`, `TipoProceso`, `Servicio`/`EmpresaServicio` models (already in `schema.prisma`, pushed to MySQL).
- The seeded-catalog precedent from `legal-tramites` (`AreaPractica`) for the Modulo/Permiso pattern.
- The `requireEmpresaAdmin` middleware (stays authoritative; this change mirrors it as `ADMINISTRADOR`).

## Success Criteria
- [ ] A single `prisma db push` + `pnpm generate` adds all 6 enums and ~11 tables with no errno-150 and no change to existing tables' columns. (No `prisma migrate dev`.)
- [ ] Seed loads the Modulo (~11 claves), Permiso, and RolEmpresaPermiso catalogs, plus the 5 Plan rows with their PlanModulo/PlanCuota matching the price card; all `precioMensual` are frozen COP amounts.
- [ ] Backfill gives every `Empresa` a `Suscripcion` on `firma` and every `USUARIO` ≥1 `UsuarioRolEmpresa` (`esAdminEmpresa=true`⇒`ADMINISTRADOR`, else `JURIDICO`).
- [ ] `resolveEntitlements(empresaId)` returns `{ modulosHabilitados, cuotas }` honoring plan defaults, overrides, baseline always-on, `NULL⇒Infinity`, and caps=0 for a non-active suscripción.
- [ ] Creating a member via the EXISTING `usuarios` / `mi-empresa` endpoints consumes a seat and (when `esAdminEmpresa`) creates the `ADMINISTRADOR` row; exceeding the cap is rejected; deactivating a member frees their seat.
- [ ] `requirePermiso(clave)` returns 403 when the permiso's módulo is not entitled, and 403 when no held `RolEmpresa` grants the clave (`esAdminEmpresa` short-circuits the RBAC gate only); `empresaId` is read only from `req`.
- [ ] A `Cliente` can be created as a pure lead (no `litiganteId`) and later linked to a `Litigante`; cross-empresa FK references are rejected; only `Empresa` cascades into `Cliente`.
- [ ] Existing auth (`requireAuth`/`requireRole`/`requireEmpresaAdmin`, JWT, tokenVersion) is unchanged and all existing tests still pass.

## Open Questions
Decisions Q1–Q6 + Q8 are CONFIRMED (see `state.yaml` → `confirmed_questions`). Only **Q7** remains
open (permiso seed granularity — recommendation: seed a minimal foundations set now, e.g. `usuarios.*`,
`cliente.*`, and let each later module ship its own catalog). The three adversarial-review blockers
(B1 db-push DDL, B2 seat-gate integration, B3 tightenings) are folded into the scope above; see
`REVIEW.md` for the full findings.
