# Tasks: API Foundation for lex-control-api

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 650–900 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes (but repo is NOT a git repo — see note) |
| Suggested split | Batch 1 Foundation → Batch 2 Auth+Seed → Batch 3 Servicio+Tests |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

> Note: this workspace is not a git repository, so literal PRs don't apply. The "work units" below map to **apply batches** with a check-in between each.

### Suggested Work Units

| Unit | Goal | Batch | Notes |
|------|------|-------|-------|
| 1 | Running server: config, app, middleware, health, CORS, errors | Batch 1 | Independent; verify `GET /health` |
| 2 | Auth: hashing, login/JWT, auth + role middleware, seed | Batch 2 | Depends on Unit 1 |
| 3 | Servicio CRUD + integration tests | Batch 3 | Depends on Units 1–2 |

## Phase 1: Foundation / Infrastructure

- [x] 1.1 Update `package.json`: add deps (express, cors, jsonwebtoken, bcryptjs, zod, dotenv), devDeps (@types/*, tsx, vitest, supertest, typescript), scripts `dev`/`build`/`start`/`seed`/`test`
- [x] 1.2 `.env` present (user added) with `DATABASE_URL`, `PORT`, `JWT_SECRET`, `CORS_ORIGINS`. (`.env.example` still pending — `.env*` is write-denied to the assistant; content handed to the user to create.)
- [x] 1.3 Create `src/config/env.ts`: load + validate env, fail fast if `JWT_SECRET` missing
- [x] 1.4 Create `src/middleware/error.ts`: `HttpError` class, central error handler, 404 handler (uniform JSON shape)
- [x] 1.5 Create `src/middleware/validate.ts`: zod validation middleware (body/params) → 400 on failure
- [x] 1.6 Create `src/app.ts`: assemble cors (from `CORS_ORIGINS`), json parser, routes mount, `GET /health`, 404, error handler
- [x] 1.7 Create `src/server.ts`: load env, start `app` on `PORT`, log startup

## Phase 2: Authentication + Seed

- [x] 2.1 `src/modules/auth/auth.service.ts`: hashPassword/verifyPassword (bcryptjs), signToken/verifyToken (jwt)
- [x] 2.2 `src/modules/auth/auth.router.ts` (+ `auth.schemas.ts`): `POST /auth/login` (200+token / 401 invalid / 401 inactive). [Flat router, no separate controller — repo convention]
- [x] 2.3 `src/middleware/auth.ts`: requireAuth (Bearer→401) + requireRole(...Rol) (403)
- [x] 2.4 `src/seed-admin.ts` + `seed:admin` script: idempotent ADMIN with bcrypt hash (env-driven). [Catalog seed lives in `seed.ts`]

## Phase 3: Servicio CRUD  (done in parallel session; protected in Batch 2)

- [x] 3.1 `src/modules/servicios/servicios.router.ts`: list/getById/create/PATCH/delete via prisma (handlers inline)
- [x] 3.2 `servicios.schemas.ts`: zod (nombre, precioBase, precioPorUnidad, unidad, incluidos, activo)
- [x] 3.3 Routes: GET requireAuth; POST/PATCH/DELETE requireRole(ADMIN); mounted in `app.ts`. Also `empresas` CRUD added (ADMIN-only).

## Phase 4: Integration Tests

- [x] 4.1 `vitest` configured; tests boot `app` via supertest with a mocked prisma client (`vi.mock("../src/index")`)
- [x] 4.2 Auth tests (`tests/auth.test.ts`): login valid→200+token, invalid→401, inactive→401, bad body→400; plus set-password (happy/expired/invalid/weak)
- [x] 4.3 Servicio tests (`tests/servicios.test.ts`): list (auth/401), create ADMIN→201 / USUARIO→403 / invalid→400, get missing→404
- [x] 4.4 Empresas tests (`tests/empresas.test.ts`): list/get/create/patch/delete guards (401/403/400/201/409/404/204)

## Phase 5: Verify / Docs

- [x] 5.1 `pnpm build` compiles clean (tsc); `pnpm test` → 45 passing across 4 suites
- [ ] 5.2 Update `lex-control-api` notes / `CLAUDE.md` with run + seed instructions (optional; CLAUDE.md still describes the pre-API state)
