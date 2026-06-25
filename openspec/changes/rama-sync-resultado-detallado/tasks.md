# Tasks: Detailed sync result

## 0. Diagnose the current 2 errors (already unblocked)

- [x] 0.1 Add reason logging to the silent `catch` in `sincronizarMisProcesos`
      (`actuaciones.service.ts`) — logs `procesoId`, `radicado`, `err`. (Done in branch.)
- [x] 0.2 Triggered "Actualizar con Rama" and read the container logs
      (`lex-control-dev-api-1`): **both failures are `RADICADO_INVALIDO`** — radicados
      `1332165` (7 digits) and `66001400300220260070` (20 digits), neither 23. NOT a
      Rama outage. Confirms the data-vs-source split was the right call.

## 1. API — categorized per-process results

- [x] 1.1 `ResultadoSyncProceso` type + `categorizarOk` / `categorizarError` helpers
      (D1/D2): map `sincronizarProceso` return and `HttpError.status` to the 6 outcomes.
- [x] 1.2 `sincronizarMisProcesos` builds `resultados[]` (`{ procesoId, titulo,
      radicado, resultado }`) alongside the existing counts (D3).
- [x] 1.3 Optional `procesoIds[]` filter (zod `sincronizarMisSchema`, max 40) for the
      targeted "Reintentar" — tenant-scoped, ignores the 6h freshness window.
- [x] 1.4 Router validates the body; client SDK `sincronizarMisProcesos(procesoIds?)`
      + `SyncMisResp.resultados` / `ItemSyncMis` types.
- [x] 1.5 Tests: `tests/sync-categorizar.test.ts` covers all 6 outcomes (7 tests).

## 2. UI — summary buckets + drill-down

- [x] 2.1 Replaced the flat toast with the 4-bucket summary chips (D4); `NO_PUBLICADO`
      shown as info ("No publicados en la Rama"), never as error.
- [x] 2.2 `ResumenSync` panel lists the failed processes split by cause, each linking
      to its ficha; transport failure shown as a separate amber card.
- [x] 2.3 `Reintentar` action on `FUENTE_NO_DISPONIBLE` rows → re-syncs only those.
- [x] 2.4 Edge states: 0 procesos con radicado ("No hay procesos con radicado…"),
      chips filter out empty buckets, closable panel.
- [x] 2.5 ARCH RULE (D6): extracted the button + state + panel into the canonical
      `components/boton-actualizar-rama.tsx` (`<BotonActualizarRama onSynced/>`) and
      reused it in ALL three `/procesos` views (Jurisdicción nivel-3, Todos, Míos),
      removing the two duplicated inline flat-toast copies. Future views/jurisdictions
      must reuse it. Panel drops to its own full-width row via `order-last basis-full`.

## 3. (Phase 2 — deferred) persist per-row state

- [ ] 3.1 NOT done: extend `ramaEstado` with `ERROR` + reason + per-row badge. Deferred
      — the toast+drill-down covers the need; revisit if it proves insufficient.

## 4. Wrap-up

- [x] 4.1 `lex-control-api` build + 505 tests green; `lex-control-client` build green.
- [x] 4.2 Spanish wording reviewed (actionable, non-alarming).
- [ ] 4.3 Commit (api submodule + client submodule + umbrella pointer/openspec).
- [ ] 4.4 Archive this change in `openspec/`.
