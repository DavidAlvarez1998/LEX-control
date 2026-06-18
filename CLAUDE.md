# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**LEX Control** is a multi-tenant platform for managing client companies (`empresas`), the services assigned to them, and billing. It is split into three independent projects (no monorepo/workspace tooling — each has its own `package.json` and is run separately):

- **`lex-control-api/`** — package `@lex/db`. Despite the name, this is **not an HTTP API server**; it is the shared Prisma data layer (MySQL schema + generated client). It exports a singleton `prisma` client and re-exports everything from `@prisma/client` (`src/index.ts`).
- **`lex-control-admin/`** — Next.js 16 (App Router, React 19) admin console for **platform ADMINs**. Runs on **port 3000**. Manages empresas, the service catalog, users, and billing across all tenants.
- **`lex-control-client/`** — Next.js 16 app for **company CLIENTE users**. Runs on **port 3001**. A tenant sees only their own account, contracted services, billing, and support.

`agents/` is unrelated local agent tooling (engram/gentle-ai) — not part of the application; ignore it for app work.

## Commands

### Database (`lex-control-api/`)
```bash
pnpm generate        # prisma generate — regenerate the typed client (does NOT touch the DB)
pnpm migrate         # prisma migrate dev — create + apply a migration from schema.prisma
pnpm migrate:deploy  # prisma migrate deploy — apply existing migrations (production/CI)
pnpm push            # prisma db push — sync schema without a migration (prototyping)
pnpm studio          # prisma studio — DB browser GUI
```
`DATABASE_URL` is read from `lex-control-api/.env` (MySQL connection string). After any change to `schema.prisma`, run `pnpm generate` so the typed client matches.

### Frontends (`lex-control-admin/` and `lex-control-client/`)
```bash
pnpm dev    # dev server (admin :3000, client :3001)
pnpm build  # next build
pnpm start  # serve the production build
pnpm lint   # eslint (flat config, eslint-config-next)
```
There is no test setup in any project.

## Architecture

### Data model (`lex-control-api/prisma/schema.prisma`)
The schema is the single source of truth. Core entities and the tenancy model:

- **`Empresa`** — a client company; groups its `Usuario`s and `EmpresaServicio`s.
- **`Usuario`** — has `rol` (`ADMIN` | `CLIENTE`). `ADMIN` = platform staff with `empresaId = null`. `CLIENTE` belongs to an `Empresa`. The `esAdminEmpresa` flag lets a CLIENTE manage other users *within their own company*.
- **`Servicio`** — global service catalog (created by ADMIN). `precioBase` is only a reference price.
- **`EmpresaServicio`** — join of `Empresa`↔`Servicio` carrying the **negotiated `precio`** for that company (may differ from `precioBase`). Unique per `(empresaId, servicioId)`.

Cascade rules matter: deleting an `Empresa` cascades to its `Usuario`s and `EmpresaServicio`s; a `Servicio` is `onDelete: Restrict` so it can't be removed while assigned. All models use `cuid()` string IDs and map to snake_case table names via `@@map`.

This ADMIN-vs-CLIENTE split in the data model is exactly what the two frontends mirror: admin operates across all tenants, client is scoped to one `Empresa`.

### Frontends
Both apps share an identical structure (the client is essentially a scoped variant of the admin):
- Routes live under `src/app/(dashboard)/` — the route group applies the shared `layout.tsx` (sidebar + topbar shell) without adding a URL segment.
- Navigation is data-driven from `src/lib/nav.tsx` (`NAV_ITEMS`), rendered by `src/components/sidebar.tsx`.
- Shared presentational primitives (`PageHeader`, `Button`, `Card`, `StatCard`, `EmptyState`, icons) live in `src/components/ui.tsx`. Build pages by composing these rather than hand-rolling markup.
- Path alias `@/` → `src/`. Styling is Tailwind CSS v4 (via `@tailwindcss/postcss`, configured in `globals.css`).
- **Route transitions (default).** Both portals use the React/Next View Transitions API (`experimental.viewTransition` in `next.config.ts`). `src/app/(dashboard)/template.tsx` wraps page content in `<ViewTransition>`, so **every page under `(dashboard)/` inherits a subtle ~200ms cross-fade on navigation automatically — no per-page wiring**. Motion tokens (`--lex-transition-dur`, `--lex-ease`) + the `@supports` fallback + `prefers-reduced-motion` live in `globals.css`. Keep transitions professional: short (~200ms), `opacity`/`transform` only, consistent easing. For a list→detail "shared element" morph, give the same `view-transition-name` to both ends via the `vtName(scope, id)` helper in `src/lib/view-transition.ts` (e.g. `<ViewTransition name={vtName("proceso", id)}>`). Do **not** add an animation library (no framer-motion) for navigation — it's unnecessary weight.

**Current state:** pages render static/empty placeholder data and `EmptyState`s — they are **not yet wired to the database**. Neither frontend currently depends on `@lex/db`. When connecting them, add `@lex/db` as a dependency and import the `prisma` singleton (Server Components / server actions) rather than instantiating `PrismaClient` directly.
