# Tasks: client-auth

## Review Workload Forecast
- **400-line budget risk: Medium** (~350–420 changed lines total).
- **Chained PRs recommended: Optional** — clean 2-slice split available.
- **Decision needed before apply: No** (proceed single-PR if under budget; otherwise split at the Phase boundary below).
- Suggested split if needed:
  - **Slice 1 (backend + shared expiry):** Phase 1 + Phase 4 (admin proactive expiry). Small, independently shippable.
  - **Slice 2 (client portal):** Phase 2 + Phase 3. Depends on Slice 1's backend `audience`.

## Phase 1 — Backend: 8h TTL + role-scoped login
- [x] 1.1 In `auth.service.ts`, change `TOKEN_TTL` from `"1d"` to `"8h"`.
- [x] 1.2 In `auth.schemas.ts`, add optional `audience: z.nativeEnum(Rol)` to `loginSchema`.
- [x] 1.3 In `auth.router.ts` `/login`, after password check, throw the generic `401` when `audience` is present and `usuario.rol !== audience`.
- [ ] 1.4 Manual check: ADMIN login with `audience:"CLIENTE"` → 401; CLIENTE with `audience:"CLIENTE"` → 200 with token; omitted audience → 200 for any rol.

## Phase 2 — Client app: session stack
- [x] 2.1 Add `lex-control-client/src/lib/auth.ts` mirroring admin's, with keys `lex_client_token` / `lex_client_user`, plus `getTokenExpiry` / `isExpired` helpers (see design).
- [x] 2.2 `lex-control-client/src/lib/api.ts`: merged the generic authenticated client (Bearer header, 401 → `clearSession` + redirect `/login`) with the existing public `setPassword` activation helper.
- [x] 2.3 Add `lex-control-client/src/components/auth-guard.tsx` with the proactive-expiry effect (see design).
- [x] 2.4 Add `lex-control-client/src/app/login/page.tsx` (email + password form; POST `/auth/login` with `audience:"CLIENTE"`; store session; redirect to dashboard; inline error on 401).
- [x] 2.5 Wrap `lex-control-client/src/app/(dashboard)/layout.tsx` with `<AuthGuard>`.
- [~] 2.6 `.env.local` blocked by sandbox perms; `api.ts` defaults to `http://localhost:4000`. User must add `NEXT_PUBLIC_API_URL` manually for non-default API URLs.

## Phase 3 — Client app: logout affordance
- [x] 3.1 Wired "Cerrar sesión" in the client **sidebar** (real user from `getUser()` + `clearSession()` + redirect, matching admin).

## Phase 4 — Admin app: proactive expiry parity
- [x] 4.1 Add `getTokenExpiry` / `isExpired` to `lex-control-admin/src/lib/auth.ts`.
- [x] 4.2 Update `lex-control-admin/src/components/auth-guard.tsx` to check `isExpired` on mount and arm the auto-logout `setTimeout` (see design).
- [x] 4.3 Make the admin login send `audience:"ADMIN"`.

## Phase 5 — Verify
- [x] 5.1 `pnpm --dir lex-control-api build` passes.
- [x] 5.2 `pnpm --dir lex-control-client build` and `pnpm --dir lex-control-admin build` pass.
- [ ] 5.3 Manual: create empresa + CLIENTE (admin) → set password via `/activar` → log in at client → reach dashboard.
- [ ] 5.4 Manual: ADMIN rejected at client login; CLIENTE rejected at admin login.
- [ ] 5.5 Manual: set a short TTL locally (e.g. `30s`), confirm idle tab auto-redirects to `/login` at expiry in both apps; restore `8h`.

## Notes
- Depends on `user-management` (activation flow) for a CLIENTE to have a usable password.
- `.env*` in `lex-control-api` is write-blocked per repo setup — TTL change is in source (`auth.service.ts`), not env, so unaffected.
