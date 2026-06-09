# Tasks: Legal Process Module (Trámites)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1200–1800 across 3 projects |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (UX prototype) → PR 2 (data layer) → PR 3 (catalog/back-office) → PR 4 (docs) |
| Delivery strategy | UX-first, chained |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes (approve UX prototype before wiring backend)
Chained PRs recommended: Yes
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Client UX prototype: área → tipo → dynamic form → expediente, mock data | PR 1 | No backend; validates flow |
| 2 | Prisma models + Express API (catalog read, tramites, litigantes) | PR 2 | Implements the mock contract |
| 3 | Admin global catalog management + form/stage builder | PR 3 | Depends on Unit 2 |
| 4 | Document templates + generation | PR 4 | Last; placeholder substitution |

## Phase 1: Client UX prototype (mock data) — UX-FIRST

> NOTE (from validation): `lex-control-client/src/components/ui.tsx` has NO form inputs, its `Button`
> takes no `onClick/type/disabled`, and `MoneyInput` exists only in the ADMIN app. Phase 1 must BUILD
> the primitives first — it is not "reuse existing primitives".

- [x] 1.0 Build form primitives in client `ui.tsx`: `Input`, `Textarea`, `NumberInput`, `DateInput`, `Select`, `MultiSelect` (custom — no native control), `Checkbox`, a `Field`/`Label` wrapper (renders the required red asterisk), and a clickable `card-grid`. Port `MoneyInput` from admin (depends only on the client's existing `lib/format.ts`). Extend `Button` to forward `type`, `onClick`, `disabled` (+ disabled styling). All `"use client"`.
- [x] 1.1 Define the TS contract in `lex-control-client/src/lib/tramites.ts` — pinned unions matching the specs (COLOMBIA): `AreaPractica` (seeded), `Jurisdiccion`, `Instancia`, `CuantiaTipo`, `TipoDocumento` (CC|CE|NIT|TI|PASAPORTE|PEP_PPT), `CampoEsquema = { key; label; tipo: 'texto'|'textoLargo'|'numero'|'fecha'|'boolean'|'select'|'multiselect'; requerido: boolean; opciones?: string[] }`, `EtapaDef` (+ `terminal`/`reglas`), `TipoTramite` (jurisdiccion + areaPracticas), `Tramite` (incl. `codigoInterno`, `radicado?`, `jurisdiccion`, `tipoProceso`, `instancia`, `cuantiaTipo?`, `cuantiaSmlmv?`, `despachoJuzgado?`, `proximaAudiencia?`, `casoRelacionadoId?`, `estado`), `Litigante` (`tipoPersona` NATURAL|JURIDICA, `tipoDocumento?`, `numeroDocumento?`), `ParteTramite` (`rol` demandante/demandado/accionante/imputado/víctima/apoderado…, `rolEtiqueta?`, `esNuestroCliente`). This becomes the API contract.
- [x] 1.2 Mock catalog: 1–2 `TipoTramite` per area (esquemaFormulario + etapas) in a fixtures module.
- [x] 1.3 `shared validarDatos(esquema, datos): { ok: boolean; faltantes: string[] }` (pure) — the exact helper the server reuses in Phase 2.
- [x] 1.4 `<FormularioDinamico esquema value onChange>` (`"use client"`): render each `tipo` via the 1.0 primitives; required labels show the red asterisk; on submit call `validarDatos`, block when `!ok`, show per-field errors + a missing-fields summary (honors the `config.yaml` apply rule).
- [x] 1.5 Route `(dashboard)/tramites/nuevo`: área de práctica picker (card grid) → tipo picker filtered by area tag + jurisdiccion + visibility (`empresaId === null || own`, mock) → `<FormularioDinamico>` + inline `radicado`/`despachoJuzgado`/`cuantiaTipo`+`cuantiaSmlmv`/`instancia` fields.
- [x] 1.6 Route `(dashboard)/tramites/[id]` (expediente): header (codigoInterno / radicado / despachoJuzgado / cuantía / próxima audiencia / estado; tutela shows casoRelacionado), stage stepper (rule-gated + terminal-aware + instancia-aware, with "why blocked" messaging), partes sub-form (litigante picker/creator + tipoDocumento + rol + esNuestroCliente), documentos placeholder.
- [x] 1.7 Route `(dashboard)/tramites` list (filters by areaPractica/jurisdiccion/estado/responsable, mock). Add "Trámites" to `lib/nav.tsx`. `pnpm --dir lex-control-client build` clean.

## Phase 2: Data layer + API (implements the contract)

- [x] 2.1 `schema.prisma`: add enums (Jurisdiccion, Instancia, CuantiaTipo, EstadoTramite, Prioridad, TipoPersona, TipoDocumento, RolParte) + models (AreaPractica seeded table, TipoTramite, Tramite, EtapaTramite, DocumentoTramite, Litigante, ParteTramite, PlantillaDocumento) with Colombian first-class columns (codigoInterno, radicado, cuantía, etc.), indexes/cascade per design (Usuario→Tramite SetNull; ParteTramite→Litigante Restrict; empresaKey sentinel; per-empresa codigoInterno). `pnpm push` + `pnpm generate`.
- [x] 2.2 `modules/tramites/tramites.schemas.ts`: Zod for create/update + a `validarDatosContraEsquema(esquema, datos)` mirroring the client helper.
- [x] 2.3 `modules/catalog/catalog.router.ts`: GET areas; GET `/tipos-tramite` scoped to global+own; schema/etapas validation on write (unique keys, select opciones, rule refs).
- [x] 2.4 `modules/tramites/tramites.router.ts`: POST (validate datos, assign folio, entry stage, scope by JWT empresaId), GET list/by-id (tenant-scoped → 404 on miss), PATCH stage transition (rule-gated, append EtapaTramite), assign responsable (same-despacho check).
- [x] 2.5 `modules/litigantes/litigantes.router.ts`: CRUD scoped by empresaId; link/unlink ParteTramite with role + same-despacho check + unique (tramite,litigante,rol).
- [x] 2.6 Swap client mock fixtures for live `fetch` to the API. Keep the TS contract as the boundary.
- [x] 2.7 `tests/tramites.test.ts`, `tests/litigantes.test.ts`: scoping/isolation, datos validation, rule-gated transitions, cross-despacho rejection.

## Phase 3: Admin global catalog management

- [x] 3.1 `modules/catalog` ADMIN endpoints: create/edit/delete global `TipoTramite` (empresaId null), 403 for non-ADMIN.
- [x] 3.2 `lex-control-admin` route `catalogo-tramites/`: list by area; form/stage builder (add fields, pick tipo, define stages + rules). Reuse `ui.tsx`. Add to admin `nav.tsx`.
- [x] 3.3 Seed the AreaPractica table + the initial global catalog: representative Colombian tipos with real stages (civil ejecutivo/verbal/verbal sumario/sucesión/pertenencia; laboral ordinario/ejecutivo/fuero sindical; administrativo nulidad y restablecimiento/reparación directa/controversias contractuales; familia alimentos/custodia/divorcio; penal audiencias; constitucional tutela/cumplimiento/popular/grupo) (script in `lex-control-api`).

## Phase 4: Document templates + generation

- [x] 4.1 `PlantillaDocumento` CRUD on a tipo (API: nested `/catalogo/tipos-proceso/:id/plantillas` + `/catalogo/plantillas/:id`; admin builder "Plantillas" modal). Stage `documentosRequeridos` now enforced in `PATCH /procesos/:id/etapa` (blocks 400 listing `documentosFaltantes`, name-match case-insensitive).
- [x] 4.2 Generation: real Handlebars-style engine (`procesos/plantilla.ts`) — vars (`datos.*`, `proceso.*`/`tramite.*`, `parte.<rol>.*`), `#if/#each`, helpers (`moneda`, `enLetras`, `fecha`, `mayus`); unresolved → visible marker `[[falta: …]]` (never fails). POST `/procesos/:id/documentos/generar` persists `DocumentoProceso.contenido` (editable draft); PATCH edits it; POST `/procesos/:id/documentos` attaches by link.
- [x] 4.3 Client expediente: `<DocumentosProceso>` — list, generate from type's templates, attach by link, edit draft inline, delete. Wired into `/procesos/[id]`.

## Phase 5: State integrations (v1 providers) — separate later deliverable

- [ ] 5.1 `modules/integrations`: `ProviderAdapter` interface (`fetchByRadicado`, `fetchActuaciones`, `mode`) returning a normalized DTO; models `ActuacionJudicial`, `IntegrationSyncLog`, `ProviderConfig` (encrypted creds).
- [ ] 5.2 **Corte Constitucional** adapter (`mode:'api'`) — datos.gov.co Socrata SODA REST (jurisprudence/tutela lookup). Lowest effort, real API.
- [ ] 5.3 **CPNU** adapter (`mode:'scrape'`) — consulta por `radicado` → actuaciones; queue (BullMQ/Redis) + Playwright/header-faithful worker, per-host rate limit, circuit breaker. NEVER inline on a request.
- [ ] 5.4 Sync engine: idempotent upsert into `ActuacionJudicial` by `hashIdempotencia`; project into `EtapaTramite`; cache TTL; on-demand (debounced) + scheduled poll of active radicados; write `IntegrationSyncLog`.
- [ ] 5.5 **RUES** adapter (`mode:'aggregator'`) — existencia y representación legal via Apitude/Verifik-class; per-despacho encrypted API key in `ProviderConfig`.
- [ ] 5.6 Compliance: Ley 1581/2012 — lawful basis, delete-synced-data on trámite delete, identifying UA + caching; DPA with aggregators. Client: "Actualizar desde el juzgado" button + actuaciones on the timeline.

## Phase 6: Verify

- [ ] 6.1 `pnpm --dir lex-control-api build` clean; API tests pass.
- [ ] 6.2 `pnpm --dir lex-control-client build` and `lex-control-admin` tsc clean.
- [ ] 6.3 Manual: two despachos cannot see each other's trámites/litigantes/own-catalog/synced data; rule-gated transition blocks correctly; document generates with data; CPNU sync upserts actuaciones idempotently into the timeline.
