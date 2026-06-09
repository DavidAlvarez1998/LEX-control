## Exploration: api-foundation — grow `lex-control-api` into a real Express HTTP API

### Current State
- `lex-control-api` is package `@lex/db` — a **data layer only**, not a server.
- `src/index.ts` exports a `prisma` singleton (dev hot-reload safe) and re-exports `@prisma/client`. That is the entire source.
- `package.json` has only Prisma scripts (`generate`, `migrate`, `push`, `studio`). **No `build`, no `start`, no `dev`, no server deps.**
- `main` points to `./src/index.ts` (raw TS) — works only inside a bundler/transpiler (the Next apps). A standalone Node server needs a TS runtime or a build step.
- `tsconfig`: `target ES2022`, `module NodeNext`, but package has no `"type":"module"` → effectively **CommonJS**. `outDir: dist`, `declaration: true`. Node v22.
- DB is already pushed (no migrations) to MySQL `LEX`. Models: `Empresa`, `Usuario`, `Servicio`, `EmpresaServicio`.
- `Usuario.password` is a plain column — **no hashing/auth layer exists yet**.
- No tests, no linter configured in this package.

### Affected Areas
- `lex-control-api/package.json` — add Express + runtime/build/start scripts and deps.
- `lex-control-api/src/index.ts` — keep as the DB export; the server should consume it, not replace it.
- `lex-control-api/src/` — new HTTP layering (entry, app, routes, controllers, middleware).
- `lex-control-api/tsconfig.json` — confirm CJS vs ESM decision; align with chosen TS runtime.
- `lex-control-admin` / `lex-control-client` — future consumers of the API (out of scope for this change, but the contract must serve them).

### Approaches
Framework is **decided: Express**. The real forks are *how* to structure and run it.

1. **Layered Express in a single `@lex/db`→`@lex/api` package** (server lives where it is, reusing the prisma singleton directly)
   - Pros: zero cross-package wiring; reuses existing `prisma` export immediately; smallest setup.
   - Cons: the package stops being "just db" — naming (`@lex/db`) becomes misleading; mixes data layer + HTTP.
   - Effort: Low

2. **Layered architecture: `routes → controllers → services → prisma`, with middleware (error handler, auth, validation)**
   - Pros: clean separation, testable, scales as endpoints grow; matches the domain (Empresa/Usuario/Servicio).
   - Cons: more files/boilerplate upfront.
   - Effort: Medium

3. **Minimal flat Express (everything in a few files)**
   - Pros: fastest to a running endpoint.
   - Cons: becomes unmaintainable as auth, validation, and 4 resources are added; rework later.
   - Effort: Low

Runtime sub-decision: **`tsx` for dev** (fast, no build) + **`tsc` build → `node dist` for prod**. Keeps CommonJS, no `type:module` churn.

### Recommendation
Combine **#1 + #2**: keep the server inside `lex-control-api` (reuse the `prisma` singleton — no new package), but structure it with **layered architecture** (`app.ts` + `server.ts` entry, `routes/`, `controllers/`, `services/`, `middleware/`). Add `tsx`-based `dev` and a `tsc` `build`/`start`. Defer auth internals but reserve the seams (auth middleware, password hashing) since `Usuario.password` already exists.

Scope this change to the **foundation**: a running Express server with health check, error handling, config/env loading, and ONE vertical slice (likely `Empresa` CRUD) to prove the layering — not all four resources at once.

### Risks
- `main: ./src/index.ts` + no build today: other consumers may rely on importing raw TS; adding a build/`exports` map could change how the Next apps resolve `@lex/db` (they don't import it yet, so low risk now).
- CommonJS vs NodeNext mismatch can bite with ESM-only deps; pin to CJS-friendly versions or switch deliberately.
- `Usuario.password` is plaintext in schema — auth must hash before any real usage; flag as a follow-up change, not this foundation.
- No migrations (push-only) means schema drift is manual — fine for dev, risky for prod.

### Ready for Proposal
Yes. Recommend proceeding to `propose` with: Express + layered architecture inside `lex-control-api`, `tsx` dev runtime, foundation scope = running server + health + error handling + one resource slice. Confirm with user whether the first vertical slice should be `Empresa` and whether auth is in-scope now or deferred.
