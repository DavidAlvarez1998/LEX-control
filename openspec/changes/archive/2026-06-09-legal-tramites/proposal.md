# Proposal: Legal Process Module (Trámites) for Despachos

## Intent
The platform manages despachos (COLOMBIAN law firms as `Empresa`) and billing, but lawyers have no
way to run their actual work: legal cases. Lawyers (`Usuario` ADMIN-of-empresa and regular) need to
open and track cases across practice areas (civil, comercial, laboral, administrativo, penal, familia,
constitucional, tributario, inmobiliario, migratorio, seguridad social) under their Colombian
procedural regimes (CGP, CPACA, CPTSS, Ley 906, tutela). Each has many process types, each with its
own intake form and lifecycle. Hardcoding areas × N processes is unmaintainable; the system must be
**metadata-driven** — a configurable catalog of process types carrying dynamic forms and staged
workflows, mirroring how MyCase/Litify/Smokeball model "matter types".

## Scope

### In Scope
- `AreaDerecho` (9 fixed areas) and a `TipoTramite` catalog (process type) carrying a dynamic
  form schema (`esquemaFormulario`), a staged workflow with rules (`etapas`), and document
  templates. Hybrid ownership: global types (ADMIN) + per-despacho types.
- `Tramite` (expediente): created from a `TipoTramite`, holds filled form `datos`, current stage,
  history (`EtapaTramite`), attachments and generated documents (`DocumentoTramite`). Colombian
  first-class fields live as typed columns (not in `datos`): `codigoInterno` (firm number), `radicado`
  (nullable 23-digit court number), `jurisdiccion`, `tipoProceso`, `instancia`, `cuantía` (SMLMV),
  `despachoJuzgado`, `proximaAudiencia`, `estado`, `casoRelacionadoId` (tutela ↔ base case).
- A **curated seeded global catalog** — real Colombian process types (ejecutivo, verbal, ordinario
  laboral, nulidad y restablecimiento, tutela…) with correct CGP/CPTSS/CPACA stages and starter
  templates — so a despacho sees its practice reflected on day one (not an empty catalog).
- `Litigante` (party registry, reusable per despacho; `tipoDocumento` CC/CE/NIT/TI/Pasaporte) linked
  to trámites via `ParteTramite` (procedural rol demandante/demandado/accionante… + `esNuestroCliente`).
- Stage transitions gated by rules (required fields/documents, deadline). Document generation from
  templates with `{{placeholder}}` substitution.
- **UX-first delivery**: build the lawyer flow (pick area → type → dynamic form → expediente) and a
  single generic form renderer in `lex-control-client` against mock data first; wire the backend after.
- **State integrations (later phase)**: an `integrations` module that syncs court **actuaciones** by
  `radicado` into the trámite timeline (idempotent, queued for scrape-grade sources), plus
  jurisprudence lookup. v1 providers only (CPNU, Corte Constitucional, RUES).

### Out of Scope
- Per-trámite billing — trámites are the core product, not metered (catalog `Servicio` unchanged).
- Court-system / external integrations, e-signature, calendaring/notifications engine.
- Contraparte self-service; litigantes are managed only by the despacho.

## Capabilities

### New Capabilities
- `tramite-catalog`: areas + `TipoTramite` with dynamic form schema, staged workflow with rules,
  and document templates; global + per-despacho ownership and visibility.
- `tramite-management`: expediente lifecycle — create from a type, fill+validate the dynamic form,
  rule-gated stage transitions, attach/generate documents, assign responsable.
- `litigantes`: party registry per despacho and linking to trámites with roles.
- `integraciones-estatales`: pulling Colombian state case data (court actuaciones by `radicado`, and
  jurisprudence) behind one normalized provider adapter (`api`/`scrape`/`aggregator`), synced
  idempotently into the trámite timeline. v1 providers: CPNU, Corte Constitucional SODA, RUES.

