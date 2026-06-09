# Integraciones Estatales Specification

## Purpose
Define how LEX Control pulls case data from Colombian state systems into a trámite — primarily court
**actuaciones** by `radicado` — behind one normalized provider interface, so the trámite domain never
depends on a specific provider. Most Colombian state systems have no open public API, so the design
must support `api`, `scrape`, and `aggregator` transports uniformly.

## Requirements

### Requirement: Normalized provider adapter
Each integration MUST be implemented as a `ProviderAdapter` exposing `fetchByRadicado` and
`fetchActuaciones`, returning a normalized DTO independent of the provider, and declaring a `mode`
(`api` | `scrape` | `aggregator`). The trámite/UI layer MUST consume only the normalized shape.

#### Scenario: Provider results are normalized
- GIVEN the CPNU (scrape) and Corte Constitucional (api) adapters
- WHEN each returns results for a query
- THEN both produce the same normalized DTO shape consumed by the trámite timeline

### Requirement: Sync actuaciones by radicado, idempotently
For a `Tramite` that has a `radicado`, the system MUST fetch its actuaciones and upsert them into
`ActuacionJudicial` keyed by `hashIdempotencia` = hash(radicado + fechaActuacion + actuacion +
anotacion), so re-syncing the same event MUST NOT create a duplicate. Each new actuación MUST be
projected into the trámite's `EtapaTramite`/timeline. Each sync run MUST record an
`IntegrationSyncLog` (status, itemsFetched, itemsNew, error).

#### Scenario: Re-sync does not duplicate
- GIVEN a radicado whose actuaciones were already synced
- WHEN the same actuaciones are fetched again
- THEN no duplicate `ActuacionJudicial` rows are created and `itemsNew` is 0

#### Scenario: New actuación appears on the timeline
- GIVEN a synced trámite and a newly published actuación at the court
- WHEN the next sync runs
- THEN a new `ActuacionJudicial` is stored AND it appears in the trámite timeline

#### Scenario: Trámite without radicado is not synced
- GIVEN a trámite whose `radicado` is null
- WHEN a sync is requested
- THEN no provider call is made and the request is a no-op

### Requirement: Sync triggers and rate protection
The system MUST support on-demand sync (debounced, served from cache within its TTL) and scheduled
low-cadence polling limited to active trámites with a `radicado`. `scrape`-mode providers MUST run
through a queue with per-host rate limiting and MUST NOT be called inline on a user request.

#### Scenario: On-demand served from cache
- GIVEN actuaciones synced within the cache TTL
- WHEN a user opens the trámite
- THEN cached data is shown and no new provider call is made

### Requirement: Per-despacho provider configuration and credentials
Provider settings MUST live in `ProviderConfig` scoped by `empresaId`. Credentials (for aggregator/
API providers) MUST be stored encrypted (never plaintext). A provider MUST be skipped when disabled
for that despacho.

#### Scenario: Disabled provider is skipped
- GIVEN a despacho with the RUES provider disabled
- WHEN a sync that would use RUES runs
- THEN RUES is not called

### Requirement: Tenant scoping of synced data
`ActuacionJudicial`, `IntegrationSyncLog`, and `ProviderConfig` MUST be reachable only through the
owning despacho's trámite (resolved from `req.user.sub`). A despacho MUST NOT read another despacho's
synced data.

#### Scenario: Cross-tenant sync data blocked
- GIVEN actuaciones synced for a trámite of despacho B
- WHEN a USUARIO of despacho A requests them
- THEN the response status is 404

### Requirement: Compliance with habeas data
Synced personal data MUST be handled under Ley 1581/2012: a lawful basis (client authorization /
legal representation) MUST exist, and the despacho MUST be able to delete a trámite's synced data on
request. Provider access MUST respect each portal's terms (human-rate, caching).

#### Scenario: Delete synced data
- GIVEN a trámite with synced actuaciones
- WHEN the despacho deletes the trámite
- THEN its `ActuacionJudicial` rows are removed
