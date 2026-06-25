# Design: Dockerize LEX Control

## Topology

```
                 docker network: lex-net
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │ admin :3000  │   │ client :3001 │   │  api :4000   │
  │ (next start) │   │ (next start) │   │ node dist/.. │
  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         │ /api/* rewrite    │ /api/* rewrite   │ Prisma
         └─────────┬─────────┘                  │
              http://api:4000          ┌────────▼─────────┐
                                       │ MySQL "LEX"      │
                                       │ dev: container   │
                                       │ prod: external   │
                                       └──────────────────┘
         external (not containerized): tecnovapp docs · notif 10.10.10.211:5020 · Rama Judicial :448
```

The browser only ever talks to admin/client (3000/3001). Each Next app proxies
`/api/*` to the API server-side via its `rewrites()` (`API_PROXY_TARGET`), so the
API port never needs to be exposed to the browser — this already matches the SSH
dev-server constraint where only 3000/3001 are forwarded.

## 1. API image (`lex-control-api/Dockerfile`)

Multi-stage, `node:22-alpine`:

- **deps/build stage**: enable pnpm via `corepack`; `pnpm install --frozen-lockfile`;
  copy `prisma/` and run `pnpm generate` (Prisma `generate` reads only the schema,
  **no DB connection needed at build time**); `pnpm build` (`tsc` → `dist`).
- **runtime stage**: copy `dist/`, `node_modules` (or run `pnpm install --prod`),
  the generated Prisma client and `prisma/schema.prisma`; run as a non-root user;
  `ENTRYPOINT ["tini","--"]`, `CMD ["node","dist/server.js"]`; `EXPOSE 4000`.

Gotchas:

- **Prisma on Alpine** needs OpenSSL — `apk add --no-cache openssl` (and keep
  `libssl`/`ca-certificates`) or the query engine fails to load at runtime. If the
  detected engine target is wrong, set
  `binaryTargets = ["native","linux-musl-openssl-3.0.x"]` in the schema generator.
- **Graceful shutdown already exists** (`server.ts` handles SIGTERM/SIGINT); use
  `tini`/`dumb-init` as PID 1 so signals reach Node instead of being swallowed.
- **Healthcheck**: `GET /health` exists (`app.ts`) → use it for the compose
  healthcheck.
- **Fail-fast env**: `config/env.ts` `process.exit(1)` if `JWT_SECRET` is missing,
  so the container will crash-loop until env is provided — intended, document it.

## 2. Frontend images (admin & client)

Multi-stage Next.js 16 with **`output: "standalone"`** added to each
`next.config.ts` (smallest runtime: copy `.next/standalone` + `.next/static` +
`public`, run `node server.js`). Client keeps port 3001 (`-p 3001` / `PORT=3001`).

**Critical gotcha — `rewrites()` and build-time env.** Next.js evaluates
`rewrites()` at **build time** for a production build, so `API_PROXY_TARGET` is
**baked into the image** when running `next build`. Therefore in prod the proxy
target must be fixed at build time. Options:

- **(chosen)** Default the rewrite to the compose service name and pass it as a
  build `ARG` → `ENV` so `next build` reads `API_PROXY_TARGET=http://api:4000`.
- Alternative: keep `API_PROXY_TARGET` defaulting to `http://api:4000` directly in
  `next.config.ts` (no build arg). Simpler, but the value is hardcoded.

In **dev** (`next dev`) `rewrites()` is evaluated per server start, so the env var
works at runtime with no rebuild — no special handling needed there.

These apps currently do **not** import `@lex/db`; their images need no Prisma and no
`DATABASE_URL`.

## 3. Compose — dev (`docker-compose.dev.yml`)

Services: `mysql`, `api`, `admin`, `client` on `lex-net`.

- **api**: run the base node image with the command overridden to `pnpm dev`
  (`tsx watch`); bind-mount `./lex-control-api:/app` with a **named volume for
  `/app/node_modules`** so host deps don't shadow the container's; `env_file:
  ./lex-control-api/.env`.
- **admin/client**: bind-mount source + named `node_modules`/`.next`; command
  `pnpm dev`; `API_PROXY_TARGET=http://api:4000`; ports `3000:3000` / `3001:3001`.

