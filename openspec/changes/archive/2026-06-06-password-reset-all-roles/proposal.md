# Proposal: Password reset for all roles (role-aware activation link)

## Intent
Let a platform `ADMIN` reset the password of **any** user, one by one, from the admin
**Usuarios** view — regardless of role (a company `USUARIO`, a company admin, or another
platform `ADMIN`). The existing per-user "Restablecer" already regenerates a single-use
activation link; the gap is that the link was hardcoded to the **client** portal, so it was
wrong for `ADMIN` users and the admin app had no `/activar` page.

## Scope

### In Scope
- **Role-aware activation link**: `POST /usuarios` (create) and `POST /usuarios/:id/reset-password`
  build the link for the portal that matches the target user's `rol` — `ADMIN → ADMIN_URL/activar`,
  `USUARIO → CLIENT_URL/activar`.
- **`ADMIN_URL`** env var (default `http://localhost:3000`).
- **Admin `/activar` page** (public) mirroring the client one, calling `POST /auth/set-password`.
- Tests for the role-aware link.

### Out of Scope
- **Automatic delivery** of the link (email / WhatsApp / SMS). Today the admin copies the
  link from the modal and shares it manually. Email is the recommended first automation.
- Temporary-password / forced-change-on-login flow (considered and rejected: more surface,
  and the admin would hold a live credential).
- Short dictate-by-phone activation codes (considered; deferred — would need email-scoped
  lookup + short expiry + lockout).

## Approach
`POST /auth/set-password` is already role-agnostic (it resolves the user by the token), so
no auth change is needed — only the **link target** must follow the user's role, and the
admin app needs its own activation page. Delivery stays manual (copy from the reset modal).

## Affected Areas
| Area | Impact |
|------|--------|
| `lex-control-api/src/config/env.ts` | New `adminUrl` (`ADMIN_URL`) |
| `lex-control-api/src/modules/usuarios/usuarios.router.ts` | `activationUrl(raw, rol)`; reset reads target `rol` |
| `lex-control-admin/src/app/activar/page.tsx` | New public activation page |
| `lex-control-api/tests/usuarios.test.ts` | Reset returns client link for USUARIO, admin link for ADMIN |

## Rollback Plan
Additive. Revert `activationUrl` to a single base, remove `ADMIN_URL` and the admin
`/activar` page. The reset endpoint and `set-password` are otherwise unchanged.

## Success Criteria
- [x] Reset of a USUARIO → link to `CLIENT_URL/activar`; reset of an ADMIN → `ADMIN_URL/activar`.
- [x] Admin `/activar` sets the password via `POST /auth/set-password` and points to `/login`.
- [x] Tests + tsc green; live smoke confirms the USUARIO link host.
