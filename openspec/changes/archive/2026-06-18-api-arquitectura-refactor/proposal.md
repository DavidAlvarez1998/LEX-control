# Proposal — API architecture refactor (layered, non-breaking, agent-driven)

## Why
`lex-control-api` works and is well tested (424 tests, tsc clean), but it has a
**fat-router architecture**: business logic and data access live inside the
Express routers.

Evidence (2026-06-18):
- Routers total **6,080** lines vs services **474** (~7% of code in a service layer).
- **18 / 18 routers import Prisma directly** — no data-access layer; the multi-tenant
  `empresaId` filter is repeated by hand in every query (a single omission = cross-tenant leak).
- Fattest routers: `procesos` **1,355**, `comercial` **864**, `contable` **520**.
- Domain logic of the proceso engine (`autoavanzarEtapas`, `terminalDecidido`,
  `recomputarTituloLaboral`, stage machine) lives **inside** `procesos.router.ts`.
- No DTO/serializer layer (Prisma models returned almost raw), no structured logging,
  Prisma errors (P2002/P2025) handled ad-hoc per router, no pagination convention.

Strengths to KEEP: feature-modular layout, solid middleware (auth/error/validate/async),
Zod validation at the edge, transactions where needed, broad test suite.

## What
Refactor the API to a **modular layered architecture** (Clean Architecture "light"),
**incrementally** (strangler pattern), one module at a time, **using agents** with a
fixed per-module recipe and an automated verifier. Layers:

```
Router (HTTP)  →  Service (use cases, rules, transactions)  →  Repository (Prisma, tenant-scoped)
                                       ↘ DTO/mapper (response shape)
domain/procesos/  = pure engine (stage machine, plazos, esquema) — no Express, no Prisma
shared/           = logger, error mapping, pagination, tenant context, prisma client
```

## Non-negotiable: do not break anything
This is an **internal refactor with zero external behavior change**.
- **HTTP contract is frozen**: same routes, same request bodies, same response shapes,
  same status codes. The two Next.js frontends MUST keep working unchanged.
- **No DB schema change**, no migration, no seed change.
- **No frontend change** (separate repos; out of scope).
- The **424 existing tests are the safety net** — they assert behavior and MUST stay green
  at every step. A response-shape **contract snapshot** is added as an extra guardrail.

## Scope
- In: `lex-control-api/src` internal structure (router → service → repository → dto),
  `domain/procesos/`, `shared/`, central Prisma-error mapping, structured logging,
  pagination contract (additive/back-compatible), per-module migration.
- Out: NestJS rewrite, hexagonal ports/adapters everywhere, CQRS, DI container,
  frontend changes, DB schema changes. OpenAPI generation is a deferred optional phase.

## Non-goals (avoid over-engineering)
No framework rewrite, no decorators/DI container, no event sourcing. Prisma stays as the
data adapter; repositories wrap it (they are not a portability abstraction).

## Rollback plan
Each module migration is an independent, PR-sized commit that preserves behavior.
- If a module's tests/contract-snapshot fail → the agent's change for that module is
  discarded (worktree isolation) and not merged; the old router stays in place.
- If a merged module regresses later → revert that single commit; other modules are
  unaffected (no shared mutable surface beyond the additive `shared/` layer).
- `shared/` and `domain/` are additive in Phase 0/2: existing code keeps working until a
  module is explicitly switched to use them.

## Success criteria
- Per module: tests green + `tsc` clean + `pnpm --dir lex-control-api build` green + **no
  contract-snapshot diff** + router contains no Prisma calls and no business logic.
- Globally: 0 direct `prisma.` imports in `*.router.ts`; tenant scoping centralized in
  repositories; proceso engine in `domain/` and unit-tested without HTTP/DB.
