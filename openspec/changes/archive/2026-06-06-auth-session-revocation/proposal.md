# Proposal: Session Revocation on Credential Change + Account-State Enforcement

## Intent
Today a password "reset" is cosmetic, not enforced. When an admin calls `POST /usuarios/:id/reset-password`, the endpoint only issues a new `activationToken`/`activationExpires` — it never disables the account or invalidates the password hash. Combined with a stateless `requireAuth` (verifies only the JWT signature + 8h `exp`) and a login flow that ignores `activationToken`, this means after a "reset": (a) the user's live JWT keeps working for up to 8h, and (b) the OLD password still logs in. The `PENDIENTE` estado shown in the usuarios list (derived from `activationToken != null`) has no effect on authentication. This proposal makes the three account states (ACTIVO / PENDIENTE / INACTIVO) authoritative for auth and makes credential changes immediately revoke both the live session and the old credential, via server-side token invalidation.

## Scope

### In Scope
- Schema: add `Usuario.tokenVersion Int @default(0)`. Sync with `pnpm push` + `pnpm generate` (no migration file needed for this prototyping flow).
- JWT: add a `tv` claim carrying the user's `tokenVersion` at sign time (`JwtPayload`, `signToken`, `verifyToken`).
- `requireAuth` becomes stateful: after verifying the JWT, look the user up by id (PK) and reject with 401 if the user is missing, `activo = false`, has a pending `activationToken != null`, or the token's `tv` != the user's current `tokenVersion`.
- `POST /auth/login`: additionally reject with the generic `Credenciales inválidas` (401) when `activationToken != null`, so a PENDIENTE user cannot log in with the old password.
- Increment `tokenVersion` on: `POST /usuarios/:id/reset-password`, `POST /auth/set-password` (activation), and deactivation (`activo` true→false via `PATCH /usuarios/:id`).
- Integration tests covering live-session revocation, old-credential rejection, and state-gated login.

### Out of Scope
- Frontend logout UX beyond confirming a 401 redirects to login (noted as a minor follow-up).
- Transactional email delivery of activation/reset links.
- Role-aware activation link routing — covered by the separate `password-reset-all-roles` change.
- Caching the per-request user lookup (noted as a future optimization).

## Capabilities

### Modified Capabilities
- `authentication`: gains a **session-revocation / account-state enforcement** sub-capability. Authentication now depends on live DB state (`activo`, `activationToken`, `tokenVersion`) rather than the JWT signature alone, and credential changes revoke outstanding tokens immediately.

## Approach
Use server-side token invalidation (chosen over relying on the short 8h TTL alone, which cannot revoke an already-issued token). Each `Usuario` carries a monotonically increasing `tokenVersion`. A JWT embeds the `tv` it was signed with; any operation that should sever existing sessions bumps `tokenVersion`, so every previously-issued token now mismatches and is rejected on its next request.

- `signToken({ sub, rol, tv })` stamps the current version; `requireAuth` decodes it, fetches the user by PK, and enforces: exists, `activo`, `activationToken == null`, and `payload.tv === user.tokenVersion`. Any failure → `401`.
- `reset-password` and the `activo` true→false transition both increment `tokenVersion` (the former also sets `activationToken`, which independently blocks login until activation). `set-password` increments `tokenVersion` and clears the token so the freshly activated session is clean and any stale token is dead.
- Login adds the `activationToken != null` gate, so a pending account is unauthenticable even if its old bcrypt hash still verifies.

**Trade-off (stated honestly):** `requireAuth` now performs one indexed primary-key lookup per authenticated request (previously zero DB calls). This is acceptable at this app's scale; if request volume grows, the lookup can be cached (e.g. short-lived in-memory cache keyed by `sub`, invalidated on `tokenVersion` bump).

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/prisma/schema.prisma` | Modified | Add `Usuario.tokenVersion Int @default(0)` |
| `lex-control-api/src/modules/auth/auth.service.ts` | Modified | `JwtPayload.tv`; `signToken`/`verifyToken` carry `tv` |
| `lex-control-api/src/middleware/auth.ts` | Modified | `requireAuth` does DB-backed user + state + `tv` checks |
| `lex-control-api/src/modules/auth/auth.router.ts` | Modified | Login pending-gate (`activationToken != null`); `set-password` bumps `tokenVersion` |
| `lex-control-api/src/modules/usuarios/usuarios.router.ts` | Modified | `reset-password` and deactivate (PATCH) bump `tokenVersion` |
| `lex-control-api/tests/*` | New | Revocation, old-credential, and state-gate assertions |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Extra DB lookup per request adds latency | Med | Indexed PK lookup; small scale; caching available as a later optimization |
| `requireAuth` now async — sync-throw error path could be missed | Low | Wrap in `asyncHandler`/promise-aware path; tests assert 401 on each reject branch |
| All existing sessions invalidated when column defaults to 0 | Low | New tokens are signed post-deploy with `tv`; old tokens lacking `tv` fail the check and re-login (acceptable, short 8h TTL anyway) |
| Schema push on live DB | Low | Additive column with `@default(0)` — no data loss, backfills existing rows |
| Frontend doesn't gracefully handle new 401s | Low | Confirm 401 → redirect to login (minor follow-up) |

## Rollback Plan
Additive and reversible. To roll back: revert the code in `auth.service.ts`, `middleware/auth.ts`, `auth.router.ts`, and `usuarios.router.ts` (restoring the stateless `requireAuth` and the prior login flow), then drop the `tokenVersion` column via `pnpm push` + `pnpm generate`. Tokens already in circulation carry an unused `tv` claim and continue to validate under the reverted stateless check, so no forced logout occurs on rollback. Existing login/activation behavior returns to its prior state.

## Success Criteria
- [ ] `Usuario.tokenVersion` exists with `@default(0)`; client regenerated.
- [ ] JWTs carry a `tv` claim equal to the user's `tokenVersion` at sign time.
- [ ] After `reset-password`, the user's previously-issued JWT is rejected with 401 on the next request.
- [ ] After `reset-password`, logging in with the OLD password is rejected (account is PENDIENTE → login 401).
- [ ] Deactivating a user (`activo` true→false) immediately invalidates their live JWT (401).
- [ ] `set-password` (activation) bumps `tokenVersion` and clears the activation token; the new session works, stale tokens do not.
- [ ] `requireAuth` returns 401 when the user is missing, inactive, pending, or `tv`-mismatched.
- [ ] The three estados (ACTIVO / PENDIENTE / INACTIVO) are authoritative for authentication, not cosmetic.
- [ ] Integration tests cover live-session revocation, old-credential rejection, and state-gated login.
