# Tasks: Auth Session Revocation + Account State Enforcement

## Review Workload Forecast
| Field | Value |
|-------|-------|
| Estimated changed lines | 150–250 |
| 400-line budget risk | Low |
| Suggested split | Single batch chain (backend-only); no UI split required |

Decision needed before apply: No
Chained PRs recommended: No (one focused backend change in `lex-control-api`)
Chain strategy: single PR
400-line budget risk: Low

## Batch 1 — Schema
- [x] 1.1 `prisma/schema.prisma`: add `Usuario.tokenVersion Int @default(0)`
- [x] 1.2 Apply: `pnpm push` then `pnpm generate` (typed client matches new field)

## Batch 2 — Auth core (service + middleware + login)
- [x] 2.1 `modules/auth/auth.service.ts`: `JwtPayload` becomes `{ sub, rol, tv }`; `signToken` includes `tv`
- [x] 2.2 `auth.service.ts`: `verifyToken` returns `tv`; treat a missing `tv` in an old token as `0`
- [x] 2.3 `middleware/auth.ts` `requireAuth`: make async-safe (wrap with asyncHandler / convert to async + try-catch returning 401 instead of throwing synchronously)
- [x] 2.4 `requireAuth`: after verifying the JWT, fetch the user by id (PK) via the prisma singleton; reject 401 unless `activo === true` AND `activationToken == null` AND `payload.tv === user.tokenVersion`
- [x] 2.5 `auth.router.ts` `POST /auth/login`: reject with generic 401 when `activationToken != null` (pending account); sign token with the user's current `tokenVersion`

## Batch 3 — tokenVersion bumps (set-password, reset, deactivate)
- [x] 3.1 `auth.router.ts` `POST /auth/set-password`: in the update, also `tokenVersion: { increment: 1 }`
- [x] 3.2 `modules/usuarios/usuarios.router.ts` `POST /:id/reset-password`: add `tokenVersion: { increment: 1 }` to the update
- [x] 3.3 `usuarios.router.ts` PATCH (activo update): bump `tokenVersion` on true→false (simplest: always `increment` when the patch includes `activo: false`)

## Batch 4 — Tests (vitest + supertest, prisma mocked)
- [x] 4.1 Update prisma mocks/fixtures so the new `requireAuth` DB lookup (`usuario.findUnique` by id) is covered, returning `activo`/`activationToken`/`tokenVersion`
- [x] 4.2 reset-password → pre-reset token rejected 401 by a protected route
- [x] 4.3 reset-password → old password rejected at login 401 (pending-gate / mismatch)
- [x] 4.4 set-password completes → pre-activation token 401
- [x] 4.5 deactivate → existing token 401
- [x] 4.6 happy path: login active user → token carries `tv` → protected route 200
- [x] 4.7 login of a pending user (`activationToken != null`) → 401

## Batch 5 — Verify
- [x] 5.1 Automated: `pnpm --dir lex-control-api test` green
- [x] 5.2 Build: `pnpm --dir lex-control-api build` clean
- [x] 5.3 (Frontend follow-up) Confirmed: both apps already turn a 401 into "clear session + redirect to /login" (`lex-control-admin/src/lib/api.ts:54`, `lex-control-client/src/lib/api.ts:52`). A revoked session bounces to login on its next request — no frontend change needed.
- [ ] 5.4 (Manual, pending) Live e2e against the running stack: login → admin resets that user → the live session 401s on its next request AND the old password is rejected at login
