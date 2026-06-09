# Proposal — client-role-based-nav

## Why

After `client-equipo-roles` let the empresa admin assign `RolEmpresa` (JURIDICO / COMERCIAL /
CONTABLE / ADMINISTRADOR), the **client portal frontend still gated everything by
`esAdminEmpresa`** — the sidebar hid items only with `adminOnly`, and module pages used
`AdminEmpresaGuard`. Consequences:

- A **CONTABLE** user could not open `/contable` (the guard rejected them) and could not see it in
  the sidebar in a meaningful way.
- A non-admin user (e.g. a JURIDICO+COMERCIAL "abogado que vende") **saw `/contable` in the sidebar**
  (it had no `adminOnly`), clicked it, and the page **crashed** with `ApiError: No autorizado` — the
  `contableApi.cuentas()` lookup lacked the `.catch` its siblings had, and the lookups `useEffect`
  fired before `AdminEmpresaGuard` could redirect.

The roles we enabled had no effect on what the user actually sees or can reach.

## What changes

Drive client-portal visibility and access by `RolEmpresa`, not just `esAdminEmpresa`:

- **Login returns roles**: `POST /auth/login` includes `user.roles` (the caller's `RolEmpresa[]`).
  Client `AuthUser` stores them.
- **Sidebar by role**: `NavItem` gains optional `roles`. An item shows if it has no restriction, OR
  the user is `esAdminEmpresa`, OR the user holds one of the item's roles. Mapping:
  `/clientes`→COMERCIAL, `/procesos`→JURIDICO, `/contable`+`/facturacion`→CONTABLE; `/servicios` and
  `/equipo` stay `adminOnly`; `/`, `/soporte`, `/cuenta` stay public.
- **Page guards by role**: new `RolEmpresaGuard roles={[...]}` (allows `esAdminEmpresa` or any listed
  role; redirects otherwise). Applied to `/contable` and `/facturacion` (CONTABLE), `/clientes`
  (COMERCIAL), `/procesos` (JURIDICO). `/servicios` keeps `AdminEmpresaGuard`.
- **Crash fix**: `/contable` no longer fetches its lookups unless the user is `esAdminEmpresa` or
  CONTABLE (matching the guard), so an unauthorized landing never triggers the 403 crash.

The API remains the real authority (`requirePermiso` already enforces module + RBAC); this is the UI
catching up to it.

## Out of scope

- Sub-routes (`/procesos/nuevo`, `/procesos/[id]`, `/clientes/[id]`) — reached from guarded lists;
  the API enforces their data access. Can be guarded later if needed.
- Changing the RBAC matrix or what each role can do (unchanged).
- Platform admin app.

## Rollback plan

Code-only, no schema/data change. Rollback = revert the login response, `AuthUser`, `nav.tsx`,
`sidebar.tsx`, the new `RolEmpresaGuard`, and the page guard swaps. Note: because `user.roles` is
added to the stored session, **users must re-login** after deploy for role-based visibility to take
effect (sessions created before the change have no `roles`; they fall back to base items + whatever
`esAdminEmpresa` allows).
