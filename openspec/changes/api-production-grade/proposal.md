# Proposal — API production-grade (4-track program)

## Why
After the layered-architecture refactor (`api-architecture` spec), the API is well-structured
but still has gaps to be production-grade. The user approved closing them ALL via SDD
(2026-06-18), one track at a time, each with a verification gate and a checkpoint. This change
is the **umbrella record** of the program: scope, status, and design decisions live here so the
plan is in OpenSpec, not only in scratch memory.

## What — the four tracks (by leverage)

1. **Migrations baseline + CI** — `ops-migraciones-ci`. ✅ DONE.
   The shared DB was managed by `db push` (no history). Adopt it into Prisma Migrate via the
   official baseline (no data touched) and add a CI gate on all three repos.

2. **Type-safe data layer** — migrate the 95 `as never` casts in the repositories (and the few
   in services) to generated Prisma input types (`Prisma.*Input`, enums). ✅ DONE.
   Restores the type-safety net in the only layer that touches Prisma.

3. **Pagination end-to-end + OpenAPI** — ⏳ PENDING. Uniform `{items,total,page,pageSize}`
   envelope across all heavy listings (today only `procesos`); generate an OpenAPI document
   from the existing Zod schemas and share generated types with the two frontends so they stop
   re-declaring the contract. **Touches the frontend — coordinate.**

4. **Data integrity + observability** — ⏳ PENDING. Transaction boundaries
   (`autoavanzarEtapas`, parte+recompute), idempotency (`registrarPago`), request-id propagation
   (AsyncLocalStorage), metrics, error tracking, graceful shutdown. Also: modernize the
   Prisma-coupled test mocks to unblock the deferred method-level fixes (`findByIdConItems`
   scoping, `generarCodigoInterno` race — already specified in `api-hardening`).

## Non-goals
- No HTTP-contract changes in tracks 1–2 (frontends unaffected). Track 3 is the first that
  coordinates with the frontend. No data-touching schema changes.

## Rollback
Each track is independently revertible. Track 1: drop `prisma/migrations/` + the `_prisma_migrations`
baseline row; CI is additive. Track 2: type-only changes (compile-time), revert the commits.
