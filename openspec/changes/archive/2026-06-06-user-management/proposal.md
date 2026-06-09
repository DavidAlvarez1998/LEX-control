# Proposal: User Management + Activation-Link Password Flow

## Intent
Admins create company users (`USUARIO`) but must not know their passwords. Each new user receives a one-time **activation link** to set their own password. Admins also need a `usuarios` screen to list users and reset their access (regenerate the link). No transactional email yet → the link is shown to the admin to share manually.

## Scope

### In Scope
- Schema: add `activationToken` (hashed, unique) + `activationExpires` to `Usuario`. Push to DB.
- Backend endpoints (all ADMIN except set-password):
  - `GET /usuarios` (list, optional `?empresaId`)
  - `POST /usuarios` (create in an empresa → returns activation link)
  - `PATCH /usuarios/:id` (nombre, rol, activo, esAdminEmpresa)
  - `POST /usuarios/:id/reset-password` (regenerate activation link)
  - `POST /auth/set-password` (PUBLIC, with token → sets password, activates)
- Admin UI `usuarios/`: list (empresa, rol, estado), create (modal → show copyable link), reset-password (show new link), activate/deactivate.
- Activation page in the **client app** (`/activar?token=…`): user sets their password.
- Integration tests for the new backend endpoints.

### Out of Scope
- Automatic email delivery of the link (manual share for now; wire later).
- Company self-admin (`esAdminEmpresa` managing their own users).
- Password reset for ADMIN users (separate concern).
- Full client-app login (only the public activation page is added here).

## Capabilities

### New Capabilities
- `user-management`: admin CRUD over `Usuario` + activation-link issuance/reset.
- `account-activation`: public token-based password creation.

### Modified Capabilities
- `authentication`: add token-based `set-password`; login still requires a set password.

## Approach
Follow existing module convention (`modules/usuarios/{usuarios.router,usuarios.schemas}`). Activation token = random 32 bytes; store its **SHA-256 hash** in `activationToken` (high-entropy → sha256, not bcrypt) and hand the raw token to the admin. `set-password` hashes the raw token, looks it up, checks expiry, sets a bcrypt password, clears the token. A user with a pending token and no password cannot log in (bcrypt compare fails). Estado derived: `activo=false` → Inactivo; token pending → "Pendiente"; else "Activo".

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/prisma/schema.prisma` | Modified | `Usuario.activationToken`, `activationExpires` |
| `lex-control-api/src/modules/usuarios/*` | New | router + schemas |
| `lex-control-api/src/modules/auth/*` | Modified | `POST /auth/set-password` |
| `lex-control-admin/src/app/(dashboard)/usuarios/page.tsx` | Modified | real list/create/reset UI |
| `lex-control-client/src/app/activar/page.tsx` | New | public set-password page |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Token leakage via manual sharing | Med | Short expiry (48h), single-use, hashed at rest |
| Admin sees link (could self-activate) | Low | Acceptable for MVP; audit later; email delivery removes it |
| Schema push on live DB | Med | Additive nullable columns only — no data loss |

## Rollback Plan
Additive change. Revert by removing the new modules/pages and dropping the two nullable columns. Existing auth/login unaffected.

## Success Criteria
- [ ] Admin creates a user → gets a copyable activation link; user has no usable password yet.
- [ ] Opening the link lets the user set a password and then log in.
- [ ] Expired/used/invalid token → clear error, no password set.
- [ ] Admin `usuarios` page lists users by empresa and can reset a user's link.
- [ ] `GET /usuarios` and writes require `ADMIN`; `set-password` is public.
