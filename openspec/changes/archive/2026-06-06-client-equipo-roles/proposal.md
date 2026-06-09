# Proposal — client-equipo-roles

## Why

The company-roles foundation (`foundations-roles-plans-clientes`) already ships everything needed to
run a despacho on four roles — the `RolEmpresa` enum (`ADMINISTRADOR`, `JURIDICO`, `CONTABLE`,
`COMERCIAL`), a seeded RBAC matrix, per-user `usuario_roles_empresa` assignments, the seat gate
(`assertSeatAvailable`/`assignRole`/`removeRole`), and `requirePermiso` enforcement on the comercial
and contable modules. The schema even allows a user to hold **several** roles at once
(`@@unique([usuarioId, rolEmpresa])`), and `requireAuth` resolves `req.rolesEmpresa` as the union.

But the **client portal cannot reach any of it**. When an empresa admin creates a teammate in
`/equipo`, `mi-empresa.router.ts` hard-codes the role:

```ts
const rolEmpresa = esAdminEmpresa ? RolEmpresa.ADMINISTRADOR : RolEmpresa.JURIDICO;
```

So `COMERCIAL` and `CONTABLE` are **orphaned**: defined, permissioned, seat-quoted — but impossible
to assign from the UI. There is also no way to change a member's roles after creation (`PATCH` only
toggles `activo`). The result: a firm can never give anyone the comercial funnel or the accounting
module, even on a plan that contracts those módulos.

## What changes

Let the empresa admin assign **one or more** `RolEmpresa` to each teammate from `/equipo`, honoring
the plan's per-role seats. Roles stay **pure** (no permission is moved between roles); a lawyer who
also sells simply holds `JURIDICO + COMERCIAL`.

- **`POST /mi-empresa/usuarios`** accepts `roles: RolEmpresa[]` (≥1) instead of the `esAdminEmpresa`
  boolean. The member is created and **all** chosen roles are assigned in one transaction, each
  seat-checked; if any role has no seat (or is not in the plan, e.g. `COMERCIAL` on `independiente`,
  whose cap is 0), nothing is created (no orphan user). `esAdminEmpresa` is derived from whether
  `ADMINISTRADOR` is among the roles (the existing mirror).
- **`PATCH /mi-empresa/usuarios/:id`** gains an optional `roles: RolEmpresa[]` that **reconciles** a
  member's role set (assign the missing, remove the extra) in one transaction, seat-checking each
  addition and keeping `esAdminEmpresa` in sync with `ADMINISTRADOR`. The existing optional `activo`
  toggle is unchanged. An admin MUST NOT remove `ADMINISTRADOR` from **their own** account.
- **`GET /mi-empresa/usuarios`** returns each member's `roles: RolEmpresa[]`.
- **`GET /mi-empresa/cupos`** (new) returns, per role, the plan `cap` and `usados` (active holders)
  so the UI can show availability and disable roles with no seat / not in the plan.
- **`/equipo` UI**: the "Administrador de la empresa" checkbox is replaced by a **multi-select of
  roles** (Administrador, Jurídico, Contable, Comercial) on the create modal and on a new "Editar
  roles" action per member, each option showing its remaining seats and disabled when full or not
  contracted. At least one role is required on create.

**No schema change. No RBAC/seed change.** Selecting `ADMINISTRADOR` is now the canonical way to make
someone a company admin (it mirrors `esAdminEmpresa`, which remains authoritative for team
management).

## Out of scope

- Changing what each role can do (RBAC matrix stays as seeded; roles remain pure).
- Platform-side commercial users (`Rol.COMERCIAL`), managed in the admin app `/usuarios` — unrelated.
- Email delivery of activation links (still copy-the-link, as today).
- Any change to the comercial/contable module behaviour itself.

## Rollback plan

Additive/behavioural only, no migration. Rollback = revert `mi-empresa.router.ts`,
`mi-empresa.schemas.ts`, the new `GET /cupos` route, and the `/equipo` page to restore the
`esAdminEmpresa`-only flow. Existing `usuario_roles_empresa` rows created in the meantime stay valid
(they are the same shape the foundation already writes); the reverted POST simply goes back to
assigning a single ADMINISTRADOR/JURIDICO seat. Nothing else depends on the new endpoints.