### Modified Capabilities
- `authentication` (minor, additive): a new `requireEmpresaAdmin` middleware that loads the user and
  checks the existing `esAdminEmpresa` flag (today that flag is stored but never enforced). No change
  to the JWT or existing requirements; tenancy reuses the per-request `req.user.sub` lookup pattern
  (`mi-empresa.router.ts`) — the JWT carries only `{ sub, rol }`.

## Approach
Metadata-driven catalog. A `TipoTramite` stores its form fields and stages as JSON definitions; one
generic `<FormularioDinamico>` renderer and one stage engine serve every area/process. New process
types are catalog rows, not code. Multi-tenant scoping reuses the existing `empresaId null = platform`
pattern. The backend grows the Express API (`api-foundation`) with new modules; frontends consume it.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/prisma/schema.prisma` | Modified | New models/enums (TipoTramite, Tramite, EtapaTramite, DocumentoTramite, Litigante, ParteTramite, PlantillaDocumento) |
| `lex-control-api/src/modules/tramites/*` | New | Catalog + tramite + litigante routers/schemas |
| `lex-control-client/src/app/(dashboard)/tramites/*` | New | Lawyer flow + `<FormularioDinamico>` renderer |
| `lex-control-admin/src/app/(dashboard)/catalogo-tramites/*` | New | Global catalog management |
| `lex-control-api/src/modules/integrations/*` | New | Provider adapters (CPNU/Corte Const./RUES), queue worker, sync |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Dynamic-form JSON drifts from filled `datos` | Med | Version the schema on the tipo; validate `datos` against it server-side (Zod built from schema) |
| Cross-tenant leak of trámites/litigantes | Med | Every query scoped by `empresaId` from the JWT; catalog visibility = global OR own |
| Over-engineering the stage rule engine | Med | Ship informational stages + a small rule set (required fields/docs, deadline); defer complex rules |
| Document generation scope creep | Med | Phase it last; start with text templates + placeholder substitution only |

## Rollback Plan
Purely additive. No existing model or endpoint changes. Revert by dropping the new Prisma models
(a `prisma db push` back), removing the `tramites`/`litigantes` API modules, and deleting the new
frontend routes. Existing auth, empresas, servicios, and billing are untouched.

## Dependencies
- `api-foundation` (Express app, JWT auth middleware, empresa scoping).
- Existing `Empresa`/`Usuario` models and the `empresaId null = platform` tenancy pattern.

## Resolved Decisions
- **Áreas (resuelto):** seed **every area the Colombian state recognizes** in a seeded `AreaPractica`
  table with `tipo` (jurisdicción/especialidad/práctica) + `jurisdiccion` mapping + `activo` flag
  (active picker shows ~10; the rest present-but-inactive). Source: Ley 270/1996 + Acuerdo 201/1997.
- **`areaPractica` ⟂ `jurisdiccion`:** practice label (firm org) vs procedural regime (drives stages).
- **State integrations (resuelto):** v1 = **CPNU** (consulta por radicado → actuaciones, scrape-grade)
  + **Corte Constitucional SODA** (clean public API) + **RUES** via aggregator. Defer SAMAI, SNR/VUR,
  DIAN, RUNT, Registraduría, Migración, and the X-Road/SCD official route.

## Success Criteria
- [ ] A lawyer can pick an área de práctica → process type → fill its dynamic form → create an
      expediente (with `codigoInterno`, optional `radicado`, `despachoJuzgado`, cuantía).
- [ ] One generic renderer drives every process type's form (no per-type frontend code).
- [ ] A despacho sees global catalog types plus its own; never another despacho's trámites/litigantes.
- [ ] Stage transitions are blocked when a stage's required fields/documents are missing; a terminal
      stage closes the trámite.
- [ ] Editing a catalog type does not invalidate in-flight trámites (schema-version pinned).
- [ ] A document is generated from a template (editable draft) with the trámite's data substituted in.
- [ ] The seeded global catalog ships representative process types for each area on first run.
