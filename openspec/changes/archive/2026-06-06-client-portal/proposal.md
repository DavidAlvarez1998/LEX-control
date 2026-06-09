# Proposal: Client Portal (login separation + scoped company data)

## Intent
Let `USUARIO` users sign in to the tenant portal (`lex-control-client`, :3001) and see
**their own company's** data. Enforce strict portal separation so an `ADMIN` cannot sign
in to the client portal and a `USUARIO` cannot sign in to the admin panel, even though
both hit the same `POST /auth/login`.

## Scope

### In Scope
- **Portal separation**: `POST /auth/login` accepts an optional `audience` (`ADMIN` | `USUARIO`).
  If present and it does not match the user's `rol`, login is rejected with a generic 401.
- **Scoped company read**: `GET /mi-empresa` (USUARIO only) returns the caller's own
  `Empresa` plus its active contracted services, resolved from the token's `sub` — never
  from a client-supplied id.
- **Client portal UI** (already scaffolded): `/login`, session (`lib/auth`), `AuthGuard`.
- Wire client pages to real data: **Mi Cuenta** (profile + empresa + contracted services)
  and **Mis Servicios** (the contracted-services table).
- Expose `esAdminEmpresa` in the login session and show a derived **Acceso** label
  (Administrador / Usuario) in Mi Cuenta instead of the raw role value.
- Integration tests for audience separation and `GET /mi-empresa`.

### Out of Scope
- **Assigning services to a company** (so "Mis Servicios" shows data) — handled in a separate/parallel workstream.
- Billing computation (the `facturacion` page) — base + per-unit usage is a later change.
- Company self-administration by a USUARIO (`esAdminEmpresa` managing its own users).
- Password change / reset from inside the portal.

## Capabilities

### New Capabilities
- `portal-auth-separation`: audience-aware login so each portal only admits its own role.
- `client-portal-data`: scoped, ownership-safe read of the caller's company.

### Modified Capabilities
- `authentication`: `POST /auth/login` gains the optional `audience` discriminator.

## Approach
Keep data protection where it already is — per-endpoint `requireRole`. `audience` is a
**portal-UX guard** layered on top: it stops a valid user from "entering" the wrong SPA,
using the same generic 401 so it never leaks whether the credentials were valid. Company
data uses a **scoped endpoint** (`/mi-empresa`) that derives the company from `req.user.sub`,
so a USUARIO can never request another company's id. The existing ADMIN-only `/empresas`
routes are untouched.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/src/modules/auth/*` | Modified | `audience` in `loginSchema`; mismatch → 401 in router |
| `lex-control-api/src/modules/mi-empresa/*` | New | `GET /mi-empresa` (USUARIO-scoped) |
| `lex-control-api/src/app.ts` | Modified | mount `/mi-empresa` |
| `lex-control-client/src/app/login`, `lib/auth.ts`, `components/auth-guard.tsx` | New | portal session + guard |
| `lex-control-client/src/app/(dashboard)/cuenta/page.tsx` | Modified | real profile + empresa + services |
| `lex-control-client/src/app/(dashboard)/servicios/page.tsx` | Modified | real contracted-services table |
| tests | New | `tests/mi-empresa.test.ts` + audience cases in `tests/auth.test.ts` |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `audience` mistaken for real authorization | Med | Data is still guarded by `requireRole` per endpoint; audience is portal UX only |
| USUARIO without `empresaId` hits `/mi-empresa` | Low | Returns 404 "No tienes una empresa asociada" |

## Rollback Plan
Additive. Remove the `/mi-empresa` module + mount, drop `audience` from `loginSchema`/router,
and revert the two client pages. Existing login and ADMIN routes are unaffected.

## Success Criteria
- [ ] ADMIN→USUARIO portal and USUARIO→ADMIN portal logins are rejected (401); matching ones pass.
- [ ] A USUARIO sees only its own company via `GET /mi-empresa`; ADMIN gets 403; no token gets 401.
- [ ] Mi Cuenta and Mis Servicios render real data for a logged-in USUARIO.
