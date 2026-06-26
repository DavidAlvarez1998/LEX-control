# Design: Rama-driven ficha autofill + actuaciones timeline

## Context

- Rama HTTP client (`rama-judicial.client.ts`) already returns, per radicado:
  `consultarRadicado` (despacho, fechas, sujetos string), `obtenerActuaciones`
  (full paged list: `actuacion`, `anotacion`, `fechaActuacion`, `consActuacion`,
  `conDocumentos`), `obtenerSujetos`, `obtenerDetalle`, `obtenerDocumentos`.
- `actuaciones.service.ts > sincronizarProceso` already: dedupes by `huella`, inserts
  new actuaciones, caches `idProcesoRama`, autofills `juzgado` + `fechaRadicacion`
  (via `fijar()` = set only if empty), emails novedades.
- `hitos-actuaciones.ts > detectarHitos` emits suggestions from a hardcoded `REGLAS`
  array, title-only, one per stage.
- `procesos.service.ts > moverEtapa` advances a stage and **enforces**
  `camposRequeridos` + `documentosRequeridos` (unless the move is a *retroceso*).
- `Proceso.etapaActual: String` (stage key); `tipoProceso.etapas` is the ordered
  stage list with `orden`, `reglas`, `disponibleSi`, `terminal`.

## Decision 1 — Mapping is data, per tipo (`mapeoActuaciones`)

Add an optional `mapeoActuaciones` array to each tipo's schema (stored in the DB
`tipoProceso`, mirrored in `seed-tipos.json`). Shape:

```jsonc
"mapeoActuaciones": [
  {
    "etapaKey": "terminacion",
    "fechaCampo": "fechaTerminacion",            // optional date field to prefill
    "actuacion": ["TERMINA", "ARCHIVO"],          // OR-match on the title
    "anotacion": ["PAGO"],                         // optional OR-match on free text
    "excluir": ["NIEGA", "TRASLADO", "SOLICITUD"], // negation: any hit => rule skipped
    "valorCampo": "modoTerminacion",               // optional non-date field
    "valor": "Pago"                                // value for valorCampo
  },
  { "etapaKey": "notifCautelares", "fechaCampo": "fechaCautelares",
    "actuacion": ["CAUTELAR", "EMBARGO"] },
  { "etapaKey": "audiencia", "fechaCampo": "fechaSentencia",
    "actuacion": ["SEGUIR ADELANTE", "SENTENCIA"], "excluir": ["NIEGA"] }
  // ...mandamiento, calificacion (admite/inadmite), liquidacionCredito, avaluoRemate
]
```

**Matching rules** (in `hitos-actuaciones.ts`, rewritten):
- Normalize (`NFD` strip-accents, uppercase) both `actuacion` and `anotacion`.
- A rule matches an actuación when **(any `actuacion` kw ∈ title OR any `anotacion`
  kw ∈ anotacion) AND no `excluir` kw ∈ (title + anotacion)**.
- `excluir` is what kills the `NIEGA terminación` / `traslado solicitud terminación`
  false-positives.
- Order matters: list more specific rules first (e.g. `INADMIT` before `ADMIT`).
- A rule only produces output if its `etapaKey` exists in the tipo's `etapas` and
  (for `fechaCampo`/`valorCampo`) the field exists in the schema and is empty in
  `datos` — same guard as today, so we never re-suggest filled data.

**Why data, not code:** the current `REGLAS` already drifted out of sync with the
ejecutivo stages (the `impulsos` bug). Keeping the mapping next to the stages it
references — in the same schema the lawyer already edits — makes drift self-evident
and lets every tipo own its mapping. Consistent with the catálogo being data-driven.

Backward-compat: if a tipo has **no** `mapeoActuaciones`, fall back to the legacy
built-in `REGLAS` for the ejecutivo (one release), then delete the array once the
ejecutivo is seeded. New tipos with no mapping = no autofill/positioning (safe).

## Decision 2 — Derivation pass returns a full plan, applied in one tx

Introduce `derivarDesdeActuaciones(actuaciones, tipo, datos)` →
```ts
{
  campos: Record<string, string>,   // every field to fijar() (dates + decisions)
  etapaDestino: string | null,      // furthest reached etapaKey by stage `orden`
  hitos: SugerenciaHito[],          // for the timeline UI / email / audit
}
```

- `etapaDestino` = the matched stage with the **highest `orden`** that is `> orden(etapaActual)`
  and whose `disponibleSi` evaluates true against the (post-autofill) `datos`. Never
  moves backward automatically (a retroceso is a human/manual decision).
- `sincronizarProceso` applies `campos` via the existing `fijar()` (only-if-empty),
  then, if `etapaDestino`, calls **`posicionarEtapaPorRama`** (Decision 3).
- All inside the existing post-insert update so one sync = one consistent write.

## Decision 3 — Stage positioning is DISABLED by default (court record ≠ firm workflow)

**Update (post-implementation, validated against real radicados):** auto-positioning
the firm's `etapaActual` from the Rama is **off by default** (`RAMA_AUTOPOSICION=off`).
Rationale: the actuaciones describe what the **court** did, not which documents the
**firm** holds. Positioning the stage from the court record (a) skips the intermediate
stages where the firm's documents should be uploaded/tracked, and (b) closes processes
(`estado = CERRADO`) while prior documents are still missing — e.g. a radicado that the
court already terminated jumps straight to "Terminación" with most of its paperwork
absent. The court's status is surfaced *informationally* (actuaciones timeline +
`EstadoJuzgado` panel), decoupled from the firm's workflow stage, which the lawyer
advances manually when they actually have the docs.

