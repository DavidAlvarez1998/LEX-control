# Proposal: API Foundation for lex-control-api (Express + Auth + Servicio CRUD)

## Intent
`lex-control-api` is only the `@lex/db` data layer — no HTTP surface. Both frontends need a backend to consume. This change stands up a real Express API with a layered, scalable structure, proven by one authenticated resource slice (`Servicio`) and a working auth flow over the existing `Usuario` model.

## Scope

### In Scope
- Express server: `server.ts` entry + `app.ts`, env/config loading, `tsx` dev + `tsc` build/start scripts.
- Layered architecture: `routes → controllers → services → prisma` (reusing the existing `prisma` singleton).
- Cross-cutting middleware: centralized error handler, request validation, 404, JSON body parsing, health check (`GET /health`).
- CORS configured from env (`CORS_ORIGINS`) allowing the admin (`:3000`) and client (`:3001`) Next.js origins, with credentials.
- Authentication: password hashing (bcrypt), `POST /auth/login` issuing JWT, auth middleware, role guard (`ADMIN` | `USUARIO`).
- `Servicio` CRUD vertical slice (list, get, create, `PATCH` update, delete) behind auth, with `ADMIN`-only writes.
- Seed script that creates the first `ADMIN` user with a bcrypt-hashed password.
- Integration tests (`vitest` + `supertest`) covering the auth and `Servicio` spec scenarios.

### Out of Scope
- CRUD for `Empresa`, `Usuario`, `EmpresaServicio` (follow-up changes).
- Refresh tokens, password reset, rate limiting.
- Wiring the Next.js frontends to the API.
- Switching push-only DB to Prisma migrations.

## Capabilities

### New Capabilities
- `http-api-foundation`: Express bootstrap, config, error handling, health, layering conventions.
- `authentication`: password hashing, JWT login, auth + role middleware.
- `service-management`: `Servicio` CRUD endpoints with role-based authorization.

### Modified Capabilities
- None.

## Approach
Keep the server inside `lex-control-api` (no new package) reusing `src/index.ts`'s `prisma`. Add `src/server.ts`, `src/app.ts`, `src/config/`, `src/middleware/`, `src/modules/auth/`, `src/modules/servicio/` (each: `*.routes.ts`, `*.controller.ts`, `*.service.ts`). Stay CommonJS (no `type:module`). Validate input with zod. Sign JWT with a secret from env.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/package.json` | Modified | Add express, cors, jsonwebtoken, bcrypt, zod, dotenv, tsx, types; add dev/build/start scripts |
| `lex-control-api/src/index.ts` | Modified | Keep DB export; server imports it |
| `lex-control-api/src/{app,server}.ts`, `config/`, `middleware/`, `modules/` | New | HTTP layering |
| `lex-control-api/.env` | Modified | Add `JWT_SECRET`, `PORT`, `CORS_ORIGINS` |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| CJS/ESM dep mismatch | Med | Pin CJS-friendly versions; `tsx` handles interop |
| Plaintext passwords in DB | High | Hash on create; login compares hash; document seeding |
| JWT secret leakage | Med | Load from env only; never commit `.env` |

## Rollback Plan
All work is additive to a non-server package. Revert by removing new `src/` files and reverting `package.json`/`.env`; `@lex/db` keeps working as before. No DB schema changes.

## Dependencies
- Existing pushed MySQL schema (`Usuario`, `Servicio`).
- `JWT_SECRET` set in `lex-control-api/.env`.

## Success Criteria
- [ ] `pnpm dev` starts the server; `GET /health` returns 200.
- [ ] `POST /auth/login` returns a JWT for valid credentials, 401 otherwise.
- [ ] `Servicio` CRUD works; writes require `ADMIN`, reads require a valid token.
- [ ] `pnpm build` compiles to `dist/` and `pnpm start` runs it.
