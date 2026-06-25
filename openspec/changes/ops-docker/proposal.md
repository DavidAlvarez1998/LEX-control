# Proposal: Dockerize LEX Control (dev + prod)

## Why

LEX Control is three independent projects (`lex-control-api`, `lex-control-admin`,
`lex-control-client`) with no workspace tooling, each run separately with `pnpm`,
plus an external MySQL. Today onboarding and deployment are manual: install pnpm,
run three dev servers on three ports, point them at a MySQL the developer must
provide, and replicate env files by hand. There is an empty `docker-compose.dev.yml`
at the repo root signalling the intent but nothing behind it.

Goals:

- **One command to run the whole stack** locally (api + admin + client + MySQL),
  reproducible across machines and the SSH dev server.
- **Reproducible production images** (multi-stage, small, non-root) that can be
  deployed without a developer toolchain on the host.
- **No secret/config drift**: env contracts captured as committed `.env.example`
  files; real secrets stay out of git (already enforced by `.gitignore`).

## What changes

Per the decisions taken for this change:

- **Scope:** both **dev** and **prod**.
- **MySQL:** ~~a containerized MySQL service in dev~~ → **REVISED 2026-06-25: dev and
  prod both connect to the existing external MySQL** via `DATABASE_URL` (no DB
  container in either). The container-MySQL idea was dropped after testing: the team
  needs their real users/data in dev, and the empty container DB only caused login
  failures (users live in the real DB). A container DB remains an option for an
  isolated sandbox, but is not the default. See `design.md` §3 + D2.

Concretely:

1. **`lex-control-api/Dockerfile`** — multi-stage Node 22 (alpine) image:
   `pnpm install` → `prisma generate` → `tsc` build → slim runtime running
   `node dist/server.js` on port 4000, non-root, with `tini`/`dumb-init` for clean
   signal handling (the server already implements SIGTERM/SIGINT graceful shutdown).
2. **`lex-control-admin/Dockerfile`** and **`lex-control-client/Dockerfile`** —
   multi-stage Next.js 16 images using `output: "standalone"` (added to each
   `next.config.ts`), serving on ports 3000 and 3001 respectively.
3. **`docker-compose.dev.yml`** (fill the existing empty file) — `mysql`, `api`,
   `admin`, `client` on a shared network, with source bind mounts + hot reload
   (`tsx watch` / `next dev`) and `env_file` per service.
4. **`docker-compose.yml`** (prod, default) — built images, external `DATABASE_URL`, restart
   policies, healthchecks, **no** source mounts and **no** DB container.
5. **`.dockerignore`** per project and **`.env.example`** per project documenting
   the required env contract.

Each `Dockerfile` / `.dockerignore` / `.env.example` / `next.config.ts` edit lives
**inside its submodule repo**; the two compose files live in the **root repo**.

## Non-goals

- No CI/CD pipeline or image registry/publishing (separate change; relates to
  `ops-migraciones-ci`).
- No containerization of the external services (tecnovapp documents, the internal
  notifications microservice at `10.10.10.211:5020`, the Rama Judicial public API) —
  these stay external and are reached over the network.
- No change to the database management strategy. The DB remains managed by
  `prisma db push`, **not** Prisma Migrate (see Design §5 and the
  `db-not-managed-by-migrate` note); containers do **not** auto-migrate.

## Impact

- Affected projects: all three (new Docker files + standalone output) and the root
  (two compose files).
- Affected workflows: local dev start, dev-server start, future deploy.
- Risk: low for dev; prod images are net-new and opt-in. Rollback = keep running
  the projects with `pnpm dev` / `pnpm build && pnpm start` as today (Docker is
  additive, nothing is removed).