> **REVISED 2026-06-25 — dev uses the REAL external DB, no MySQL container.**
> Originally dev shipped a throwaway `mysql:8` container (empty DB, `DATABASE_URL`
> overridden to `mysql:3306`). In practice the team needs their real users/data, so
> the `mysql` service + the `DATABASE_URL` override were removed: the dev API now
> reads `DATABASE_URL` from `.env` and connects to the external DB
> (`DEMO-ROUTER.FINOVA.COM.CO:3306`), exactly like bare `pnpm dev` did. The container
> DB and its volume (`lex-mysql-data`) were deleted. Reachability verified: the
> container opens TCP to that remote host fine (it is not `localhost`). **Consequence:
> dev now talks to production data → `pnpm push` from the container hits the REAL
> schema. Do not run it casually** (and `pnpm migrate` resets the DB — see §5).
> The container-MySQL option remains valid if an isolated sandbox is ever wanted
> (load a dump into it); it was simply not what this team needed.

## 4. Compose — prod (`docker-compose.yml`, default)

Built images (`image:`/`build:`), `restart: unless-stopped`, healthchecks, **no**
source mounts, **no** mysql service. The API's `DATABASE_URL` points at the external
MySQL (env-injected). `CORS_ORIGINS`, `CLIENT_URL`, `ADMIN_URL` set to the real
public origins. Frontends built with `API_PROXY_TARGET=http://api:4000`.

Reaching the **internal** notifications host `10.10.10.211:5020` from inside a
container depends on the Docker host having a route to that subnet (usually fine on
the dev/prod server; bridge networking NATs out through the host). Flag for the
first prod smoke test; `network_mode` tweaks are a fallback if not reachable.

## 5. Database & migrations (do NOT auto-migrate)

The live DB is managed by `prisma db push`, not Migrate — `prisma migrate dev`
**resets the database** (`db-not-managed-by-migrate`). A baseline `0_init` migration
exists (`prisma/migrations/0_init`, from `ops-migraciones-ci`) but the live schema
was advanced with `db push` and may have drifted from it.

Therefore:

- The API container entrypoint **does not** run any migration automatically.
- Schema changes continue to be applied manually with `pnpm push` against the target
  DB (a documented step, not part of container startup).
- **Since dev now points at the REAL DB (see §3 revision), `pnpm push` from the dev
  container alters production.** It is NOT a routine dev step here. (When the throwaway
  container DB existed, `push` was safe because it hit an empty, disposable database.)
- `prisma migrate deploy` MAY be adopted later as an opt-in entrypoint **only** once
  the baseline is reconciled with the live schema — out of scope here.

## 6. Secrets & env contract

`.gitignore` already blocks `.env*` except `!.env.example`. This change adds a
committed `.env.example` per project enumerating the contract:

- **api**: `DATABASE_URL`, `JWT_SECRET` (required), `PORT`, `CORS_ORIGINS`,
  `CLIENT_URL`, `ADMIN_URL`, plus optional `DOCUMENTOS_*`, `NOTIFICAR_*`,
  `RAMA_JUDICIAL_*` (all have defaults in `config/env.ts`).
- **admin/client**: `API_PROXY_TARGET` (and `PORT` for client).

Real `.env` files are mounted/`env_file`-injected, never baked into images.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Dev + prod compose, separate files | Different lifecycles: hot-reload+bind-mount vs built+immutable. |
| D2 | ~~MySQL container in dev~~ → **dev + prod both use the external/real DB** (REVISED 2026-06-25) | Team needs real users/data in dev; the empty container DB only caused confusion (logins failing because users live in the real DB). Container MySQL kept as an optional sandbox, not the default. |
| D3 | Next.js `output: "standalone"` | Smallest runtime image; official pattern for Next on Docker. |
| D4 | `API_PROXY_TARGET` as build ARG for prod | `rewrites()` is build-time evaluated; can't be purely runtime in a prod build. |
| D5 | No auto-migration in entrypoint | DB is push-managed; `migrate dev` would reset it. |
| D6 | Dockerfiles live in submodules, compose in root | Each project is its own git repo; root orchestrates. |
| D7 | `tini`/`dumb-init` as PID 1 | Deliver SIGTERM/SIGINT to Node so the existing graceful shutdown runs. |
| D8 | **Shared pnpm store across the 3 dev containers** (added 2026-06-25) | A single `pnpm-store` volume + `npm_config_store_dir=/pnpm-store` in all three services. Otherwise pnpm falls back to `/app/.pnpm-store` inside each bind-mounted submodule (3× store, ~1.2 GB, polluting the repos — had to be `.gitignore`d). All 3 images are Alpine/musl, so one shared store is safe. Set ONLY in the root compose → no `.npmrc` in submodules. Note: `node_modules` stay as 3 separate volumes (distinct dependency trees; can't dedupe across volume mounts). |
