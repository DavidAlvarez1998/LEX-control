# Tasks — procesos-ux-ddp-tutela

Presentation-only UX change. Driver cases: Derecho de Petición & Tutela. No schema, no stage/gate/
vencimiento rule changes. API limited to two read-only list query params.

## A. Deadline-first surfacing
- [ ] List: add a `Vence` column rendering `fechaLimite` with semáforo color (rojo vencido / rojo
      "vence hoy" / ámbar ≤3 hábiles / neutro al día); "vence hoy" derived in UI from `fechaLimite === today`
- [ ] List: default-sort open procesos by urgency (soonest/overdue first; no-fechaLimite and
      closed/archived after)
- [ ] Home (`(dashboard)/page.tsx`): "Vencimientos de procesos" card from `GET /procesos/vencimientos`
      (counts `vencido`/`por_vencer` + nearest few, links to fichas); collapses when none
- [ ] Ficha: active stage shows live countdown from `fechaLimite` ("Vence en N días hábiles · fecha" /
      "Vencido hace N" in red), reusing the derived value (no new math)

## B. Find anything fast
- [ ] API `GET /procesos`: accept optional `q` (codigoInterno/titulo/cliente.nombre/radicado,
      case-insensitive) and `responsableId`, composing with `area`/`estado`, hard `WHERE { empresaId }`
- [ ] Client `lib/procesos-api.ts`: pass `q`/`responsableId` through `listProcesos`
- [ ] List UI: search box (debounced) + responsable selector next to the existing área/estado filters
- [ ] Tests: search matches título/código/cliente/radicado; responsable filter; both stay despacho-scoped

## C. The caso is the unit
- [ ] List: per-row "caso" marker when the proceso has `casoRelacionadoId` or derivados, linking to the
      base proceso (data already available or via the list projection)
- [ ] `CasoChain`: show each node's current stage name (in addition to estado/`fechaLimite`); fix
      narrow-viewport horizontal scroll without clipping; keep the active node highlighted

## D. Continuity decision visible
- [ ] Ficha: promote the `crearDerivado` action to a prominent contextual CTA (out of the stage-list
      footnote), reusing the continuation-vs-escalation copy already added
- [ ] Preserve idempotency: when the derivado exists, show "abrir expediente →" instead of create

## E. Stage flow legibility
- [ ] Stepper: show each stage's plazo (`reglas.plazoDias` + `plazoTipoDias`); emphasize very short
      terms (tutela impugnación = 3 días)
- [ ] DdP branches: present applicable branch(es) as takeable; keep unavailable ones dimmed/
      non-clickable (current behavior) + one line of guidance that the path follows `contestaron`

## Verify
- [ ] `pnpm --dir lex-control-api build` (tsc) clean
- [ ] `pnpm --dir lex-control-client build` (next) clean
- [ ] `pnpm --dir lex-control-api test` green (new tests for `q`/`responsableId` scoping)
- [ ] Live smoke: DdP with near deadline shows in home card + list red/amber; reiteración shows caso
      marker; CTA reiterar/escalar contextual; search by entity finds the DdP
