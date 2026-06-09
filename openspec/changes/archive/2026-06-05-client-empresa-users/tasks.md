# Tasks: Empresa Admin Manages Their Team (Client Portal)

> APPLIED 2026-06-05. Q1 = ALLOW esAdminEmpresa on create; Q2 = ALL lifecycle actions
> (activate/deactivate + resend activation link). All phases in scope.

## Phase 0: Confirm scope
- [x] 0.1 Q1: allow `esAdminEmpresa` checkbox on create → **ALLOW**
- [x] 0.2 Q2: list+create + activate/deactivate + resend activation link → **ALL**

## Phase 1: Backend — endpoints (core)
- [x] 1.1 `mi-empresa.schemas.ts` (new): `createMiembroSchema = { nombre, email, esAdminEmpresa? }`
      (+ `updateMiembroSchema = { activo }`, `miembroIdParams`). Does NOT accept `rol`/`empresaId`.
- [x] 1.2 `mi-empresa.router.ts`: `GET /usuarios` — `requireAuth` + `requireRole(USUARIO)` +
      `requireEmpresaAdmin`; list `where: { empresaId: req.empresaId }` with `PUBLIC_SELECT` +
      derived `estado`; strip `activationToken`.
- [x] 1.3 `mi-empresa.router.ts`: `POST /usuarios` — create with `rol=USUARIO`,
      `empresaId=req.empresaId`, activation token (48h), placeholder password; return
      `{ user, activationUrl }` (client portal). Map P2002→409.
- [x] 1.4 Shared helpers extracted to `modules/usuarios/usuarios.shared.ts`
      (`ACTIVATION_TTL_MS`, `PUBLIC_SELECT`, `activationUrl`, `deriveEstado`); reused by
      `usuarios.router.ts` and `mi-empresa.router.ts`.

## Phase 2: Frontend — client portal
- [x] 2.1 `lib/nav.tsx`: add `{ href: "/equipo", label: "Equipo", adminOnly: true, icon }`; extend
      `NavItem` with optional `adminOnly`.
- [x] 2.2 `components/sidebar.tsx`: filter `NAV_ITEMS` by `user.esAdminEmpresa` for `adminOnly`.
- [x] 2.3 `app/(dashboard)/equipo/page.tsx`: list team (estado badges) + "Invitar usuario" modal
      (nombre*, email*, esAdminEmpresa checkbox); on create, show the activation link to copy.
      Required-field validation on submit (red asterisk; block API call if empty).
- [x] 2.4 Guard the page for non-admins (EmptyState "Acceso restringido") — API remains authority.

## Phase 3: Tests / Verify (core)
- [x] 3.1 `tests/mi-empresa-usuarios.test.ts`: 403 non-admin; 403 platform ADMIN; 201 valid create
      with forced rol/empresa; body rol/empresaId ignored; 400 invalid; 409 duplicate; list scoped +
      no secrets.
- [x] 3.2 `pnpm --dir lex-control-api test` green (98 tests, 15 new); client `tsc --noEmit` clean.

## Phase 4 (Q2 = activate/deactivate)
- [x] 4.1 `PATCH /mi-empresa/usuarios/:id` (own empresa only via `updateMany where empresaId`) →
      toggle `activo` with `tokenVersion increment` on deactivate (revoke sessions); 404 if not in
      own empresa; cannot self-deactivate (400).
- [x] 4.2 UI toggle (Activar/Desactivar with confirm) + tests.

## Phase 5 (Q2 = resend link)
- [x] 5.1 `POST /mi-empresa/usuarios/:id/activation` → regenerate token + bump tokenVersion; return
      fresh `activationUrl` (client portal). Own empresa only (404 otherwise).
- [x] 5.2 UI "Reenviar enlace" action (shown for PENDIENTE) + tests.
