# Tasks

> **Estado real (2026-06-26, verificado contra el código).** Las checkboxes de abajo
> quedaron desactualizadas. Resumen: **§1 y §2 (backend) = HECHO** (motor data-driven,
> `derivarDesdeActuaciones`, `posicionarEtapaPorRama`, env `RAMA_AUTOPOSICION`, mapeo
> sembrado + parcheado en v44, fix del test §7). **PENDIENTE** = los 3 workstreams de
> cierre en §8 (refactor de granularidad, UI de hitos, spec de vencimientos + smoke).
> O1 resuelto (encode en `nota`); O2 se cierra en WS-B. Plan detallado en `design.md`
> → "Plan de cierre — sesión 2026-06-26".

## 0. Decisions to close before coding
- [ ] O1: `EtapaHistorial.origen` enum (`MANUAL`|`RAMA`) vs. encode in `nota`.
- [ ] O2: surface Rama-vs-lawyer date divergence in the timeline (non-blocking hint).
- [ ] Confirm the ejecutivo date/decision field keys to prefill
      (`fechaMandamiento`, `fechaCautelares`/`fechaEmbargo`, `fechaSentencia`,
      `fechaTerminacion`, `decisionCalificacion`, …) against the live v42 schema.

## 1. Mapping is data (`mapeoActuaciones`)
- [ ] Define `mapeoActuaciones` rule shape + matching semantics (actuacion OR
      anotacion, `excluir` negation, order-sensitive) in `specs/rama-judicial/spec.md`.
- [ ] Rewrite `hitos-actuaciones.ts`:
  - [ ] Read per-tipo `mapeoActuaciones`; legacy `REGLAS` only as fallback.
  - [ ] Normalize + match on `actuacion` **and** `anotacion`.
  - [ ] Apply `excluir` (fixes `NIEGA terminación` / `traslado` false-fire).
  - [ ] Keep the "field exists + empty in `datos`" guard.
- [ ] Seed the ejecutivo `mapeoActuaciones` (radicación, calificación admite/inadmite,
      mandamiento, cautelares, embargo, seguir-adelante=sentencia, liquidación,
      avalúo/remate, terminación by pago).
- [ ] Patch the **live v42** tipo record surgically (DB ahead of seed) **and** update
      `seed-tipos.json`. Do **not** re-run `pnpm seed:catalogo` (would clobber live edits).

## 2. Derivation + autofill + positioning (API)
- [ ] `derivarDesdeActuaciones(actuaciones, tipo, datos)` → `{ campos, etapaDestino, hitos }`.
- [ ] `etapaDestino` = furthest stage by `orden` with `disponibleSi` true, only forward.
- [ ] Extend `sincronizarProceso`: `fijar()` all `campos`; if `etapaDestino`, call
      `posicionarEtapaPorRama`.
- [ ] `posicionarEtapaPorRama(tx, proceso, etapaDestino)`:
  - [ ] Never auto-retrocede; create `EtapaHistorial` (origen RAMA); set `etapaActual`,
        recompute `fechaLimite`, set terminal `estado` when the stage is terminal.
  - [ ] **Skip** `camposRequeridos`/`documentosRequeridos` validation (docs stay pending).
- [ ] Env kill-switch `RAMA_AUTOPOSICION` (on by default; `off` = autofill-only).
- [ ] Ensure `moverEtapa` (manual) keeps full documental gating unchanged.

## 3. Timeline UI (client)
- [ ] `LineaTiempoActuaciones` on the ficha: dated, newest-first, all actuaciones.
- [ ] Badge mapped actuaciones (stage + prefilled field); doc chip when `conDocumentos`.
- [ ] Header CTA "Aplicar sugerencias" (batch apply remaining `hitos`).
- [ ] Show documental requirements still pending for a Rama-positioned stage.
- [ ] Keep bulk sync on the canonical `BotonActualizarRama` panel (unchanged).

## 4. Specs
- [ ] `specs/rama-judicial/spec.md` delta: mapping contract, autofill, positioning,
      negation, anotacion matching (Given/When/Then, RFC-2119).
- [ ] `specs/proceso-vencimientos/` delta: "stage positioned by Rama" vs "confirmed",
      docs-pending semantics.