The mechanism below stays in the code as an **opt-in** (`RAMA_AUTOPOSICION=on`) for
future, smarter use (e.g. position only with docs present, never to terminal stages).
The **autofill of dates/decisions remains always on** — those are facts, only fill
empty fields, and are reversible.

### (opt-in) `posicionarEtapaPorRama` bypasses the documental gate, records pending

`moverEtapa` must keep enforcing docs for **manual** advances. We add a sibling that
the sync uses:

```ts
posicionarEtapaPorRama(tx, proceso, etapaDestino):
  - if orden(etapaDestino) <= orden(etapaActual): no-op (never auto-retrocede)
  - createEtapa({ etapaKey: etapaDestino, nota: "Posicionado por sincronización Rama", origen: "RAMA" })
  - update proceso.etapaActual = etapaDestino, recompute fechaLimite (same plazo logic)
  - DO NOT validate camposRequeridos / documentosRequeridos
```

The documental requirements are **not** marked met — they remain computed as
*faltantes* by the existing logic, so the ficha and the timeline show them as pending
("falta: auto que ordena seguir adelante"). This realizes the user's choice: position
the stage, never fake the paperwork.

Audit/visibility: tag the auto-created `EtapaHistorial` row with `origen = "RAMA"`
(new optional column or reuse `nota`) so the timeline distinguishes
*positioned-by-Rama* from *confirmed-by-lawyer*. **Open question O1** below.

## Decision 4 — Timeline component (`LineaTiempoActuaciones`)

Client-side, on the ficha:
- Vertical, newest-first, dated list of all actuaciones (we already store them).
- Each item: date, `actuacion`, `anotacion`; a badge when it mapped to a stage
  (which stage, which field it prefilled); a doc chip when `conDocumentos`.
- Header CTA **"Aplicar sugerencias"**: applies the still-unapplied `hitos` in one
  call (same derivation, but user-initiated for fields that were non-empty / ambiguous).
- Reuses motion tokens; no new animation lib. Renders via `ModalPortal` patterns
  already established. The bulk "Actualizar con la Rama" result keeps using the
  canonical `BotonActualizarRama` panel — the timeline is the *per-proceso* surface.

## Risks / mitigations

- **Wrong positioning from an ambiguous auto** → mitigated by `excluir`, by
  never auto-retroceding, and by docs staying visibly pending (nothing is "closed"
  silently). Env kill-switch `RAMA_AUTOPOSICION=off` falls back to autofill-only.
- **Free-text variance across despachos** → match on normalized substrings, allow
  `anotacion` matches, and keep mappings editable as data so a new phrasing is a data
  fix, not a deploy.
- **Terminal stages** (`terminado_excepciones`, `archivado_rechazo`) → only reach via
  explicit, well-excluded rules; a terminal auto-position sets `estado` like
  `moverEtapa` does for `terminal` stages — confirm in tasks.

## Open questions

- **O1:** add `EtapaHistorial.origen` enum (`MANUAL` | `RAMA`) vs. encode in `nota`?
  Leaning enum for clean timeline filtering. (Schema touch → `pnpm push`.)
- **O2:** when an autofilled date conflicts with a lawyer-entered one, we keep the
  lawyer's (only-if-empty). Do we *surface* the divergence in the timeline? Proposed:
  yes, as a non-blocking "Rama dice 2021-05-27" hint, no overwrite.

## Defect — red unit test on `feat/cuenta-clientes` (CI blocker)

`tests/hitos-actuaciones.test.ts` was committed (good — it contradicts the old
"no test harness → manual" assumption in tasks §5) but one case is **red**, so
`pnpm test` (vitest, run by CI) fails 1/506 and the pipeline is blocked.

- **Failing case:** `"Envió de Notificación" → { etapaKey: "mandamientoPago",
  campoFecha: "fechaNotificacion" }` (`hitos-actuaciones.test.ts:36-39`). Got
  `undefined`.
- **Root cause:** the case exercises the **legacy fallback** (`mapeo` undefined →
  `REGLAS_LEGACY`). `REGLAS_LEGACY` has a `mandamientoPago` rule keyed on
  `"MANDAMIENTO" → fechaMandamiento`, but **no rule for the notification** of the
  mandamiento. Nothing matches `"NOTIFICACION"`, so `detectarHitos` returns nothing.
  The accent normalization the test name advertises (`normaliza`, NFD strip) already
  works; the gap is a **missing mapping rule**, not a normalization bug.
- **Why fix the impl, not the test:** the ejecutivo's stage *"Mandamiento de pago y
  notificación al demandado"* really has a `fechaNotificacion` field (live seed), and
  the Rama really publishes a standalone *"Notificación…"* actuación. Mapping it to
  `mandamientoPago/fechaNotificacion` is correct domain behavior and adds autofill
  value. So: **add the legacy rule**, keep the test.

### Decision

Add to `REGLAS_LEGACY`, after the `MANDAMIENTO` rule:
`{ etapaKey: "mandamientoPago", actuacion: ["NOTIFICAC"], fechaCampo: "fechaNotificacion" }`
(`"NOTIFICAC"` covers *notificación/notificacion/notificado*; placed **after**
`MANDAMIENTO` so a text mentioning both prefers the libramiento date.)

### Known limitation (note, out of scope of the red fix)

`detectarHitos` keeps **one suggestion per `etapaKey`** (`porEtapa.has(...) →
continue`). `mandamientoPago` now has two date fields (`fechaMandamiento`,
`fechaNotificacion`); when both a *mandamiento* and a *notificación* actuación exist,
only the first-processed one's date is suggested, the other is dropped. Acceptable for
now (each is a separate prefill the lawyer can complete), but if both must autofill in
one sync the "one-per-stage" model has to become "one-per-(stage,field)". Tracked
here; not required to green the build.
