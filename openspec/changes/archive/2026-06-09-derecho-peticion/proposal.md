# Proposal: Derecho de Petición (catalog seed) + deadline & conditional engine

## Intent
The `doc's/DERECHO DE PETICIÓN.docx` roadmap document describes the *derecho de petición* (DdP)
workflow — a constitutional right (Ley 1755/2015): the firm files a petition to an entity, the entity
must answer within a legal term, and if it does not (or answers partially) the firm escalates to an
**acción de tutela**, which itself runs a full lifecycle (demanda → admisión → fallo → impugnación →
segunda instancia).

DdP is **not a new module**: it is a particular case of the existing process catalog
(`tramite-catalog` / `tramite-management`, jurisdicción `CONSTITUCIONAL`). It fits the metadata-driven
model almost 1:1 — entidad/correo (`texto`), tipo de petición (`select`), "¿qué desea?" (`multiselect`),
requiere poder (`boolean`), PDFs (`DocumentoProceso` + `documentosRequeridos`), and a staged workflow
(`etapas`). The escalation to tutela is a **separate** global `TipoProceso` linked via the
already-modeled `Proceso.casoRelacionadoId` ("enlaza una tutela a su caso base").

Three things the generic engine does **not** cover yet, surfaced by the DdP doc but valuable to **every**
process type — so they are solved in the engine, not as a DdP special case:

1. **Computed legal deadline (días hábiles).** The doc requires "Fecha de Vencimiento (automático
   dependiendo del tipo de petición)": radicación + **15 / 10 / 30 días hábiles** (general / documental /
   consulta). Today `fecha` fields are manual; there is no business-day arithmetic (Colombian holidays),
   no derived deadline, and no expiry alerting.
2. **Conditional fields & required-ness.** "Requiere poder = SÍ ⇒ PDF poder obligatorio";
   "Contestaron = PARCIAL ⇒ reiteración"; "= NO ⇒ habilita rama tutela". Today fields are
   unconditionally `requerido` and stages are linear with flat `camposRequeridos`/`documentosRequeridos`.
3. **Stage branching / escalation action.** The DdP flow forks on the "Contestaron" answer and can
   spawn a derived tutela. Today the stage graph allows movement but has no value-driven branching nor a
   first-class "create derived process" action.

## Scope

### In Scope
- **Business-day engine** (new `proceso-vencimientos` capability): a pure Colombian holiday/business-day
  utility (festivos via algorithm — fixed dates + Emiliani-shifted Mondays + Easter-relative days), and a
  stage `plazo` rule that derives a `fechaLimite` on the `Proceso`. A deadline/alerts read endpoint
  (semáforo: al día / por vencer / vencido), mirroring the comercial-alertas pattern.
