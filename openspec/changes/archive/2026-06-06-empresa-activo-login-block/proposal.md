# Proposal: Deactivating an Empresa Blocks Its Users' Access

## Intent
`Empresa.activo` exists in the schema and is editable from the admin form (the "Activa"
checkbox), but it is **inert** — nothing reads it. Login only checks `Usuario.activo`, and the
auth middleware never looks at the company. So marking a company inactive does nothing. This
change makes `Empresa.activo = false` actually **block every user of that company**: they cannot
log in, and any live session is revoked on the next request. The admin form warns before
deactivating, since the effect is broad.

## Scope

### In Scope
- `POST /auth/login`: reject (generic `401`) when the user belongs to an Empresa whose
  `activo = false`. Platform ADMINs (no empresa) are unaffected.
- `requireAuth` middleware: reject (`401`) on every request when the authenticated user's Empresa
  is inactive — so deactivation takes effect immediately, not just on the next login (consistent
  with how `auth-session-revocation` already re-checks account state per request).
- Admin empresa form: when the admin **unchecks "Activa"** on an empresa that was active, show a
  confirmation alert stating that all of that company's users will be blocked from signing in;
  abort the save if they cancel. Also show an inline warning while the box is unchecked.

### Out of Scope
- A self-service way for clients to reactivate (admin-only, via the same form).
- Any UI in the client portal for the blocked state (they simply get the generic 401 at login).
- Filtering/badging inactive empresas in the admin list (possible follow-up; not required here).
- Bumping `tokenVersion` on deactivation — the per-request middleware check already revokes live
  sessions, so no token-version change is needed.

## Capabilities

### Modified Capabilities
- `authentication`: login and the auth middleware additionally deny access when the user's Empresa
  is inactive. (Existing `Usuario.activo`, audience, and token-version rules are unchanged.)

## Approach
Login already loads `usuario.empresa` (added for the sidebar's company name); extend that
`include` to also select `activo` and add one guard returning the same generic `invalidas` 401.
In `requireAuth`, add `empresa: { select: { activo: true } }` to the existing user lookup and add
`(user.empresa && !user.empresa.activo)` to the revoke condition — reusing the same generic 401.
The admin form compares the original `activo` (from the loaded list) with the form value; a true→
false transition triggers a `confirm()` before `guardar()` proceeds.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/src/modules/auth/auth.router.ts` | Modified | `include` empresa `activo`; block login when empresa inactive |
| `lex-control-api/src/middleware/auth.ts` | Modified | Select empresa `activo`; revoke per request when empresa inactive |
| `lex-control-admin/src/app/(dashboard)/empresas/page.tsx` | Modified | Confirm alert on deactivation + inline warning |
| `lex-control-api/tests/auth.test.ts` | Modified | Cover login 401 for inactive empresa; admin still 200 |
| `lex-control-api/tests/session-revocation.test.ts` | Modified | Cover middleware 401 for inactive empresa |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Locking out an entire company by accident | Med | Confirm alert + inline warning before saving the deactivation |
| ADMINs (no empresa) wrongly blocked | Low | Guard is `empresa && !empresa.activo`; null empresa → not blocked (tests cover) |
| Leaking that credentials were valid | Low | Reuse the same generic `401 "Credenciales inválidas"` message |
| Reactivation doesn't restore access | Low | The checks read live state; setting `activo = true` restores access immediately |

## Rollback Plan
Remove the two backend guards (login + middleware) and the form confirm/warning. `Empresa.activo`
returns to being an inert flag. No DB/schema change (the column already exists). Additive and
reversible.

## Dependencies
- Existing `Empresa.activo` column and the admin empresa create/edit form.
- The empresa `include` already added to login for the company-name feature.

## Success Criteria
- [ ] A user of an inactive empresa gets `401` at `/auth/login`; an ADMIN still gets `200`.
- [ ] A user with a live token whose empresa is then deactivated gets `401` on the next request.
- [ ] Reactivating the empresa restores both login and request access with no other action.
- [ ] The admin form alerts before deactivating and aborts if cancelled.
- [ ] `pnpm --dir lex-control-api test` passes (existing + new cases).
