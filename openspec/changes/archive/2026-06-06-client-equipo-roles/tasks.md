# Tasks: Assign Empresa Roles from the Client Portal (multi-role)

> Multi-role decision: a member may hold several `RolEmpresa` at once; access = union; roles stay
> pure (no RBAC change). `ADMINISTRADOR` role replaces the standalone `esAdminEmpresa` checkbox.
> Builds on `foundations-roles-plans-clientes` (seat gate, mirror, `requirePermiso` all exist).

## Phase 0: Confirm scope
- [ ] 0.1 Multi-role (multi-select), not single-role — CONFIRMED with user
- [ ] 0.2 Roles pure, NO grant of comercial permisos to JURIDICO — CONFIRMED (supersedes earlier pick)
- [ ] 0.3 No schema change, no seed/RBAC change

## Phase 1: Backend — schemas
- [ ] 1.1 `mi-empresa.schemas.ts`: replace `esAdminEmpresa` in `createMiembroSchema` with
      `roles: z.array(z.nativeEnum(RolEmpresa)).min(1)` (dedupe). Keep `email`, `nombre`.
- [ ] 1.2 `mi-empresa.schemas.ts`: extend `updateMiembroSchema` to `{ activo?: boolean,
      roles?: RolEmpresa[] }` (at least one of the two present; `roles` deduped, may be empty? no —
      min(1) to avoid a roleless member). Keep `miembroIdParams`.

## Phase 2: Backend — POST (atomic create + assign all roles)
- [ ] 2.1 `mi-empresa.router.ts` `POST /usuarios`: in one `prisma.$transaction`, lock suscripción
      (`SELECT id FROM suscripciones WHERE empresaId=? FOR UPDATE`), create `Usuario`
      (`esAdminEmpresa = roles.includes(ADMINISTRADOR)`, `rol=USUARIO`, `empresaId=req.empresaId`,
      activation token, placeholder password), then per role: `assertSeatAvailable(tx,…)` + create
      `usuario_roles_empresa` row. Any seat 409 rolls back the whole tx (no orphan user).
- [ ] 2.2 Return `{ user (incl. roles), activationUrl }`. Map P2002→409 (duplicate email).

## Phase 3: Backend — PATCH (reconcile roles) + GET roles + cupos
- [ ] 3.1 `PATCH /usuarios/:id`: keep `activo` toggle. If `roles` present: guard "cannot remove
      ADMINISTRADOR from self" (400); in one tx lock suscripción, read current roles, deleteMany
      removed, seat-check + create added, set `esAdminEmpresa` to match ADMINISTRADOR in final set.
      Scope by `empresaId` (404 if not own empresa). 409 naming the role if a seat is full.
- [ ] 3.2 `GET /usuarios`: include each member's `roles: RolEmpresa[]` (select
      `usuarioRolEmpresa: { select: { rolEmpresa: true } }`, map to string[]).
- [ ] 3.3 `GET /mi-empresa/cupos` (new, equipoGuards): from `resolveEntitlements(req.empresaId)` +
      active-holder counts per role, return `[{ rol, cap (number|null), usados }]` (cap null =
      ilimitado, 0 = not in plan).

## Phase 4: Frontend — /equipo (client portal)
- [ ] 4.1 `equipo/page.tsx`: load `/mi-empresa/cupos`; `FormState` carries `roles: RolEmpresa[]`
      (default `["JURIDICO"]`). Replace the `esAdminEmpresa` Checkbox with a role multi-select
      (four checkboxes), each labeled with remaining seats (e.g. "Comercial — 1/1 usado") and
      DISABLED when `cap===0` (not contracted) or `usados>=cap` (full). Require ≥1 role on submit
      (red asterisk; block API call if none, per project form rule).
- [ ] 4.2 Show each member's roles as badges in the team list.
- [ ] 4.3 Per-member "Editar roles" action → modal pre-checked with current roles → PATCH `{ roles }`;
      hide/disable removing one's own ADMINISTRADOR; surface 409 seat errors inline.
- [ ] 4.4 Update `Miembro`/types; drop the `esAdminEmpresa`-only UI affordances (admin status now = has
      ADMINISTRADOR role). Keep activate/deactivate + resend link unchanged.

## Phase 5: Tests / Verify
- [ ] 5.1 `tests/mi-empresa-usuarios.test.ts` (extend): create with `roles:["JURIDICO","COMERCIAL"]`
      → both assigned, `esAdminEmpresa=false`; create with `["ADMINISTRADOR"]` → `esAdminEmpresa=true`;
      create with `["COMERCIAL"]` on a basic-plan empresa → 409 (no seat), no user created (no orphan);
      create with `[]` → 400.
- [ ] 5.2 PATCH reconcile: add a role (seat ok) → assigned; remove a role → removed + esAdminEmpresa
      synced; remove own ADMINISTRADOR → 400; seat-full add → 409 and no partial change; cross-empresa
      id → 404.
- [ ] 5.3 `GET /usuarios` includes `roles`; `GET /cupos` returns cap/usados per role.
- [ ] 5.4 `pnpm --dir lex-control-api test` green; `pnpm --dir lex-control-api build` clean;
      client `tsc --noEmit` / `pnpm --dir lex-control-client build` clean.
