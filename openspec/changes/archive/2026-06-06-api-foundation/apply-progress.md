# Apply Progress: API Foundation

**Mode**: Standard (no TDD; test runner added but tests come in Batch 3)

## Batch 1 — Foundation (DONE)

### Completed Tasks
- [x] 1.1 package.json: deps + scripts
- [x] 1.3 src/config/env.ts
- [x] 1.4 src/middleware/error.ts
- [x] 1.5 src/middleware/validate.ts
- [x] 1.6 src/app.ts
- [x] 1.7 src/server.ts
- [ ] 1.2 .env keys — BLOCKED (user action; `.env*` write-denied)

### Files Changed
| File | Action | What Was Done |
|------|--------|---------------|
| `lex-control-api/package.json` | Modified | Added express/cors/jsonwebtoken/bcryptjs/zod/dotenv + dev types/tsx/vitest/supertest/typescript; scripts dev/build/start/seed/test |
| `lex-control-api/src/config/env.ts` | Created | Env load + fail-fast on missing JWT_SECRET; parses CORS_ORIGINS |
| `lex-control-api/src/middleware/error.ts` | Created | HttpError + central error handler + 404 (uniform JSON) |
| `lex-control-api/src/middleware/validate.ts` | Created | zod validation middleware → 400 |
| `lex-control-api/src/app.ts` | Created | createApp: cors, json, GET /health, 404, error handler |
| `lex-control-api/src/server.ts` | Created | Entry: app.listen(PORT) |

### Verification
- `tsc --noEmit`: passes (after `prisma generate`).
- Runtime smoke (JWT_SECRET inline, port 4099): `GET /health` → 200 `{status:ok}`; unknown route → 404 JSON; CORS preflight from :3000 → allow-origin matched.

### Deviations from Design
- Used **bcryptjs** instead of **bcrypt** — pure-JS, avoids native node-gyp build (pnpm ignores build scripts here). Same API surface for our use. Design/proposal said bcrypt; this is the intended substitution.

### Issues Found
- `pnpm install` drops the generated Prisma client (build scripts ignored) — must run `pnpm generate` after installs. Documented.
- `.env*` files are write-denied for the assistant in lex-control-api — user must add env keys.

## Reconciliation — parallel session work (discovered later)

A parallel session advanced beyond Batch 1 and refined the domain. Actual state on disk:
- **Prisma schema evolved**: `Servicio` gained `precioPorUnidad`, `unidad`, `incluidos`, `nombre @unique`; `EmpresaServicio` now has per-empresa `precioBase`/`precioPorUnidad`/`incluidos`. Billing = base + per-unit beyond included. (Pushed to DB.)
- **`servicios` CRUD** done — `modules/servicios/{servicios.router.ts, servicios.schemas.ts}` (Batch 3 Phase 3, but UNPROTECTED — no role guard yet).
- **`empresas` CRUD** done — `modules/empresas/*` (was out of original scope; now in).
- **`middleware/async.ts`** added (asyncHandler for Express 4).
- **`seed.ts`** seeds the real service catalog (NOT a first-ADMIN user).
- **app.ts** mounts `/empresas` and `/servicios`; `/auth` still pending.
- Convention chosen: flat router (no controller/service split), Spanish comments/messages. `design.md` layering is superseded by this simpler convention.
- Fixed 2 TS2742 build errors (added explicit `: Router` type to exported routers).

`tsc --noEmit` clean after fixes.

## Batch 2 — Auth (DONE)
- `modules/auth/auth.service.ts` — hashPassword/verifyPassword (bcryptjs), signToken/verifyToken (JWT, 1d).
- `modules/auth/auth.schemas.ts` + `auth.router.ts` — `POST /auth/login` (generic 401, 401 inactive, 400 invalid body).
- `middleware/auth.ts` — `requireAuth` (Bearer) + `requireRole(...Rol)`; augments `Express.Request.user`.
- `app.ts` — mounts `/auth`.
- **servicios** routes protected: GET = requireAuth; POST/PATCH/DELETE = requireAuth + requireRole(ADMIN).
- **empresas** routes: ALL require ADMIN (assumption: platform-admin manages companies — confirm with user; a USUARIO seeing its own empresa is future work).
- `seed-admin.ts` + `seed:admin` script — idempotent ADMIN upsert with bcrypt hash, reads ADMIN_EMAIL/ADMIN_PASSWORD from env.
- Verified at runtime (port 4099, JWT_SECRET inline): protected routes → 401, login bad body → 400, bad creds → 401. Happy-path login not run (needs a real ADMIN row in DB — user to seed). `tsc --noEmit` clean.

## Batch 3 — Integration Tests (DONE)
- `tests/auth.test.ts` — login (400/401×3/200) + set-password (400 bad body / 400 weak / 400 missing / 400 expired / 200 happy, asserts token cleared + activo true).
- `tests/servicios.test.ts` — list auth/401, get 404, create 401/403/400/201.
- `tests/empresas.test.ts` — list/get/create/patch/delete with 401/403/400/201/409/404/204.
- `tests/usuarios.test.ts` — list (guards + derived estado + no token leak), create (403/400/201+link/409/400), patch (200/404), reset-password (200+link/404/403).
- Prisma errors simulated via `new Prisma.PrismaClientKnownRequestError(msg, { code, clientVersion })`.
- Result: `pnpm test` → **45 passing** across 4 suites. `pnpm build` (tsc) clean.

## Resolved since last update
- `.env` now present (user added `DATABASE_URL`/`PORT`/`JWT_SECRET`/`CORS_ORIGINS`). `.env.example` still pending — `.env*` is write-denied to the assistant; content handed to the user.
- `service-management` spec updated for the richer Servicio model (`precioPorUnidad`/`unidad`/`incluidos`).

## Remaining
- Confirm empresas authorization policy with product (currently ADMIN-only for all routes; a USUARIO viewing its own empresa is future work).
- Optional: refresh `lex-control-api` CLAUDE.md to describe the HTTP API + `seed:admin` (still documents the pre-API data-layer state).
