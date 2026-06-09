# Proposal: Integraciones estatales (consulta de datos judiciales) — v1

## Intent
Carve out the "Phase 5" of `legal-tramites` (state integrations) into its own change. The canonical
spec already exists (`openspec/specs/integraciones-estatales/`): pull Colombian state case data —
court **actuaciones** by `radicado`, jurisprudence, and company existence/representation — behind one
normalized `ProviderAdapter`, synced idempotently into the proceso timeline. This change implements it,
**phased by feasibility**, because the three v1 providers have very different infrastructure needs.

## Reality check (why phased, and what's blocked here)
| Provider | Mode | Infra needed | Feasible now? |
|----------|------|--------------|---------------|
| **Corte Constitucional** (datos.gov.co Socrata SODA) | `api` | none — free public REST | ✅ yes — start here |
| **CPNU** (consulta de procesos → actuaciones) | `scrape` | Redis + BullMQ queue + Playwright worker, per-host rate limit, circuit breaker; NEVER inline | ❌ needs infra not in this env |
| **RUES** (existencia/representación legal) | `aggregator` | per-despacho **paid** API key (Apitude/Verifik-class), encrypted in `ProviderConfig` | ❌ needs paid credentials |

So v1 ships the **Corte Constitucional** adapter end-to-end; CPNU and RUES land later once Redis/
Playwright and aggregator contracts exist.

## Scope

### Phase A — Foundation + Corte Constitucional (feasible now)
- `modules/integraciones`: `ProviderAdapter` interface (`mode`, normalized DTO) + a stateless
  **Corte Constitucional** adapter over the Socrata SODA REST API (jurisprudence/tutela lookup).
- `GET /integraciones/jurisprudencia?q=` (despacho-scoped, requireAuth) → normalized results.
- Unit tests mocking `fetch` (no live network in CI), documenting the real endpoint.
- No schema change in Phase A (stateless lookup).

### Phase B — Persistence + sync engine (needs schema window)
- Models `ActuacionJudicial`, `IntegrationSyncLog`, `ProviderConfig` (encrypted creds).
- Idempotent upsert by `hashIdempotencia`; project into `EtapaProceso` timeline; cache TTL;
  on-demand (debounced) + scheduled poll; write `IntegrationSyncLog`.
- ⚠️ **Blocked until the parallel contratos/documentos schema work is committed** — `schema.prisma`
  currently carries uncommitted parallel changes; adding models now would entangle commits.

### Phase C — CPNU scrape (needs Redis + Playwright)
- BullMQ/Redis queue + Playwright worker; per-host rate limit + circuit breaker; never inline.

### Phase D — RUES aggregator (needs paid keys)
- Adapter + per-despacho encrypted API key in `ProviderConfig`.

### Out of Scope (v1)
- SAMAI, SNR/VUR, DIAN, RUNT, Registraduría, Migración, the X-Road/SCD official route.

## Compliance
Ley 1581/2012 (habeas data): lawful basis, delete synced data when a proceso is deleted, identifying
User-Agent + caching, DPA with aggregators, respect portal ToS. Client: "Actualizar desde el juzgado"
button + actuaciones on the timeline.

## Rollback Plan
Phase A is additive (one module + one read endpoint, no schema). Later phases drop their models via
`prisma db push` back and remove the queue worker.

## Dependencies
- `legal-tramites` (Proceso/EtapaProceso, radicado) — ARCHIVED, specs canonical.
- Phase B blocked on the in-flight contratos/documentos schema work landing first.
- Phases C/D blocked on Redis/Playwright infra and aggregator contracts respectively.

## Success Criteria (Phase A)
- [ ] A lawyer can look up Corte Constitucional jurisprudence by query; results normalized.
- [ ] Adapter unit-tested (mocked fetch); real SODA endpoint documented.
- [ ] One `ProviderAdapter` interface that CPNU/RUES will implement later without API changes.
