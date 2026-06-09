# Design: API Foundation for lex-control-api

## Technical Approach
Add an Express HTTP server inside the existing `@lex/db` package, reusing its `prisma` singleton (`src/index.ts`). Code is organized by **feature module** (`modules/auth`, `modules/servicio`) with a shared layering convention `routes → controller → service → prisma`, plus cross-cutting `config/` and `middleware/`. Input is validated with zod. Auth uses bcrypt + JWT. Stays CommonJS; `tsx` runs TS directly in dev, `tsc` builds to `dist/` for prod. Realizes specs `http-api-foundation`, `authentication`, `service-management`.

## Architecture Decisions

### Decision: Server lives in lex-control-api (no new package)
**Choice**: Keep the server in `@lex/db`, import its `prisma` export directly.
**Alternatives considered**: New `@lex/api` package consuming `@lex/db`.
**Rationale**: Zero cross-package wiring; the singleton already exists. Renaming to a clearer name is a cheap follow-up; not worth blocking the foundation.

### Decision: Feature-module structure over technical-layer folders
**Choice**: `modules/<feature>/<feature>.{routes,controller,service}.ts`.
**Alternatives considered**: Top-level `routes/ controllers/ services/` split by layer.
**Rationale**: Co-locating a feature's files scales better as resources grow (Empresa, Usuario, EmpresaServicio coming next) and keeps slices independent.

### Decision: tsx (dev) + tsc/node (prod), stay CommonJS
**Choice**: `dev: tsx watch src/server.ts`; `build: tsc`; `start: node dist/server.js`.
**Alternatives considered**: ts-node; switch to ESM (`type:module`).
**Rationale**: `tsx` is fast and interop-friendly; switching to ESM now risks churn with the existing NodeNext+CJS setup and Prisma. Defer ESM.

### Decision: zod for validation, central error handler
**Choice**: Validate body/params with zod schemas in a `validate` middleware; throw typed `HttpError`; one error middleware maps to the uniform JSON shape.
**Rationale**: Keeps controllers thin and satisfies the foundation's error-shape requirements in one place.

## Data Flow
```
Frontend (:3000 / :3001)
   │  Authorization: Bearer <jwt>
   ▼
app.ts ─→ cors ─→ json ─→ router
                            │
              ┌─────────────┴─────────────┐
        /auth/login                  /servicios/*
              │                            │
        auth.controller            authMiddleware → roleGuard(ADMIN for writes)
              │                            │
        auth.service                servicio.controller → servicio.service
              │                            │
         bcrypt / jwt                    prisma (@lex/db)
              └──────── error middleware (catch-all) ───────┘
                            ▼
                       MySQL "LEX"
```

## File Changes
| File | Action | Description |
|------|--------|-------------|
| `lex-control-api/package.json` | Modify | Add deps (express, cors, jsonwebtoken, bcrypt, zod, dotenv) + dev types + tsx; scripts `dev`/`build`/`start` |
| `lex-control-api/.env` | Modify | Add `PORT`, `JWT_SECRET`, `CORS_ORIGINS` |
| `lex-control-api/src/index.ts` | Keep | Remains the DB export; server imports `prisma` from it |
| `lex-control-api/src/config/env.ts` | Create | Load + validate env (fail fast if `JWT_SECRET` missing) |
| `lex-control-api/src/app.ts` | Create | Build Express app: cors, json, routes, 404, error handler |
| `lex-control-api/src/server.ts` | Create | Entry: load env, start `app` on `PORT` |
| `lex-control-api/src/middleware/error.ts` | Create | `HttpError` + central error handler + 404 |
| `lex-control-api/src/middleware/validate.ts` | Create | zod validation middleware |
| `lex-control-api/src/middleware/auth.ts` | Create | JWT verify + `requireRole(...roles)` guard |
| `lex-control-api/src/modules/auth/*` | Create | `auth.routes/controller/service` (login, hashing) |
| `lex-control-api/src/modules/servicio/*` | Create | `servicio.routes/controller/service` (CRUD) |

## Interfaces / Contracts
```ts
// JWT payload
type JwtPayload = { sub: string; rol: "ADMIN" | "USUARIO" };

// Uniform error body
type ApiError = { error: { message: string; issues?: unknown } };

// POST /auth/login
type LoginRequest = { email: string; password: string };
type LoginResponse = { token: string; user: { id: string; nombre: string; rol: string } };
```

## Testing Strategy
| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | auth.service (hash/verify, token sign), servicio.service | Pure function tests (test runner TBD — none configured yet) |
| Integration | login flow, servicio CRUD with role guards | supertest against the Express app with a test DB |
| E2E | — | Out of scope for this change |

No test runner exists yet; this change MAY add `vitest`+`supertest` as part of tasks, or defer testing to a follow-up. Flag in Open Questions.

## Migration / Rollout
No DB migration required — schema already pushed. Rollout is additive: existing `@lex/db` consumers are unaffected. A seed/admin-bootstrap step is needed to create the first `ADMIN` with a hashed password (since current rows, if any, are plaintext).

## Resolved Decisions
- **Testing**: include integration tests with `vitest` + `supertest` covering auth + `Servicio` spec scenarios. (Unit tests optional.)
- **Seed**: add a `seed` script that creates the first `ADMIN` with a bcrypt-hashed password.
- **Update verb**: `PATCH /servicios/:id` (partial update).
- **Password column**: keep `Usuario.password String` (VARCHAR 191) — bcrypt hash (60 chars) fits; no schema change.
