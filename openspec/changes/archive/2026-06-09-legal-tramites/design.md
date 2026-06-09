# Design: Legal Process Module (Trámites)

> v3 — **Jurisdiction = COLOMBIA** (Colombian lawyers, Colombian law). Corrects the earlier Mexico
> assumption from the `rfc` field: no amparo (→ acción de tutela), identifiers are CC/CE/NIT/TI/
> pasaporte (no RFC/CURP), civil procedure = Código General del Proceso (Ley 1564/2012), contencioso
> = CPACA (Ley 1437/2011), penal = Ley 906/2004. Revised after adversarial validation (4 agents) +
> Colombian domain research. **[fix]** corrects a validation finding; **[CO]** is a Colombia
> specific; **[decision]** needs product sign-off.

## Decision 1 — Metadata-driven catalog, not code-per-process
**Choice:** A `TipoTramite` stores its form fields (`esquemaFormulario`) and stages (`etapas`) as
JSON. One generic `<FormularioDinamico>` renderer and one stage engine serve every area/process.
**Rationale:** 9+ areas × N processes = dozens of intake forms and workflows. Hardcoding a component
per process does not scale and forces a deploy per new process; the industry (MyCase/Litify/
Smokeball "matter types") is configuration-driven.
**Trade-off:** Weaker compile-time typing of `datos`. Mitigated by validating `datos` server-side
against the schema (Zod built from `esquemaFormulario`) on create and on each stage transition.
**[fix] Genericity risk:** a pure engine feels like a form-builder, not a litigation tool. The
differentiator is (a) a **curated seeded global catalog** with real Colombian process types, stages,
and templates (now a v1 success criterion), and (b) the first-class legal fields below — not buried
in `datos`.

## Decision 2 — Hybrid catalog ownership via nullable `empresaId`
**Choice:** `TipoTramite.empresaId` nullable: `null` = global (ADMIN), set = despacho-owned.
Visibility = global OR own. `origenId` records a despacho cloning a global type.
**[fix] NULL-unique trap:** MySQL/InnoDB treats NULLs as distinct, so `@@unique([empresaId, area,
nombre])` does NOT prevent duplicate global types. Enforce global-type uniqueness in app code
(pre-insert check), and add a non-null sentinel `empresaKey String` (= `empresaId ?? ""`) carrying
the unique `@@unique([empresaKey, area, nombre])`.

## Decision 3 — Litigante as an entity, not form fields
**Choice:** `Litigante` + `ParteTramite` (role) instead of party identity in `datos`.
**[CO] Colombian identifiers:** `Litigante` has `tipoPersona` (NATURAL | JURIDICA), and
`tipoDocumento` ∈ **CC | CE | NIT | TI | PASAPORTE | PEP_PPT** with `numeroDocumento`. **No RFC, no
CURP** (those are Mexican). NIT applies to personas jurídicas (and natural commerciantes).
**[CO][fix] Roles speak the Colombian lawyer's language:** the procedural role depends on the
`tipoProceso`, so `ParteTramite.rol` ∈ **DEMANDANTE | DEMANDADO | EJECUTANTE | EJECUTADO |
ACCIONANTE | ACCIONADO | IMPUTADO | ACUSADO | VICTIMA | TERCERO | APODERADO | OTRO**, plus a free-text
`rolEtiqueta` and `esNuestroCliente Boolean` (which side the despacho represents, independent of the
procedural position). The lawyer of record is modeled as `APODERADO`.

## Decision 4 — Trámites are not metered
**Choice:** The trámites module is decoupled from `Servicio`/`EmpresaServicio` billing.
**[fix] Don't paint into a corner:** acceptable for v1, but leave the door open — no link now, but
do not forbid a future `honorarios`/time entry. Note only.

