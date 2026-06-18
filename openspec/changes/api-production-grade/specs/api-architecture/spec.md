# API Architecture Specification — delta (api-production-grade)

## ADDED Requirements

### Requirement: Type-safe data layer (no `as never`)
Repositories MUST type their write/read inputs with the generated Prisma types
(`Prisma.<Model>UncheckedCreateInput`, `UncheckedUpdateInput`, `UncheckedUpdateManyInput`,
`CreateManyInput`, `<Model>WhereInput`) and enum types from `@prisma/client`. The `as never`
escape hatch MUST NOT be used in repositories. Because repositories pass scalar foreign keys
(e.g. `empresaId`), the `Unchecked` input variants are the correct choice. When a repository
injects a fixed field, the parameter MUST omit it (e.g. `Omit<Prisma.XUncheckedCreateInput,
"empresaId">`). This change is type-only: it MUST NOT alter runtime behavior or which Prisma
method is invoked.

#### Scenario: A repository write is typed, not cast
- GIVEN any `<feature>.repository.ts` method that creates or updates a record
- WHEN its data parameter is declared
- THEN it uses a `Prisma.*Input` type (not `Record<string, unknown>` + `as never`)

#### Scenario: Existing tests remain green after the migration
- GIVEN the unit tests that mock the Prisma singleton by method name
- WHEN the repositories are retyped (compile-time only)
- THEN the suite still passes unchanged (no runtime/method change)

### Requirement: Schema changes are versioned migrations
Database schema evolution MUST be captured as Prisma migrations under `prisma/migrations/`,
applied in production with `prisma migrate deploy`. The existing shared database is adopted via
the official baseline (`migrate diff --from-empty` + `migrate resolve --applied`) without
executing SQL or touching data. `prisma migrate dev` MUST NOT be run against the shared/production
database (it resets on drift → data loss); `db push` MAY be used only for local prototyping.

#### Scenario: Shared DB is managed by Migrate
- GIVEN the shared database
- WHEN `prisma migrate status` is run
- THEN it reports the schema is up to date (baseline `0_init` applied), not "not managed by Prisma Migrate"

#### Scenario: A new schema change ships as a migration
- GIVEN a change to `schema.prisma`
- WHEN it is prepared for deployment
- THEN a migration is authored (e.g. via `migrate diff` offline) and applied with `migrate:deploy`, not `migrate dev`

### Requirement: Continuous integration gate
Each repository MUST run a CI pipeline (GitHub Actions) on push and pull request. The API pipeline
MUST run `prisma generate` + `tsc` build and the test suite against an ephemeral database; the
frontends MUST run `lint` + `build`.

#### Scenario: CI blocks a broken build
- GIVEN a pull request that fails type-check, build, or tests
- WHEN CI runs
- THEN the pipeline fails and the regression is surfaced before merge
