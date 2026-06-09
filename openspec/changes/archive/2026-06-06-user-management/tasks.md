# Tasks: User Management + Activation Link

## Review Workload Forecast
| Field | Value |
|-------|-------|
| Estimated changed lines | 500–750 |
| 400-line budget risk | High |
| Suggested split | Batch 1 backend → Batch 2 admin UI → Batch 3 client activation |

Decision needed before apply: Yes
Chained PRs recommended: Yes (mapped to apply batches; per-project repos)
Chain strategy: pending
400-line budget risk: High

## Batch 1 — Backend (API)
- [x] 1.1 `schema.prisma`: add `Usuario.activationToken String? @unique`, `activationExpires DateTime?`; pushed + generated
- [x] 1.2 `config/env.ts`: add `clientUrl` (`CLIENT_URL`, default `http://localhost:3001`)
- [x] 1.3 `auth.service.ts`: `generateActivationToken()` (raw + sha256), `hashActivationToken(raw)`
- [x] 1.4 `modules/usuarios/usuarios.schemas.ts` + `auth.schemas.ts` setPasswordSchema (min 8)
- [x] 1.5 `modules/usuarios/usuarios.router.ts`: GET list (`?empresaId`), POST create (→ activationUrl), PATCH, POST `/:id/reset-password`; all `requireRole(ADMIN)`
- [x] 1.6 `auth.router.ts`: `POST /auth/set-password` (public) — verify token+expiry, set bcrypt password, clear token
- [x] 1.7 `app.ts`: mount `/usuarios`
- [x] 1.8 Tests (`tests/usuarios.test.ts` + set-password block in `tests/auth.test.ts`): create→link, set-password (happy/expired/invalid/weak), list guard (401/403) + derived estado + no token leak, reset (200/404/403)

## Batch 2 — Admin UI (`usuarios/page.tsx`)
- [x] 2.1 Replaced placeholder with real list: GET /usuarios (empresa, rol, estado: ACTIVO/PENDIENTE/INACTIVO badges)
- [x] 2.2 "Nuevo usuario" modal: email, nombre, empresa (select from GET /empresas), rol, esAdminEmpresa → POST; on success shows copyable activation link
- [x] 2.3 Row actions: "Restablecer" (POST reset → show new link), "Editar" (PATCH nombre/rol/esAdminEmpresa/activo), "Desactivar/Activar" (PATCH activo)
- [x] 2.4 Copy-link modal (activation URL + copy button via navigator.clipboard, reused for create + reset)

## Batch 3 — Client activation page
- [x] 3.1 `lex-control-client/src/lib/api.ts`: minimal `setPassword(token, password)` client with AbortController timeout
- [x] 3.2 `lex-control-client/src/app/activar/page.tsx`: reads `?token` (Suspense-wrapped useSearchParams), password + confirm, POST /auth/set-password, success → "Ir al portal"
- [x] 3.3 Invalid/missing token and expired/used token (API 400) render a clear error message

## Batch 4 — Verify / Docs
- [x] 4.1 Automated: `pnpm test` 45 passing (incl. usuarios + set-password); admin + client `tsc --noEmit` clean; API `pnpm build` clean
- [x] 4.2a API e2e (assistant, against real MySQL DEMO): login admin → create empresa+user → set-password → login as new user → 200. Asserted: login-before-activate=401, token reuse=400 (single-use). Test rows cleaned up via empresa cascade.
- [ ] 4.2b Browser e2e (user action): admin :3000 → Usuarios → Nuevo → copy link → client :3001/activar → set password.
- [ ] 4.3 Update README/CLAUDE.md notes if needed (optional)