## Decision 5 — Stage model: linear-by-orden, with terminal outcomes and non-forward moves **[CO]**
**[fix]** Real Colombian processes branch. A strict forward-only list is too naive. v1 keeps an
ordered `etapas` list BUT: (a) a stage MAY be `terminal: true` with a `resultado` that closes the
trámite (e.g. "demanda rechazada", "sentencia favorable"); (b) transitions MAY move backward/sideways
(each target's `reglas` validated independently), not only `orden+1`; (c) `EstadoTramite`
(ABIERTO | EN_PROCESO | SUSPENDIDO | CERRADO | ARCHIVADO) lifecycle is specified. The seeded catalog
encodes the real Colombian stage sets per process, e.g.:
- **Civil verbal (CGP):** demanda → admisión/inadmisión/rechazo → notificación → contestación →
  audiencia inicial (art. 372) → audiencia de instrucción y juzgamiento (art. 373) → sentencia →
  apelación. (Verbal sumario = única instancia, sin apelación.)
- **Ejecutivo (CGP):** demanda con título → mandamiento de pago → notificación + cautelares →
  excepciones → sentencia / seguir adelante la ejecución → liquidación → avalúo → remate.
- **Ordinario laboral (CPTSS):** demanda → contestación → audiencia art. 77 → audiencia art. 80
  (pruebas, alegatos, sentencia) → apelación.
- **Tutela (Dec. 2591/91):** presentación → reparto → fallo (≤10 días) → impugnación → 2ª instancia →
  remisión a revisión Corte Constitucional.
`instancia` (primera/segunda/única/casación/revisión) is tracked on the `Tramite`. Full
branching/substages: deferred. **Rules** stay small: `camposRequeridos`, `documentosRequeridos`,
`plazoDias`.

## Decision 6 — UX-first delivery, building the form primitives the client lacks
**Choice:** Build the lawyer flow + generic renderer in `lex-control-client` against a mock TS
contract that becomes the API contract; wire the backend after.
**[fix] The client app has NO form inputs.** `lex-control-client/src/components/ui.tsx` exports only
`PageHeader, Button, Card, StatCard, EmptyState, PlusIcon`; `Button` takes no `onClick/type/disabled`;
`MoneyInput` exists only in the ADMIN app (client has `formatMoney`/`parseMoneyInput` in `lib/format.ts`
but no component). Phase 1 MUST first build form primitives: `Input, Textarea, NumberInput, DateInput,
Select, MultiSelect (custom — no native control), Checkbox, a Field/Label wrapper (red asterisk),
a clickable card-grid`, port `MoneyInput`, and extend `Button` (`type/onClick/disabled`). Pages are
`"use client"` + `useEffect`+`api.ts` fetch (the established client pattern), so a stateful form fits.

## Decision 7 — Auth & tenancy grounded in the REAL api-foundation
**[fix BLOCKER] The JWT carries only `{ sub, rol }` — NOT `empresaId`.** Every scoped endpoint
resolves the empresa per-request by `prisma.usuario.findUnique({ where: { id: req.user.sub } })`
(see `mi-empresa.router.ts:20-34`). All specs/queries say "scoped to the caller's empresa, resolved
from `req.user.sub`" — never "empresaId from the JWT".
**[fix BLOCKER] `esAdminEmpresa` is a stored boolean never used for authorization and not in the JWT.**
Add a `requireEmpresaAdmin` middleware that loads the user and checks `esAdminEmpresa` (additive to
api-foundation). Authorization matrix (v1):
- Create/read/update trámites & litigantes: any `USUARIO` of the despacho.
- Create/edit/delete **despacho-owned** catalog types: `esAdminEmpresa` only.
- Create/edit/delete **global** catalog types: `Rol.ADMIN` only (`requireRole(ADMIN)`).

## Data model (Prisma additions) — Colombia
- Enums: `Jurisdiccion` (ordinaria-civil, ordinaria-laboral, contencioso-admin, penal, constitucional,
  familia), `Instancia` (PRIMERA | SEGUNDA | UNICA | CASACION | REVISION), `CuantiaTipo` (MINIMA |
  MENOR | MAYOR | SIN_CUANTIA), `EstadoTramite`, `Prioridad`, `TipoPersona` (NATURAL | JURIDICA),
  `TipoDocumento` (CC | CE | NIT | TI | PASAPORTE | PEP_PPT), `RolParte` (see Decision 3).
- `AreaPractica(id, slug @unique, nombre, tipo, jurisdiccion, activo, orden)` — seeded table (Decision 8),
  so areas extend without a `db push`. M:N with `TipoTramite`.
- `TipoTramite(id, jurisdiccion, nombre, descripcion?, esquemaFormulario Json, esquemaVersion Int
  @default(1), etapas Json, empresaId?, empresaKey, origenId?, activo, timestamps)` + `areaPracticas`
  (M:N to `AreaPractica`) — `@@unique([empresaKey, nombre])`, `@@index([empresaId])`,
  `@@index([jurisdiccion])`.
- `Tramite(id, codigoInterno, radicado?, empresaId, tipoTramiteId, tipoEsquemaVersion Int, jurisdiccion,
  tipoProceso, instancia, cuantiaTipo?, cuantiaSmlmv Decimal? @db.Decimal(10,2), cuantiaValor Decimal?
  @db.Decimal(14,2), despachoJuzgado?, casoRelacionadoId?, creadoPorId, responsableId?, titulo,
  datos Json, proximaAudiencia DateTime?, etapaActual, estado, prioridad, timestamps)`
  — `@@unique([empresaId, codigoInterno])`, indexes on `empresaId`, `tipoTramiteId`, `responsableId`,
  `estado`, `radicado`, `casoRelacionadoId`.
  **[CO]** `codigoInterno` = the firm's own case number (always present, per-empresa unique, generated
  in the create `$transaction`). `radicado` = the public 23-digit court number, **nullable** (a matter
  exists before it is filed/assigned). `cuantía` stored as SMLMV multiple + computed pesos (SMLMV
  changes yearly). `casoRelacionadoId` self-FK links a tutela to its base case. `despachoJuzgado` =
  court office. **[fix]** `tipoEsquemaVersion` pins the schema version (drift fix).
