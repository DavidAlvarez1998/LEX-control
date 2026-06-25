# Proposal: Detailed, actionable result for "Actualizar con Rama"

## Why

In the procesos list, the **"Actualizar con Rama"** button (P16, bulk on-demand sync)
shows a flat toast like:

> ✓ 2 consultado(s) · 0 con novedades · 2 con error.

This is opaque and slightly contradictory (a ✓ next to "all errored"). Two real
problems:

1. **The result is a count with no reason.** The backend
   (`sincronizarMisProcesos`, `actuaciones.service.ts`) only returns
   `{ procesos, conNovedad, nuevasTotal, errores }`. Until this change the `catch`
   was even silent (`catch { errores++ }`) — it threw the cause away, so neither the
   user nor the logs knew *which* process failed or *why*. (A first step — logging the
   reason server-side — has already been added in this branch.)

2. **"con error" conflates very different outcomes** and scares the user about the
   wrong thing:
   - A radicado that **doesn't exist / isn't published** is NOT an error — it returns
     normally with `ramaEstado = NO_PUBLICADO`. It does not increment `errores`.
   - `errores` only counts **thrown exceptions**, which are one of two unrelated
     things:
     - **`RADICADO_INVALIDO`** — the stored radicado isn't 23 valid digits
       (`normalizarRadicado` → `HttpError 400`). A **data** problem the user fixes.
     - **`FUENTE_NO_DISPONIBLE`** — timeout / no connection / 403·429 (rate-limit) /
       5xx from the Rama after retries (`HttpError 502`). A **transient** problem;
       retry later.

   Collapsing both into "con error" gives the user no idea whether to fix their data
   or just retry.

## What changes

Make the sync result **per-process, categorized, and actionable** — both in the API
payload and in the UI.

1. **API — return outcomes, not just counts.** `sincronizarMisProcesos` returns a
   `resultados[]` array alongside the existing aggregate counts (kept for
   backward-compat). Each entry: `{ procesoId, titulo, radicado, resultado }` where
   `resultado` ∈
   `ACTUALIZADO | SIN_NOVEDAD | NO_PUBLICADO | RESERVADO | RADICADO_INVALIDO | FUENTE_NO_DISPONIBLE`.
   - Map `sincronizarProceso`'s return + the caught `HttpError` to these buckets:
     - `r.nuevas > 0` → `ACTUALIZADO`; else `r.encontrado` → `SIN_NOVEDAD`.
     - `r.reservado` → `RESERVADO`; `!encontrado && !reservado` → `NO_PUBLICADO`.
     - caught `HttpError 400` (invalid radicado) → `RADICADO_INVALIDO`.
     - caught `HttpError 502` / anything else → `FUENTE_NO_DISPONIBLE`.

2. **UI — summary by real buckets + drill-down.** Replace the single flat toast in
   `procesos/page.tsx` (`actualizarMisProcesos`) with:
   - A summary line by meaningful bucket with severity color, e.g.
     *Actualizados N · Al día N · No publicados en la Rama N · ⚠️ No se pudieron consultar N*.
     Never label `NO_PUBLICADO` as an error.
   - An expandable panel listing the processes that need attention, split by cause:
     - `RADICADO_INVALIDO` → "Revisa el radicado" + link to the ficha.
     - `FUENTE_NO_DISPONIBLE` → "La Rama no respondió" + a **Reintentar** action that
       re-syncs only those.

3. **(Optional, phase 2) Persist per-row state.** Extend `ramaEstado` with `ERROR` (+
   reason) and show a small badge per row in the list, so the diagnosis survives
   closing the toast. Decide during design whether to include now or defer.

## Scope / non-goals

- Reuses the existing Rama client/transport unchanged — this is about **surfacing**
  outcomes, not changing how we query the Rama.
- No change to the cron bulk sync's behavior (`sincronizarTodas`), beyond optionally
  sharing the same outcome categorization helper.
- Keep the aggregate counts in the response for any current consumer.

## Rollback plan

API change is additive (new `resultados[]` field; counts unchanged) — safe to revert
the UI alone. Full rollback = `git revert` the API + client commits; the already-merged
catch-logging line is harmless and can stay. No DB migration unless phase 2 (the
`ramaEstado = ERROR` enum value) is included — that would need a `pnpm push`.
