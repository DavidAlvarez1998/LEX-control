# Design — client-equipo-roles

## Context

This change is a thin client-facing layer over the already-applied `foundations-roles-plans-clientes`
machinery. The hard parts (seat gate with `FOR UPDATE` on the stable `suscripciones` row,
`esAdminEmpresa` mirror, per-request role resolution, `requirePermiso`) exist and are tested. We only
expose role assignment to the empresa admin and let one user hold several roles.

## Decisions

### D1 — Multi-role, roles stay pure
A member may hold any subset of the four `RolEmpresa` values. Access = union of the roles' permisos
(already how `requirePermiso` evaluates `req.rolesEmpresa`). We do **not** grant comercial permisos to
`JURIDICO`; "abogado que vende" = `JURIDICO + COMERCIAL`. Rationale: keeps each role a clean,
single-responsibility permission bundle; the union model already exists in code, so this is zero new
authorization logic.

### D2 — `ADMINISTRADOR` role IS the empresa-admin toggle
We drop the standalone `esAdminEmpresa` checkbox from the UI. Selecting the `ADMINISTRADOR` role is
how you grant team-management; `assignRole`/`removeRole` already mirror `esAdminEmpresa` on
add/remove. `esAdminEmpresa` stays the **authoritative** flag for `requireEmpresaAdmin` (unchanged).
Rationale: one concept, one control — avoids the confusing "admin checkbox AND a role" duplication.

### D3 — Atomic create, atomic reconcile (no orphans, no multi-tx races)
- **Create**: one `prisma.$transaction` — lock the suscripción, create the `Usuario`
  (`esAdminEmpresa = roles.includes(ADMINISTRADOR)`), then for each role `assertSeatAvailable(tx,…)`
  + create the `usuario_roles_empresa` row. Any seat failure rolls back the whole thing → no user
  with a half-applied role set, no orphan.
- **Reconcile (PATCH roles)**: one `prisma.$transaction` — lock the suscripción, read current roles,
  `deleteMany` the removed ones, then seat-check + create the added ones, and set `esAdminEmpresa` to
  match `ADMINISTRADOR` presence in the final set.

We do **not** reuse `assignRole`/`removeRole` here because each opens its own transaction; inlining
keeps create and reconcile each in a single atomic transaction. The seat-counting and lock logic is
identical to `assertSeatAvailable` (active-holder count under a `FOR UPDATE` on `suscripciones`), so
the invariant is preserved.

### D4 — Self-lockout guards
Mirror the existing "cannot deactivate self" rule: an admin MUST NOT remove `ADMINISTRADOR` from
their own account via PATCH (would strip their own team management). Returns 400. (Removing it from
*another* admin is allowed, as long as ≥1 admin remains is **not** enforced here — out of scope;
matches today's lack of a "last admin" guard.)

### D5 — Plan-not-contracted surfaces as "no seat"
A role absent from the plan has cap 0 in `resolveEntitlements` (e.g. `COMERCIAL`/`CONTABLE` on
`independiente`). The seat gate already returns 409 for cap 0, so "role not in plan" needs no special
case server-side. `GET /mi-empresa/cupos` reports `cap: 0` so the UI disables it with a clear hint.

### D6 — Validation shape
- `roles` is a non-empty array of the `RolEmpresa` enum (zod `z.array(z.nativeEnum(RolEmpresa)).min(1)`),
  deduped. On `POST` it is required; on `PATCH` it is optional (alongside the still-optional `activo`).
- The legacy `esAdminEmpresa` body field is removed from `createMiembroSchema`. (No external callers;
  only the `/equipo` page uses it.)

## Risks / tradeoffs

- **Partial UX on seat exhaustion**: if the admin picks two new roles and the second has no seat, the
  whole PATCH/POST rolls back with a 409 naming the failing role — the admin retries with a valid set.
  Chosen over silent partial application.
- **No "last admin" guard**: consistent with current behaviour; an empresa could in principle end up
  with zero admins by editing others (but not self). Flagged as a known limitation, not fixed here.

## Migration / rollback

None (no schema change). Rollback is a code revert; pre-existing role rows remain valid.
