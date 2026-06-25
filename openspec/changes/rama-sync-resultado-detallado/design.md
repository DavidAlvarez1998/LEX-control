# Design: Detailed sync result

## D1. Where the categorization lives

A single helper maps a per-process sync outcome to a `ResultadoSyncProceso` enum, used
by both the on-demand path (`sincronizarMisProcesos`) and — optionally — the cron
(`sincronizarTodas`). Keeping it in one place avoids the two paths drifting on what
counts as an "error".

```
ACTUALIZADO         // r.encontrado && r.nuevas > 0
SIN_NOVEDAD         // r.encontrado && r.nuevas === 0
NO_PUBLICADO        // !r.encontrado && !r.reservado   (radicado no existe/sin publicar)
RESERVADO           // r.reservado
RADICADO_INVALIDO   // caught HttpError 400 (normalizarRadicado falló)
FUENTE_NO_DISPONIBLE// caught HttpError 502 / timeout / 403·429 / 5xx / otro
```

**Rationale.** The current code already distinguishes `NO_PUBLICADO`/`RESERVADO` inside
`sincronizarProceso` (it sets `ramaEstado` accordingly and returns
`{ encontrado, reservado, nuevas, total }`) — it just gets flattened away by the caller.
We surface what the domain already knows.

## D2. Distinguishing error causes from the caught exception

The two error buckets are told apart by `HttpError.status`:
- `400` → `RADICADO_INVALIDO` (thrown by `sincronizarProceso` at the radicado guard).
- anything else (`502`, or non-HttpError) → `FUENTE_NO_DISPONIBLE`.

We must read `err.status` defensively (it may be a plain `Error`). Default to
`FUENTE_NO_DISPONIBLE` when unknown — it's the safe "retry later" bucket and won't
wrongly tell the user their data is broken.

## D3. API response shape (additive, backward-compatible)

```jsonc
{
  "procesos": 2, "conNovedad": 0, "nuevasTotal": 0, "errores": 2,  // kept as-is
  "resultados": [
    { "procesoId": "...", "titulo": "...", "radicado": "...", "resultado": "FUENTE_NO_DISPONIBLE" }
  ]
}
```

Existing consumers that only read the counts keep working; the UI switches to
`resultados[]`.

## D4. UI: summary buckets + drill-down (no new library)

Built with existing primitives (`Card`, `Button`, the toast/aviso pattern already in
`procesos/page.tsx`). The summary maps the 6 outcomes to **4 user-facing buckets** so
`NO_PUBLICADO` is never shown as an error:

| Bucket (UI) | Outcomes folded in | Severity |
|-------------|--------------------|----------|
| Actualizados | `ACTUALIZADO` | success |
| Al día | `SIN_NOVEDAD` | neutral |
| No publicados en la Rama | `NO_PUBLICADO`, `RESERVADO` | info |
| No se pudieron consultar | `RADICADO_INVALIDO`, `FUENTE_NO_DISPONIBLE` | warning |

The expandable detail lists only the warning bucket, split by cause, each row linking
to the ficha; `FUENTE_NO_DISPONIBLE` rows get a **Reintentar** that re-calls the sync
scoped to those processes.

## D6. Canonical component — ARCHITECTURE RULE

The bulk "Actualizar con la Rama" result is rendered by **one** shared component,
`lex-control-client/src/components/boton-actualizar-rama.tsx` (`<BotonActualizarRama
onSynced={...} />`), which bundles the button + sync state + the `ResumenSync` panel.

**Rule (applies to all current and future process views / jurisdictions):**
- Every list view that offers bulk Rama sync (Jurisdicción nivel-3, Todos, Míos, and any
  future jurisdiction/view) MUST reuse `<BotonActualizarRama />`. Do **not** re-inline the
  button + `sincronizarMisProcesos()` + a flat toast.
- The result is **never** shown as the flat string `✓ N consultado(s) · … · N con error`.
  It is always the bucketed, actionable `ResumenSync` (data-vs-source split + drill-down +
  Reintentar).

**Why:** the page had drifted into two duplicated inline copies of the old flat toast
(VistaPlana Todos/Míos and CatalogoProcesos nivel-3). A single component removes the
duplication and guarantees the same actionable UX everywhere. Layout: the panel renders
inside the toolbar flex row with `order-last basis-full` so it drops to its own full-width
row below the filters regardless of what other controls the view has.

## D5. Phase 2 (deferred decision): persist `ramaEstado = ERROR`

Persisting an `ERROR` state + reason on the row would let the list show a badge after
the toast is dismissed. This needs a schema change (`ramaEstado` enum/string + a reason
column) and a `pnpm push` (no `prisma migrate` — it resets the DB). Defer unless the
toast+drill-down proves insufficient; the additive API change does not depend on it.
