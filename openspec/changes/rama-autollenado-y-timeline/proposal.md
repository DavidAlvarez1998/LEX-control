# Proposal: Rama-driven ficha autofill + actuaciones timeline

## Why

A Rama Judicial sync already pulls the full, dated, ordered list of `actuaciones`
for a radicado, but we barely use it. Today (`hitos-actuaciones.ts`) we read **only
the `actuacion` title**, match it against a **hardcoded keyword array** scoped to the
ejecutivo, and emit **at most one "suggestion"** per stage that the lawyer applies by
hand. The sync also autofills exactly two fields (`juzgado`, `fechaRadicacion`).

Probing a real radicado — `66001400300320210022500`, an *Ejecutivo Singular por sumas
de dinero* (Juzgado 3 Civil Municipal de Pereira, 18 actuaciones, 2021–2024) — shows
how much signal we throw away, and that the current engine is **wrong on this very
case**:

| # | Actuación | Etapa it should drive | Engine today |
|---|---|---|---|
| 1 | Reparto y Radicación | `radicacionJuzgado` | only `fechaRadicacion` |
| 2 | Auto libra mandamiento ejecutivo | `mandamientoPago` | ✓ |
| 3 | Auto decreta **medidas cautelares** | `notifCautelares` | ❌ no keyword |
| 5 | Auto **seguir adelante con la ejecución** (sentencia ejecutiva) | `audiencia` | ❌ no keyword |
| 6 | Auto decreta **embargo** | cautelares/embargo | ❌ no keyword |
| 7,8,15 | Aprueba/**modifica liquidación del crédito** | `liquidacionCredito` | maps to stale `impulsos` |
| 11,14 | **Niega**/traslado solicitud terminación | (none) | ❌ false-fires `terminacion` |
| 16 | Auto termina proceso por Pago | `terminacion` | ✓ |

Four concrete defects surface:

1. **Stale stage keys.** `REGLAS` still targets `impulsos`; the tipo now has
   `liquidacionCredito` and `avaluoRemate` as separate stages, so suggestions land on
   a stage that no longer exists in the schema and are silently dropped.
2. **Missing high-value hitos.** No keyword for `CAUTELAR`, `EMBARGO`, or
   `SEGUIR ADELANTE` — three of the most important autos in this process go undetected.
3. **Negation false-positives.** `TERMINA` fires on *"NIEGA terminación"* and
   *"traslado solicitud terminación"*, which would mark a live process as terminated.
4. **Title-only + hardcoded + ejecutivo-only.** The `anotacion` free text (where the
   real signal often lives) is ignored, the mapping lives in a TS array, and no other
   tipo (verbal/sumario/laboral/DdP) can declare its own.

The actuaciones are effectively a dated event log of the case's state machine. We
should treat them that way.

## What changes

Three coordinated changes (scope confirmed with the user):

1. **Data-driven, negation-aware, anotacion-aware mapping (all tipos).**
   Replace the hardcoded `REGLAS` array with a `mapeoActuaciones` block declared
   **per tipo** in its schema (DB-resident, like the rest of the catálogo). Each rule
   matches on `actuacion` **and/or** `anotacion`, supports an `excluir` (negation)
   list, and points at an `etapaKey` plus optional `fechaCampo` / `valorCampo` to
   prefill. We seed the ejecutivo mapping first; verbal/sumario/laboral/DdP can add
   theirs without code changes.

2. **Autofill + stage positioning on every sync (no documental gating).**
   On sync, derive **all** matchable dates/decisions and `fijar()` them (keep the
   existing "only if empty" rule), and **move `etapaActual` to the furthest stage
   reached according to the Rama** — *without* requiring the judge's documents. The
   formal documental requirements stay visibly **pending** on the ficha; the lawyer
   uploads the auto when they have it. This needs a new positioning path that bypasses
   the `moverEtapa` documental gate while recording what is still missing.

3. **Visible actuaciones timeline in the ficha + batch apply.**
   A new component renders all actuaciones as dated milestones, highlights the ones
   mapped to a stage, shows which prefilled fields/stage they produced, and offers a
   single **"aplicar sugerencias"** action — keeping the human in the loop for review.

Out of scope: full auto-advance that marks documental requirements as met (explicitly
rejected); changing the cron cadence or the Rama HTTP client.

## Impact

- **API** (`lex-control-api`): rewrite `hitos-actuaciones.ts` to consume per-tipo
  `mapeoActuaciones` (negation + anotacion); extend `actuaciones.service.ts`
  (`sincronizarProceso`) to autofill all derived fields and call a new
  `posicionarEtapaPorRama`; new positioning helper alongside `moverEtapa`; seed the
  ejecutivo `mapeoActuaciones`.
- **Schema/seed**: add `mapeoActuaciones` to the ejecutivo tipo (DB is ahead of seed
  at v42 → patch live record surgically + update `seed-tipos.json`).
- **Client** (`lex-control-client`): new `LineaTiempoActuaciones` component on the
  ficha; wire the existing sync result to surface suggestions + batch apply.
- **Specs**: delta under `specs/rama-judicial/` (autofill + positioning + mapping
  contract) and `specs/proceso-vencimientos/` (stage positioned by Rama vs confirmed).

## Rollback plan

- The mapping is data: clearing a tipo's `mapeoActuaciones` reverts that tipo to "no
  autofill, no positioning" with zero code change.
- Stage positioning is behind a per-sync derivation; if it misbehaves, gate it with an
  env flag (`RAMA_AUTOPOSICION=off`) so sync falls back to autofill-only, then to the
  current suggestion-only behavior.
- Autofill keeps the existing "only fill empty fields" invariant, so it never
  overwrites lawyer-entered data; positioning only ever moves a stage and is itself a
  reversible `moverEtapa` (retroceso is always allowed).