## 5. Verify (no test harness → manual)
- [ ] `tsc` green in api + client.
- [ ] Re-run against `66001400300320210022500`: expect mandamiento, cautelares,
      embargo, seguir-adelante, liquidación, terminación-por-pago detected;
      `niega/traslado terminación` **not** firing terminación; `etapaActual` lands on
      `terminacion` with the terminación auto's date prefilled.
- [ ] Confirm a second radicado mid-process positions correctly and leaves docs pending.
- [ ] Smoke the timeline + batch apply in the client ficha.

## 7. Fix red test — missing legacy notification rule (CI blocker)
> Root cause + decision in `design.md` → "Defect — red unit test". 1-line fix.
- [ ] Add to `REGLAS_LEGACY` (`hitos-actuaciones.ts`), right after the `MANDAMIENTO`
      rule: `{ etapaKey: "mandamientoPago", actuacion: ["NOTIFICAC"], fechaCampo: "fechaNotificacion" }`.
- [ ] `pnpm test hitos-actuaciones` → 7/7 green; `pnpm test` → full suite green (506).
- [x] (Spec) the legacy fallback is transitional, so no spec delta needed; the
      data-driven `mapeoActuaciones` of the ejecutivo ALSO carries the
      notification→`fechaNotificacion` rule. Added with `excluir`
      `["ESTADO","SENTENCIA","EDICTO","EMPLAZA"]` (avoid notif-by-estado / of the
      sentencia / edicto / emplazamiento false-fires) in `seed-tipos.json` AND
      surgically in the live v44 record (seed:catalogo does not write this column).
- [ ] (Follow-up, separate) lift `detectarHitos` from one-suggestion-per-stage to
      one-per-(stage,field) so `fechaMandamiento` + `fechaNotificacion` can both
      autofill in a single sync (see design "Known limitation"). NOT required to
      green the build.

## 8. Plan de cierre — 3 workstreams (ver `design.md`)

### WS-A — `detectarHitos`: one-per-(stage, campo) [backend, acotado] ✅
- [x] `hitos-actuaciones.ts`: clave de dedup `etapaKey|fechaCampo??valorCampo??_`;
      N hitos por etapa, pero mismo destino sigue colapsando.
- [x] Test: "mandamiento + notificación → AMBAS fechas sugeridas".
- [x] Test: "dos actuaciones al mismo campo → una sola (la más reciente)".

### WS-B — Consciencia de la Rama en la ficha [cliente+api] — cierra O2 y §3 ✅
> Reescopeado: el equipo había quitado el panel "¿avanzar?" a propósito (el sync
> autollena solo). NO se reintroduce; solo se hace VISIBLE lo ya derivado.
- [x] Enriquecer `ActuacionesJuzgado` sin Card nueva ni CTA de "aplicar".
- [x] `getSugerenciasActuaciones` (antes muerto) ahora retorna `{ hitos, divergencias }`.
- [x] Transparencia: "✓ La Rama completó: <campos>" (de `camposRamaCsv`/P8).
- [x] Etapa: "El juzgado ya va en <etapa>" cuando va por delante (solo consciencia).
- [x] **O2:** hint ámbar no bloqueante con las fechas Rama-vs-abogado (no pisa). Nueva
      función pura `divergenciasRama` + 2 tests.
- [x] Doc-chip: descartado (lo cubre `DocumentosRama`); no se infló el DTO.
- [x] CTA "Aplicar sugerencias": **descartado** (contradecía la decisión del equipo).

### WS-C — Spec `proceso-vencimientos` + verificación
- [x] `specs/proceso-vencimientos/spec.md` (delta): "posicionada por Rama" vs
      "confirmada", docs pendientes, consciencia O2 (Given/When/Then, RFC-2119).
- [x] `tsc` api+client verde; `pnpm test` verde (510/510, +4 casos nuevos).
- [ ] **Smoke en radicado real** (manual, lo hace el usuario): autollenado de fechas +
      transparencia "La Rama completó" + aviso de etapa + hint de divergencia. Confirmar
      de paso el texto real de la notificación (ver `design.md` → hallazgo de ordering).

## 6. Memory / docs
- [ ] On completion, archive into `openspec/specs/` and update MEMORY.md pointer.