- **Conditional schema** (modify `tramite-catalog`): `campoEsquema` gains optional `mostrarSi` /
  `requeridoSi` (`{ campo, igualA }`); etapa `reglas` gains conditional required lists and a `plazo`
  definition (incl. `diasPorValorDe` — term that depends on another field's value, e.g. tipoPeticion).
- **Conditional validation & branching** (modify `tramite-management`): `validarDatos` honors conditional
  required-ness; stage transitions can be guarded/offered by a field value; a `crearDerivado` stage
  action opens a related `Proceso` of a target tipo, linked via `casoRelacionadoId`.
- **Seed** (global catalog, jurisdicción `CONSTITUCIONAL`): `TipoProceso` **"Derecho de Petición"** and
  **"Acción de Tutela"** with correct esquemaFormulario, etapas, deadline rules, and conditional rules
  from the doc.

### Out of Scope
- A general formula/expression language for fields (only equality conditions + value-mapped terms).
- Push/email notifications for expiring deadlines (the alerts endpoint returns the semáforo; surfacing is
  a later phase — reuse whatever the comercial-alertas UI established).
- Auto-filing with the actual entity / court integration (still `integraciones-estatales`, deferred).
- Backfilling `fechaLimite` for historical procesos (computed forward only; see rollback).

## Capabilities

### New Capabilities
- `proceso-vencimientos`: Colombian business-day calculator + stage `plazo` rule → `Proceso.fechaLimite`,
  and a deadline-status query (al día / por vencer / vencido).

### Modified Capabilities
- `tramite-catalog`: conditional field visibility/required-ness in `esquemaFormulario`; `plazo` and
  conditional rules in etapa `reglas`. Additive JSON — existing types keep validating unchanged.
- `tramite-management`: `validarDatos` respects conditional required-ness; value-guarded stage
  transitions; a `crearDerivado` action that opens a linked `Proceso` (e.g. DdP → tutela).

## Approach
Keep the metadata-driven core: all new behavior lives in the `esquemaFormulario`/`etapas` JSON plus a
small set of pure helpers (business-day calc, conditional evaluator). The only schema change is an
additive `Proceso.fechaLimite DateTime?` (+ index) so deadlines are queryable for alerts; everything else
is JSON the validators already parse. DdP and Tutela ship as **seeded global rows**, not code.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/prisma/schema.prisma` | Modified | Additive `Proceso.fechaLimite DateTime?` + `@@index` |
| `lex-control-api/src/modules/procesos/esquema.ts` | Modified | Conditional field eval + `plazo` types in rule schema |
| `lex-control-api/src/modules/procesos/diasHabiles.ts` | New | Pure Colombian holiday/business-day calculator |
| `lex-control-api/src/modules/procesos/procesos.router.ts` | Modified | Derive `fechaLimite` on stage move; `crearDerivado`; deadline-status query |
| `lex-control-api/src/modules/catalog/catalog.schemas.ts` | Modified | Zod for `mostrarSi`/`requeridoSi`/`plazo` |
| `lex-control-api/prisma/seed*.ts` | Modified/New | Seed DdP + Acción de Tutela global TipoProcesos |
| `lex-control-client/src/components/*` (dynamic form, expediente) | Modified | Hide/show + conditional-required fields; show fechaLimite/semáforo |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Wrong festivos → wrong legal deadline (lawyer-visible, high stakes) | Med | Algorithmic festivos with an explicit unit-tested table per year; label deadlines "estimado" until verified; allow manual override of `fechaLimite` |
| Conditional rules turn into a mini-language (scope creep) | Med | Only equality (`igualA`) + value→term maps; no AND/OR trees, no arithmetic in v1 |
| Existing types break on the extended schema | Low | All new keys optional; absent ⇒ current behavior; add regression scenario |
| `crearDerivado` duplicates tutelas on repeated clicks | Med | Idempotent: one derived proceso per (origen, tipo destino); link via `casoRelacionadoId`, 409 on repeat |

## Rollback Plan
Additive. Revert by: dropping `Proceso.fechaLimite` (a `prisma db push` back), removing the conditional/
`plazo` keys from the Zod/eval helpers (older JSON simply ignores them), deleting `diasHabiles.ts` and
the deadline-status endpoint, and removing the two seeded global TipoProcesos. In-flight procesos keep
their `datos`/`etapaActual`; only the (nullable) `fechaLimite` disappears.

## Dependencies
- `legal-tramites` (catalog, expediente, etapas engine, documentos/plantillas Fase 4) — this builds on it.
- Existing `Proceso.casoRelacionadoId`/`derivados` relation (already in schema) for DdP → tutela.

## Resolved Decisions (closed 2026-06-09)
- **Festivos source:** ✅ algorithmic (Ley 51/1983 Emiliani-Monday + Easter-relative via Meeus),
  unit-tested against an explicit expected set per year (2024–2027).
- **Deadline override:** ✅ yes — `fechaLimite` is writable; stage-move recompute MUST NOT silently
  clobber a manual edit.
- **Tutela modeling:** ✅ separate global `TipoProceso` linked via `casoRelacionadoId` (matches the
  schema's "tutela ↔ caso base" design; keeps tutela reusable standalone).
- **Área de práctica:** ✅ both DdP and Tutela seed under jurisdicción `CONSTITUCIONAL` + áreaPractica
  `constitucional` (already seeded, orden 7). No constitutional tipo exists yet — these are the first.
- **Deadline rule shape:** ✅ EXTEND the existing `reglas.plazoDias` with
  `plazoDesdeCampo`/`plazoTipoDias`/`plazoDiasPorValorDe` (derive only when `plazoDesdeCampo` present),
  rather than a parallel `plazo` object — keeps the 209 seeded tipos validating unchanged.

## Success Criteria
- [ ] DdP and Acción de Tutela exist as seeded global `TipoProceso` (CONSTITUCIONAL) usable by any despacho.
- [ ] Filing a DdP with tipo "Documental" sets `fechaLimite` = radicación + 10 días hábiles (festivos honored).
- [ ] "Requiere poder = SÍ" makes the poder PDF a blocking required document; "NO" does not.
- [ ] "Contestaron = NO" offers escalation; `crearDerivado` opens a linked Acción de Tutela
      (`casoRelacionadoId` set) and is idempotent.
- [ ] A deadline-status query buckets the despacho's procesos into al día / por vencer / vencido.
- [ ] Pre-existing process types (no conditional/plazo keys) validate and transition exactly as before.
