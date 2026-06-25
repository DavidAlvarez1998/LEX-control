# Tasks: Dockerize LEX Control

> Each file lives in its submodule unless marked **(root)**. Build command gate:
> images build clean and the dev stack comes up healthy.

## Phase 1 — API image (`lex-control-api`)

- [ ] 1.1 Add `.dockerignore` (`node_modules`, `dist`, `.next`, `.env*`, `.git`, logs).
- [ ] 1.2 Add multi-stage `Dockerfile` (node:22-alpine): corepack pnpm →
  `pnpm install --frozen-lockfile` → `pnpm generate` → `pnpm build`.
- [ ] 1.3 Runtime stage: non-root user, `apk add openssl ca-certificates`, copy
  `dist` + prod deps + generated Prisma client + `prisma/schema.prisma`.
- [ ] 1.4 `ENTRYPOINT ["tini","--"]`, `CMD ["node","dist/server.js"]`, `EXPOSE 4000`.
- [ ] 1.5 If the engine fails to load, set `binaryTargets` in the schema generator
  and re-run `pnpm generate`.
- [ ] 1.6 Add `.env.example` (DATABASE_URL, JWT_SECRET, PORT, CORS_ORIGINS,
  CLIENT_URL, ADMIN_URL, optional DOCUMENTOS_*/NOTIFICAR_*/RAMA_JUDICIAL_*).
- [ ] 1.7 Build standalone (`docker build`) and smoke `GET /health` with a throwaway
  `DATABASE_URL`/`JWT_SECRET`.

## Phase 2 — Frontend images (`lex-control-admin`, `lex-control-client`)

- [ ] 2.1 Add `output: "standalone"` to each `next.config.ts` (keep existing
  `rewrites`/`redirects`/`viewTransition`).
- [ ] 2.2 Add `.dockerignore` to each (`node_modules`, `.next`, `.env*`, `.git`).
- [ ] 2.3 Multi-stage `Dockerfile` each: deps → `next build` (with
  `ARG API_PROXY_TARGET` → `ENV`) → runner copying
  `.next/standalone` + `.next/static` + `public`; `CMD ["node","server.js"]`.
  Client serves on 3001 (`PORT=3001` / `EXPOSE 3001`).
- [ ] 2.4 Add `.env.example` each (`API_PROXY_TARGET`; client also `PORT`).
- [ ] 2.5 Build both images and verify each renders a page.

## Phase 3 — Dev compose **(root)**

- [ ] 3.1 Fill `docker-compose.dev.yml`: `mysql` (mysql:8, DB `LEX`, named volume,
  `mysqladmin ping` healthcheck).
- [ ] 3.2 `api` service: bind-mount `./lex-control-api`, anonymous `/app/node_modules`,
  command `pnpm dev`, `env_file`, `DATABASE_URL=mysql://...@mysql:3306/LEX`,
  `depends_on: mysql (service_healthy)`.
- [ ] 3.3 `admin` + `client`: bind-mount source, anonymous `node_modules`/`.next`,
  command `pnpm dev`, `API_PROXY_TARGET=http://api:4000`, ports 3000 / 3001.
- [ ] 3.4 Shared `lex-net` network.
- [ ] 3.5 `docker compose -f docker-compose.dev.yml up` → all healthy; load
  admin (3000) and client (3001); confirm a `/api/*` call reaches the API.
- [ ] 3.6 One-time DB setup: run `pnpm push` (+ seeds) against the dev MySQL.

## Phase 4 — Prod compose **(root)**

- [ ] 4.1 `docker-compose.yml` (prod, default): built images, `restart: unless-stopped`,
  healthchecks, no source mounts, **no** mysql service.
- [ ] 4.2 API `DATABASE_URL` → external MySQL; `CORS_ORIGINS`/`CLIENT_URL`/`ADMIN_URL`
  = real origins; frontends built with `API_PROXY_TARGET=http://api:4000`.
- [ ] 4.3 Smoke on the target host: stack up, `/health` green, verify the internal
  notifications host `10.10.10.211:5020` is reachable from the API container
  (fallback: adjust networking if not).

## Phase 5 — Docs & commit

- [ ] 5.1 README: "Run with Docker" (dev one-liner + prod notes); restate the
  DB gotcha (push, never `migrate dev`; containers don't auto-migrate).
- [ ] 5.2 Commit per submodule (Dockerfile/.dockerignore/.env.example/next.config)
  and the two compose files in root; bump submodule pointers in root.
- [ ] 5.3 Archive this change into `openspec/specs/` once verified.
