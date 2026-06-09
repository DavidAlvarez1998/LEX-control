# Tasks: Role-based nav & access in the client portal

## Phase 1: API
- [x] 1.1 `auth.router.ts` login: include `rolesEmpresa` in the query; return `user.roles` (RolEmpresa[]).
- [x] 1.2 Fix auth tests (mock returns `rolesEmpresa`; assert `user.roles`).

## Phase 2: Client session + nav
- [x] 2.1 `lib/auth.ts`: add `roles?: string[]` to `AuthUser`.
- [x] 2.2 `lib/nav.tsx`: add `roles?: string[]` to `NavItem`; set /clientes=COMERCIAL,
      /procesos=JURIDICO, /contable=CONTABLE, /facturacion=CONTABLE; keep /servicios + /equipo adminOnly.
- [x] 2.3 `components/sidebar.tsx`: filter by `puedeVer` (adminOnly→admin; roles→admin or has-role; else all).

## Phase 3: Page guards
- [x] 3.1 New `components/rol-empresa-guard.tsx` (`RolEmpresaGuard roles={[...]}`: admin or any role).
- [x] 3.2 `/contable` + `/facturacion`: AdminEmpresaGuard → RolEmpresaGuard(["CONTABLE"]).
- [x] 3.3 `/clientes`: wrap in RolEmpresaGuard(["COMERCIAL"]); `/procesos`: RolEmpresaGuard(["JURIDICO"]).
- [x] 3.4 `/contable` cargarLookups: skip unless esAdminEmpresa or CONTABLE (crash fix).

## Phase 4: Verify
- [x] 4.1 API build + 221 tests green.
- [x] 4.2 Client `next build` clean.
- [ ] 4.3 Runtime smoke: re-login as a CONTABLE-only and a COMERCIAL-only user; confirm sidebar +
      access; confirm a JURIDICO user no longer sees/reaches /contable.
