# Tasks — procesos-ux-ddp-tutela

Presentation-only UX change. Driver cases: Derecho de Petición & Tutela. No schema, no stage/gate/
vencimiento rule changes. API limited to two read-only list query params.

## A. Deadline-first surfacing
- [x] List: add a `Vence` column rendering `fechaLimite` with semáforo color (rojo vencido / rojo
      "vence hoy" / ámbar ≤3 hábiles / neutro al día); "vence hoy" derived in UI from `fechaLimite === today`
- [x] List: default-sort open procesos by urgency (soonest/overdue first; no-fechaLimite and
      closed/archived after)
- [x] Home (`(dashboard)/page.tsx`): "Vencimientos de procesos" card from `GET /procesos/vencimientos`
      (counts `vencido`/`por_vencer` + nearest few, links to fichas); collapses when none
- [x] Ficha: active stage shows live countdown from `fechaLimite` ("Vence en N días · fecha" /
      "Vence hoy" / "Vencido hace N" in red), reusing the derived value (no new math)

## B. Find anything fast
- [x] API `GET /procesos`: accept optional `q` (codigoInterno/titulo/cliente.nombre/radicado,
      case-insensitive) and `responsableId` (already existed), composing with `area`/`estado`, hard `WHERE { empresaId }`
- [x] Client `lib/procesos-api.ts`: pass `q`/`responsableId` through `listProcesos`
- [x] List UI: search box (debounced) + responsable selector (derived from procesos seen)
- [ ] Tests: search matches título/código/cliente/radicado; responsable filter; both stay despacho-scoped

## C. The caso is the unit
- [x] List: per-row "caso" marker when the proceso has `casoRelacionadoId` (link to base) or derivados (badge)
- [x] `CasoChain`: show each node's current stage name (`etapaNombre`, resolved server-side) in addition
      to estado/`fechaLimite`; horizontal scroll already present; active node highlighted

## D. Continuity decision visible
- [x] Ficha: the `crearDerivado` action is an amber CTA box with continuation-vs-escalation copy
      ("Crear la reiteración" vs "Crear {tipo}"); the layout reorder put Etapas high, so the CTA is prominent
- [x] Idempotency preserved: when the derivado exists, shows "abrir expediente →"

## E. Stage flow legibility
- [x] Stepper: shows each stage's plazo; very short terms (≤3 días, e.g. tutela impugnación) are
      emphasized in red with a ⚠ marker
- [x] DdP branches: applicable branch takeable; unavailable ones dimmed/non-clickable (existing behavior)

## Verify
- [x] `pnpm --dir lex-control-api build` (tsc) clean
- [x] `pnpm --dir lex-control-client build` (next) clean
- [ ] `pnpm --dir lex-control-api test` green (new tests for `q`/`responsableId` scoping)
- [ ] Live smoke: DdP with near deadline shows in home card + list red/amber; reiteración shows caso
      marker; CTA reiterar/escalar contextual; search by entity finds the DdP