- `EtapaTramite(id, tramiteId, etapaKey, nota?, usuarioId, createdAt)` — `@@index([tramiteId])`.
- `DocumentoTramite(id, tramiteId, nombre, url, generadoDePlantillaId?, createdAt)` —
  `@@index([tramiteId])`; `generadoDePlantillaId` `onDelete: SetNull` (deleting a template keeps issued docs).
- `Litigante(id, empresaId, tipoPersona, nombre, tipoDocumento?, numeroDocumento?, email?, telefono?,
  timestamps)` — `@@index([empresaId])`. **[CO]** no `rfc`/`curp`.
- `ParteTramite(id, tramiteId, litiganteId, rol, rolEtiqueta?, esNuestroCliente)` —
  `@@unique([tramiteId, litiganteId, rol])`, `@@index([litiganteId])`.
- `PlantillaDocumento(id, tipoTramiteId, nombre, contenido @db.Text)`.
- **[CO] Integrations (Decision 11):**
  - `ActuacionJudicial(id, tramiteId, provider, providerCaseId?, fechaActuacion, actuacion, anotacion?,
    fechaInicia?, fechaTermina?, hashIdempotencia @unique, rawJson? Json, createdAt)` —
    `@@index([tramiteId])`; system-of-record for synced court events, projected into `EtapaTramite`.
  - `IntegrationSyncLog(id, tramiteId, provider, startedAt, finishedAt?, status, itemsFetched,
    itemsNew, error?)` — `@@index([tramiteId])`.
  - `ProviderConfig(id, empresaId, provider, mode, enabled, encryptedCredentials? @db.Text,
    rateLimitOverride?)` — `@@unique([empresaId, provider])`; per-despacho, credentials envelope-encrypted.
