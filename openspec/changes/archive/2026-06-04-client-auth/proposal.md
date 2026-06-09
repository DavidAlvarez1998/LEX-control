# Proposal: Client Portal Login + Strict Role Separation + Proactive 8h Session Expiry

## Intent
Users that admins create inside an `Empresa` (rol `CLIENTE`) must be able to **log in to the client app** (`lex-control-client`, :3001) with their email and password. At the same time, **sessions in both frontends must expire** predictably: an absolute 8-hour JWT lifetime that the frontend enforces **proactively** (auto-logout the moment the token expires, not only on the next API call). Login must be **role-scoped**: the client app only accepts `CLIENTE`, the admin app only accepts `ADMIN`.

## Background / Current State
- The Express API already exposes `POST /auth/login` (issues a JWT, currently `1d` TTL) and works for any `Usuario` regardless of `rol`. `requireAuth`/`requireRole` middleware already exist.
- The **admin** app already has a full session stack: `lib/auth.ts` (localStorage), `lib/api.ts` (sends Bearer, reacts to 401), `components/auth-guard.tsx`, `app/login/page.tsx`.
- The **client** app has **none** of this — all pages are static placeholders, and it does not depend on the API client.
- How a CLIENTE gets a usable password is **already covered** by the `user-management` change (activation-link flow → `/activar`). This change consumes that; it does not re-define password creation.

## Scope

### In Scope
- **Backend (`lex-control-api`)**
  - Lower JWT TTL from `1d` to `8h` (absolute lifetime).
  - Make login role-aware: `POST /auth/login` accepts an optional expected audience (`audience: "ADMIN" | "CLIENTE"`) and returns `401` when the user's `rol` does not match. (Defense-in-depth on top of existing `requireRole` route guards.)
- **Client app (`lex-control-client`)** — mirror the admin session stack:
  - `lib/auth.ts` (token + user in localStorage, keys `lex_client_*`).
  - `lib/api.ts` (Bearer header, 401 → clear session + redirect to `/login`).
  - `components/auth-guard.tsx` protecting `(dashboard)`.
  - `app/login/page.tsx` (email + password form; rejects non-`CLIENTE`).
  - Wire `(dashboard)/layout.tsx` to use the guard.
  - `.env.local` example with `NEXT_PUBLIC_API_URL`.
- **Both frontends — proactive expiry**
  - Shared helper to read the JWT `exp` claim (decode only, no verification).
  - On guard mount: if `exp` is past → clear + redirect to `/login`.
  - Schedule a timer for the remaining lifetime → auto-logout exactly at expiry.

### Out of Scope
- Sliding / idle-timeout sessions and refresh tokens (documented as a future phase).
- Server-side session revocation / "log out everywhere" (would need stateful sessions or a token blocklist).
- Password creation / activation links (owned by `user-management`).
- Client-app data pages wired to real data (separate change).
- ADMIN password reset.

## Capabilities

### New Capabilities
- `client-portal-auth`: the client app's login, session storage, route guard, and role gate.
- `session-expiry`: proactive, absolute-lifetime session expiry shared by both frontends.

### Modified Capabilities
- `authentication`: shorten JWT TTL to 8h; role-scoped login via `audience`.

## Approach
Reuse the admin pattern verbatim in the client app (same `lib/auth` + `lib/api` + `AuthGuard` shape) so both stay consistent and easy to maintain — only the storage keys and the role gate differ. Role separation is enforced in two layers: the API rejects a mismatched `audience` at login, and each frontend refuses to store a session whose `rol` is not its own. Proactive expiry is achieved by base64url-decoding the JWT payload to read `exp` (no signature check needed client-side — the API remains the source of truth) and arming a `setTimeout`; this upgrades the current purely-reactive 401 handling without new backend infrastructure.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/src/modules/auth/auth.service.ts` | Modified | `TOKEN_TTL` 1d → 8h |
| `lex-control-api/src/modules/auth/auth.schemas.ts` | Modified | optional `audience` on `loginSchema` |
| `lex-control-api/src/modules/auth/auth.router.ts` | Modified | reject `rol`/`audience` mismatch with 401 |
| `lex-control-client/src/lib/auth.ts` | New | session storage (`lex_client_*`) + `exp` helper |
| `lex-control-client/src/lib/api.ts` | New | HTTP client, 401 handling |
| `lex-control-client/src/components/auth-guard.tsx` | New | route guard + proactive expiry |
| `lex-control-client/src/app/login/page.tsx` | New | login form, CLIENTE-only |
| `lex-control-client/src/app/(dashboard)/layout.tsx` | Modified | wrap with guard |
| `lex-control-admin/src/lib/auth.ts` + `components/auth-guard.tsx` | Modified | add proactive `exp` check/timer |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| CLIENTE has no password yet (activation not applied) | High | Depends on `user-management`; login shows clear "credenciales inválidas". Document the dependency. |
| Reading `exp` client-side is spoofable | Low | It's only UX; real authority is the API verifying the signature. A forged `exp` still fails server-side. |
| Clock skew → premature/late auto-logout | Low | Absolute 8h tolerates minutes of skew; API is authoritative on 401. |
| Lowering TTL logs admins out sooner | Low | Intended; communicate the 8h policy. |

## Rollback Plan
Additive on the client side (new files) and a one-line TTL revert on the backend. Revert by: restoring `TOKEN_TTL` to `1d`, removing the `audience` check, and deleting the new client `lib/`, `components/auth-guard.tsx`, and `app/login/` (plus reverting the `(dashboard)/layout.tsx` wrap). Admin proactive-expiry changes are self-contained and revertible independently.

## Success Criteria
- [ ] A CLIENTE with a set password logs in at the client app and reaches the dashboard.
- [ ] An ADMIN cannot log in at the client app (and a CLIENTE cannot log in at the admin app) — clear rejection, no session stored.
- [ ] Tokens expire 8h after login; an idle tab is auto-redirected to `/login` at expiry without any API call.
- [ ] An expired/missing token on any protected client route redirects to `/login`.
- [ ] Admin app gains the same proactive auto-logout behavior.
