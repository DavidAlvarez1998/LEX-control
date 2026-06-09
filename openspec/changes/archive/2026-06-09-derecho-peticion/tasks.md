# Tasks: Derecho de Petición + deadline & conditional engine

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 600–900 (api-heavy; client touch-ups) |
| 400-line budget risk | Med |
| Chained PRs recommended | Optional |
| Suggested split | PR 1 (engine: días hábiles + conditional + plazo) → PR 2 (derive + seed) → PR 3 (client UX) |
| Delivery strategy | backend-first (engine is the value; UX is incremental) |

Decision needed before apply: Yes (confirm festivos source + manual override — see proposal Open Decisions).

## Phase 1: Business-day engine (`proceso-vencimientos`)
- [x] 1.1 `src/modules/procesos/diasHabiles.ts` (pure): `festivosColombia(year)` (fixed + Emiliani-Monday + Easter-relative via Meeus), `esDiaHabil`, `sumarDiasHabiles`, `sumarDiasCalendario`. No `Date.now`.
- [x] 1.2 Unit tests: explicit expected festivo set for 2024–2027; weekend/festivo exclusion; add-days across weekend+festivo.
- [x] 1.3 Schema: additive `Proceso.fechaLimite DateTime?` + `@@index([empresaId, fechaLimite])`; `pnpm generate` + `pnpm push`.

## Phase 2: Conditional schema + validation
- [x] 2.1 `esquema.ts`: add `Condicion`, `mostrarSi`/`requeridoSi` to `CampoEsquema`; `evaluarCondicion`; `esEfectivamenteRequerido(campo, datos)`; update `validarDatos` to skip hidden + honor `requeridoSi`.
- [x] 2.2 `catalog.schemas.ts`: Zod for field `mostrarSi`/`requeridoSi`; etapa `requeridosSi`/`disponibleSi`/`accion` and the deadline keys that EXTEND existing `plazoDias` (`plazoDesdeCampo`/`plazoTipoDias`/`plazoDiasPorValorDe`); extend the `superRefine` to validate every referenced `campo`/`tipoDestinoNombre` exists (422). Keep `plazoDias`/`resultado`/`ayuda` intact.
- [x] 2.3 Regression test: a pre-existing tipo (no conditional/plazo keys) validates and transitions exactly as before.

## Phase 3: Deadline derivation + branching + derive action
- [x] 3.1 `procesos.router.ts`: on stage move, if target etapa has `reglas.plazo`, derive and persist `fechaLimite` (skip if source empty; do not clobber a manual override without explicit recompute).
- [x] 3.2 Enforce `disponibleSi` on stage transitions (422 with reason); enforce conditional `requeridosSi` in the rule gate.
- [x] 3.3 `crearDerivado` action: tx creates derived `Proceso` (fresh `codigoInterno`, `casoRelacionadoId`, initial etapa); unique per `(casoRelacionadoId, tipoProcesoId)` → 409 on repeat.
- [x] 3.4 `GET /procesos/vencimientos` (despacho-scoped) → buckets vencido/por_vencer/al_dia.
- [x] 3.5 Tests: DdP documental → +10 hábiles; poder conditional gate; contestaron branch availability; idempotent escalation; tenant isolation on vencimientos.

## Phase 4: Seed DdP + Acción de Tutela
- [x] 4.1 Seed two global `TipoProceso` in `prisma/seed-tipos.json` — jurisdiccion CONSTITUCIONAL, `areaSlugs: ["constitucional"]` (first constitutional tipos; área already seeded, orden 7) — with esquemaFormulario, etapas, plazo 15/10/30 (plazoDesdeCampo+plazoDiasPorValorDe), conditional rules, escala_tutela derive — per design.md §4. Idempotent upsert by `(empresaKey="", nombre)`.
- [x] 4.2 Optional starter `PlantillaDocumento` for the petición/reiteración drafts (reuse Fase 4 engine).
- [x] 4.3 Seed test: both types present, DdP `radicada` carries the term mapa, derive target resolves.

## Phase 5: Client UX
- [x] 5.1 `<FormularioDinamico>`: use shared `evaluarCondicion` to hide/show fields and to mark the dynamic red asterisk; never submit hidden-required as missing.
- [x] 5.2 Expediente header: show `fechaLimite` with semáforo (al día / por vencer / vencido); stage stepper honors `disponibleSi` ("why blocked"/"only X available").
- [x] 5.3 `escala_tutela`: a "Crear acción de tutela" action that calls `crearDerivado` and links to the new expediente; show the relation both ways.
- [x] 5.4 Optional: a "Vencimientos" widget/list consuming `GET /procesos/vencimientos`. `pnpm --dir lex-control-client build` clean.

## Verify
- [ ] `pnpm --dir lex-control-api build` clean; full test suite green (new días-hábiles + conditional + derive + vencimientos tests).
- [ ] `pnpm --dir lex-control-client build` clean.
- [ ] Live smoke: seed → file a DdP (Documental) → fechaLimite correct → contestaron=NO → escalate → linked tutela appears.