- **[fix] Cascade map (explicit per relation):**
  - `Empresa` → `TipoTramite`(own) / `Tramite` / `Litigante`: `Cascade`.
  - `Tramite` → `EtapaTramite` / `DocumentoTramite` / `ParteTramite`: `Cascade`.
  - `ParteTramite` → `Litigante`: **`Restrict`** (avoid MySQL multi-cascade-path errno 150; the row
    dies via the `Tramite` cascade). Same caution for any second path into a table.
  - `Usuario` → `Tramite.creadoPorId` / `Tramite.responsableId` / `EtapaTramite.usuarioId`:
    **`SetNull`** (these FKs nullable) so deleting a lawyer preserves the caseload/history. Policy:
    prefer deactivating (`activo=false`) over deleting staff.
  - `TipoTramite` → `Tramite`: **`Restrict`** (can't delete a type in use; mirrors `Servicio`).
- All ids `cuid()`, snake_case `@@map`, JSON columns typed `Json`.

## Decision 8 — Split área de práctica from jurisdicción/régimen procesal **[CO][decision]**
Colombian research showed the flat "9 areas" conflates two different things:
- **`areaPractica`** — how a firm organizes/staffs/reports (a label): civil, comercial, laboral,
  administrativo, penal, familia, **constitucional**, **tributario**, inmobiliario, migratorio,
  seguridad social. This is what the lawyer picks first in the UI; cheap to extend.
- **`jurisdiccion`** — the procedural regime that actually drives the **process catalog + stages**:
  ordinaria-civil, ordinaria-laboral, contencioso-administrativa, penal, constitucional, familia.
A `TipoTramite` belongs to a `jurisdiccion` (its stages follow that code) and is *tagged* with one or
more `areaPractica`. Colombian specifics that motivated the split:
- **Seguridad social** is NOT a separate jurisdiction — it litigates as ordinario **laboral** (CPTSS,
  same jueces laborales). Keep it as a practice label routing to laboral.
- **Inmobiliario / migratorio / tributario** are practice labels, not jurisdictions: inmobiliario
  litigation maps to **civil**; migratorio to **contencioso-administrativa**; tributario to
  contencioso-administrativa (DIAN).
- **Comercial vs Civil**: separate practice areas, but both litigate under the **CGP** in the
  jurisdicción ordinaria civil — they share one process catalog.
- **Constitucional** is needed as a home for the acciones constitucionales (next decision).
**[RESOLVED]** Per the product owner: seed **every area the Colombian state recognizes**, as a seeded
`AreaPractica` table (not an enum). Each row has `slug`, `nombre`, `tipo` (JURISDICCION | ESPECIALIDAD
| PRACTICA), `regimenProcesal`/`jurisdiccion` (the mapping that routes to the right stage set), and
`activo` (firm-facing picker shows active ones; the rest stay in the catalog inactive until needed).
This mirrors the state's own two-level structure (Ley 270/1996 jurisdicciones + Acuerdo 201/1997
especialidades — the source of the radicado's 2-digit código de especialidad).
**Seed (active v1, 10):** civil, comercial-societario, laboral (y seguridad social), penal, familia,
administrativo (contencioso), constitucional, tributario-aduanero, restitucion-tierras, disciplinario.
**Seed (present, inactive until demanded):** agrario-rural, insolvencia, propiedad-intelectual,
ambiental, electoral, notarial-registral, migratorio, arbitraje-masc, consumo, penal-adolescentes,
ejecucion-penas, pequenas-causas, jurisdiccion-paz, jurisdiccion-indigena, penal-militar.
`promiscuo`/`pequeñas causas` are court-type attributes, modeled on the court, not as practice areas.
**Mapping areaPractica → jurisdiccion:** ordinaria-civil ← civil, comercial-societario, insolvencia,
propiedad-intelectual, consumo, pequeñas-causas; ordinaria-laboral ← laboral; familia ← familia;
penal ← penal(+adolescentes, ejecución, militar separado); contencioso-admin ← administrativo,
tributario-aduanero, electoral, ambiental, migratorio, notarial-registral; constitucional ←
constitucional; especializada ← restitucion-tierras (Ley 1448), agrario; disciplinaria ← disciplinario.

## Decision 10 — Acciones constitucionales (incl. tutela) as first-class matter types **[CO]**
Colombia has no amparo; instead: **acción de tutela** (by far the highest-volume judicial filing),
acción de cumplimiento, acción popular, acción de grupo, habeas corpus, habeas data. They are
cross-cutting (a tutela can arise out of any matter) and have their own radicado, parties, and fast
lifecycle (fallo ≤10 días → impugnación → eventual revisión en la Corte Constitucional). Therefore a
tutela is its OWN `Tramite` (not buried in a base case) under the `constitucional` jurisdiction, with
an **optional `casoRelacionadoId`** linking it to the originating `Tramite`. Tutela is flagged as a
high-priority, fast-clock type in the UI.

## Decision 11 — State integrations behind one normalized adapter interface **[CO]**
Research (SAMAI + the Colombian judicial/registry stack) found that **almost none of the state
systems expose an open, documented public API** — so the architecture must absorb three transport
modes behind one interface, never leaking provider specifics into the trámite domain.

Findings per system (what's realistic):
- **CPNU — Consulta de Procesos Nacional Unificada** (`consultaprocesos.ramajudicial.gov.co`): the
  single most valuable source (lookup by 23-digit `radicado` → sujetos, despacho, **actuaciones**).
  It has an *undocumented* JSON backend but the WAF deliberately blocks scripted clients → treat as
  **scrape-grade** (queued, headless/header-faithful, low rate). It already unifies TYBA/Justicia XXI,
  so integrate CPNU, not those directly.
- **SAMAI (Consejo de Estado)**: the court's electronic case-file portal for contencioso-administrativo
  before the Consejo de Estado. ASP.NET portal, **no public API** → niche, **defer** (scrape its
  estados only if a client needs it). NOTE: this is unrelated to LEX Control's own billable service
  "IA legal – Lectura de documentos (Samai)" (an AI document-reader feature in `seed.ts`); the shared
  name is coincidental. See Decision 12.
- **Corte Constitucional jurisprudence**: published on **datos.gov.co via a clean public Socrata
  (SODA) REST API** (confirmed live, JSON, no token) → the one genuinely easy API; use for
  sentencia/tutela lookup.
- **RUES (Cámaras de Comercio)**: existencia y representación legal; no open API → via a **commercial
  aggregator** (Apitude/Verifik-class) for empresa-centric trámites.
- **SNR/VUR (certificado de tradición y libertad), DIAN-RUT, RUNT, Registraduría, Migración**: no open
  API (paid portals / captchas) → **defer**; store uploaded artifacts for now.
- **Servicios Ciudadanos Digitales / X-Road (AND)**: the *official* interoperability route, but
  **entity-gated** (requires formal vinculación) and doesn't yet publish rama judicial/SNR/RUES as
  consumable services → strategic, **defer**.

**Architecture:** an `integrations` module in `lex-control-api` with a `ProviderAdapter` interface
(`fetchByRadicado`, `fetchActuaciones`) returning a normalized DTO, and a `mode` flag:
- `api` (Corte Constitucional SODA, aggregators, DIAN-PT) → plain `fetch`/SOAP, retry+backoff.
- `scrape` (CPNU, SAMAI) → enqueue a job (BullMQ/Redis), worker uses Playwright/header-faithful fetch
  with per-host rate limit, jitter, circuit breaker.
**Sync:** on-demand (open a trámite → debounced refresh, cache-gated) + scheduled low-cadence polling
of *active* trámites that have a `radicado`. **Idempotency:** `hashIdempotencia` =
hash(radicado+fecha+actuacion+anotacion) → upsert into `ActuacionJudicial`, then project into
`EtapaTramite` so the existing timeline UI is unchanged. **Caching:** normalized responses with TTL
(actuaciones ~6–12h). **Credentials:** per-despacho `ProviderConfig`, envelope-encrypted (CPNU needs
none; aggregators/DIAN do).
**Compliance:** synced case data is personal data → **Ley 1581/2012 (habeas data)**: privacy policy,
lawful basis (client authorization / legal representation), retention, data-subject rights; respect
portal terms (human-rate, identifying UA, caching) and sign DPAs with aggregators.
**v1:** CPNU (scrape) + Corte Constitucional SODA (api) + RUES (aggregator). **Defer:** SAMAI, SNR/VUR,
DIAN, RUNT, Registraduría, Migración, X-Road.

## Decision 12 — Product "Samai" (AI document reader) vs. judicial SAMAI — disambiguation
LEX Control already sells an internal service, **"IA legal – Lectura de documentos (Samai)"** (an
AI document-reader, billed via `Servicio`/`EmpresaServicio` in `seed.ts`). It is **NOT** the Consejo
de Estado's SAMAI court portal (Decision 11) — the shared name is coincidental and was a source of
confusion. They are different concerns:
- Judicial SAMAI = a **state system** to *read* from (deferred integration, Decision 11).
- Product Samai = an **internal AI feature** that could later *enrich a trámite* — e.g. upload a
  demanda/PDF → AI extracts parties, hechos, cuantía → **prefill the dynamic form's `datos`**. This is
  a product feature on top of the trámites module, separate from state integrations. **Deferred** /
  not in this change's scope; noted as a future hook (it would call the existing Samai service, not a
  government API).
```jsonc
// CampoEsquema (pinned union — client lib + server Zod share it)
{ "key": "monto", "label": "Monto reclamado", "tipo": "numero",
  "requerido": true /*, "opciones": string[] for select|multiselect */ }
// EtapaDef
{ "key": "demanda", "nombre": "Demanda", "orden": 1, "terminal": false,
  "reglas": { "camposRequeridos": ["monto"], "documentosRequeridos": ["Demanda"], "plazoDias": 15 } }
```
`tipo ∈ texto | textoLargo | numero | fecha | boolean | select | multiselect`.
**[fix] `validarDatos(esquema, datos): { ok: boolean; faltantes: string[] }`** — shared pure helper
(client UX + server truth). Server rules: reject keys not in schema (`.strict()`); `fecha` = ISO
string; coerce `numero` from string (`z.coerce.number()`); `multiselect` values ⊆ `opciones`;
unknown `tipo` in a stored schema fails closed. Required labels show a red asterisk and block submit
(per `openspec/config.yaml` apply rule), with per-field error + a missing-fields summary.

## Decision 9 — Document templates: a draft, with a real engine **[CO]**
**[fix]** Flat `{{path}}` + "unresolved → empty" cannot produce filing-ready demandas. A Colombian
demanda (art. 82 CGP) needs partes, pretensiones, hechos numerados, fundamentos de derecho, pruebas,
cuantía and (for títulos valores, art. 623 C.Co) amounts **"en letras"** — so the engine needs
conditionals, loops (over partes/pretensiones/hechos), a number-to-words helper (cuantía en letras,
auto-generated from the numeric field — no manual dual entry), and date formatting. v1 sets the
expectation that generation produces an **editable draft, not a final pleading**, using a template
engine with conditionals/loops/helpers (Handlebars-style or docx-templates). Unresolved placeholders
render a **visible marker**, not a silent blank. Also model the **poder** (especial = documento
privado con presentación personal; general = escritura pública) as a document type with poderdante /
apoderado. Placeholder namespace: `datos.<key>`, `tramite.<field>`, `parte.<rol>.<litiganteField>`.

## Data flow (lawyer create)
1. `/tramites/nuevo` → pick `areaPractica` (card grid) → pick `TipoTramite` (filtered by area tag +
   jurisdiccion + visible).
2. `<FormularioDinamico esquema={tipo.esquemaFormulario}>` renders inputs; validates on submit.
   Inline first-class fields: `radicado?`, `despachoJuzgado?`, `cuantiaTipo?`/`cuantiaSmlmv?`, `instancia`.
3. POST `{ tipoTramiteId, titulo, datos, cuantia?, radicado?, partes[], casoRelacionadoId? }` → server
   (single `$transaction`): resolve empresa from `sub`, validate `datos` against the type's current
   schema, snapshot `tipoEsquemaVersion`, assign per-empresa `codigoInterno`, create trámite +
   `ParteTramite` rows → 201.
4. Expediente view: stage stepper (rule-gated, terminal-aware, instancia-aware), partes, documentos
   (attach + generate), header showing `codigoInterno` / `radicado` / `despachoJuzgado` / `cuantía` /
   `proximaAudiencia`. A tutela shows its `casoRelacionado` link.
