# Proposal: Empresa Admin Manages Their Team (Client Portal)

> STATUS: APPLIED 2026-06-05. Q1 = ALLOW esAdminEmpresa on create; Q2 = ALL lifecycle actions
> (activate/deactivate + resend activation link). Backend, client UI, and tests done.

## Intent
A client company (`Empresa`) has users with `esAdminEmpresa = true` who should be able to manage
the other users of **their own company** — concretely, invite/create the company's lawyers
(`abogados`, i.e. `Usuario` with `rol = USUARIO`). Today only the platform `ADMIN` can create
users (via `POST /usuarios`), and the client portal has no team screen. This change adds an
empresa-scoped team capability so an empresa admin can see their team and create new members from
the **client portal** (port 3001), without ever touching other companies or platform admins.

## Field Validation (what a new member needs)
The `Usuario` model only carries these human-set fields: `nombre`, `email`, `rol`, `empresaId`,
`esAdminEmpresa`, `activo` (no phone/other). So creating a lawyer requires:

| Field | Source | Rule |
|-------|--------|------|
| `nombre` | form | required, trimmed, min 1 |
| `email` | form | required, valid email, unique (409 on duplicate) |
| `esAdminEmpresa` | form (optional) | boolean, default `false` — **OPEN Q1** below |
| `rol` | **forced server-side** | always `USUARIO` (an empresa admin MUST NOT create platform `ADMIN`s) |
| `empresaId` | **forced server-side** | always the requester's own `req.empresaId` (never chosen by the client) |
| `password` | not set | defined by the new user via the activation link (same flow as admin-created users) |

So the client request body is just `{ nombre, email, esAdminEmpresa? }`.

## Scope

### In Scope
- New empresa-scoped endpoints (resolve empresa from the token, never from a client-supplied id),
  guarded by `requireAuth` + `requireRole(USUARIO)` + `requireEmpresaAdmin`:
  - `GET /mi-empresa/usuarios` — list the company's users with derived `estado`
    (ACTIVO / PENDIENTE / INACTIVO), excluding secrets.
  - `POST /mi-empresa/usuarios` — create a member; force `rol=USUARIO` and `empresaId=req.empresaId`;
    return the user + `activationUrl` (client portal `/activar?token=...`) to share.
- Client portal "Equipo" page (empresa-admin only) listing the team and a create form
  (nombre*, email*, optional esAdminEmpresa), composing the shared UI primitives; shows the
  activation link after creating.
- Nav: add an "Equipo" item visible only when `user.esAdminEmpresa` (filter `NAV_ITEMS` in the
  client sidebar).

### Out of Scope (unless chosen in Open Q2)
- Activate/deactivate a teammate; resend/regenerate an activation link; editing a member.
- Any change to the platform admin's `/usuarios` flow (unchanged).
- Email delivery of the activation link (none exists yet — the link is shown to copy, as today).

## Open Questions (confirm next session)
- **Q1 — `esAdminEmpresa` field:** may the empresa admin grant company-admin rights to a new
  member (a checkbox), or are all created as plain `USUARIO` (only the platform can grant)?
  Security trade-off: allowing it lets an admin mint more admins. *Recommended default: allow it,
  but it's a real decision.*
- **Q2 — management actions beyond create:** (a) list + create only; (b) + activate/deactivate;
  (c) + resend activation link. Phases 4–5 below are gated on this.

## Capabilities

### New Capabilities
- `empresa-team`: an empresa admin manages the users of their own company from the client portal
  (list + create now; optional lifecycle actions per Q2).

### Modified Capabilities
- None required for the core. (Reuses `authentication` middleware and the activation flow from
  `user-management`; their existing requirements are unchanged.)

## Approach
Add the routes to the existing `mi-empresa` module (already the empresa-scoped surface), reusing
`generateActivationToken`, the 48h TTL, the `PUBLIC_SELECT`/`estado` derivation, and the
duplicate-email handling from `usuarios.router.ts`. Guard with the already-defined-but-unused
`requireEmpresaAdmin` middleware. The empresa is always `req.empresaId`; the client cannot target
another company. The client page mirrors the admin `usuarios` page but scoped, and the nav item is
gated on `esAdminEmpresa`.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/src/modules/mi-empresa/mi-empresa.router.ts` | Modified | Add `GET`/`POST /mi-empresa/usuarios` (+ optional lifecycle per Q2) |
| `lex-control-api/src/modules/mi-empresa/*.schemas.ts` | New | `createMiembroSchema` ({ nombre, email, esAdminEmpresa? }) |
| `lex-control-api/src/middleware/auth.ts` | Reused | `requireEmpresaAdmin` (already exists) |
| `lex-control-client/src/app/(dashboard)/equipo/page.tsx` | New | Team list + create form (empresa-admin only) |
| `lex-control-client/src/lib/nav.tsx` + `components/sidebar.tsx` | Modified | "Equipo" item gated on `esAdminEmpresa` |
| `lex-control-api/tests/mi-empresa-usuarios.test.ts` | New | Authz + create/validate/duplicate/scoping |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cross-tenant leak (managing another empresa's users) | Med | empresa always from `req.empresaId`; never accept an empresaId from the client |
| Privilege escalation to platform ADMIN | Med | Force `rol = USUARIO` server-side; ignore any `rol` in the body |
| Non-admin USUARIO reaching the endpoints/page | Med | `requireEmpresaAdmin` on the API; nav + page guard on `esAdminEmpresa` (UI is convenience only, API is authority) |
| Duplicate email | Low | Catch P2002 → 409, mirroring `/usuarios` |

## Rollback Plan
Additive. Remove the `mi-empresa/usuarios` routes + schema, the client "Equipo" page, and the nav
item. No DB/schema change (uses existing `Usuario` fields). Fully reversible.

## Dependencies
- Activation flow + `generateActivationToken` (`user-management`).
- `requireEmpresaAdmin`, `req.empresaId` (`middleware/auth.ts`).
- Client `AuthUser.esAdminEmpresa` (already present in `lex-control-client/src/lib/auth.ts`).

## Success Criteria
- [ ] An empresa admin lists ONLY their own company's users with correct `estado`.
- [ ] An empresa admin creates a USUARIO in their own empresa and gets an activation link to share.
- [ ] `rol`/`empresaId` cannot be overridden by the client body (no ADMIN, no cross-tenant).
- [ ] A non-admin USUARIO gets 403 on the endpoints and does not see the "Equipo" nav/page.
- [ ] `pnpm --dir lex-control-api test` passes (new authz/scoping cases).
