# Design — API production-grade

## Decisions & discoveries (the "memory" of the program)

### Track 1 — Migrations baseline (no data loss)
- **Problem:** the shared/prod DB (`LEX` at `DEMO-ROUTER`) was never managed by Prisma Migrate
  (`migrate status` → "not managed by Prisma Migrate"). `prisma migrate dev` (`pnpm migrate`)
  **resets** the DB on drift → data loss.
- **Decision:** adopt the existing DB via the official baseline, NOT a fresh migrate:
  1. `prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script`
     → `prisma/migrations/0_init/migration.sql` (50 tables), generated **offline**.
  2. `prisma migrate resolve --applied 0_init` → records the baseline row in `_prisma_migrations`
     **without executing the SQL** (DB schema and data untouched).
- **Rule (documented in `lex-control-api/MIGRATIONS.md`):** never run `migrate dev` against the
  shared DB. New migrations are authored with `migrate diff` (offline) and applied with
  `migrate:deploy`. `db push` stays for local prototyping only.

### Track 1 — CI
- One workflow per repo (each submodule is a separate GitHub repo). API: build (`prisma generate`
  + `tsc`) + tests against an **ephemeral MySQL service container** seeded via `db push` +
  `seed:foundations` + `seed:catalogo`. Frontends: `lint` + `build`. Node 22, pnpm.

### Track 2 — Type-safe data layer (key insight)
- **Insight that unblocked it:** replacing `as never` with `Prisma.*Input` is a **compile-time-only**
  change. It does not alter runtime behavior nor which Prisma method is called, so the
  method-name-coupled test mocks (`vi.mock("../src/index")`) stay intact. The earlier assumption
  that mocks had to be modernized FIRST was wrong — that is only needed for *method* changes
  (e.g. `findUniqueOrThrow`→`findFirstOrThrow`), which are deferred to Track 4.
- **Pattern applied (95 repo casts + 8 service casts):**
  - Repos pass scalar FKs (e.g. `empresaId`) → use the `Unchecked` variants:
    `Prisma.<Model>UncheckedCreateInput` / `UncheckedUpdateInput`.
  - `updateMany` → `UncheckedUpdateManyInput`; `createMany` → `CreateManyInput`.
  - When the repo injects a fixed field (`{ ...data, empresaId }`), the param is
    `Omit<Prisma.<Model>UncheckedCreateInput, "empresaId">`.
  - Enum `where` filters where the param is a plain `string` → `value as <Enum>`.
- **Left intentionally (3 hard casts):** `contable.service` money helper `n(d as never)` (belongs
  to the `shared/money` dedup item) and `procesos.service` ×2 DTO-boundary casts
  (`toProcesoListItem`/`toCasoNodo(p as never)`), which need the DTO param typed to the exact
  Prisma include payload.
- **Execution:** the 8 large repos were migrated by 8 parallel subagents (one file each) with the
  proven recipe; the small repos by hand. Gate after each batch: `tsc` exit 0 + 442/442 tests.

### Tracks 3–4 — open design questions (to resolve when started)
- Pagination envelope shape must be agreed with the frontends before rollout (Track 3).
- OpenAPI: generate from Zod with `@asteasolutions/zod-to-openapi`; serve Swagger at `/docs`;
  emit shared TS types for both portals.
- Idempotency key strategy for `registrarPago` (header vs derived natural key) — TBD in Track 4.
