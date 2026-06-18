# Tramite Catalog Specification — delta (laboral-doble-instancia)

> Refina el esquema del `TipoProceso` "Proceso Laboral" definido por `laboral-flujo-doc`.

## ADDED Requirements

### Requirement: Laboral schema fields for subsanación-admission and second instance
The "Proceso Laboral" `esquemaFormulario` MUST include these `soloFicha` fields, shown by
`mostrarSi` as indicated:

| key | tipo | mostrarSi |
|---|---|---|
| `fechaAdmisionTrasSubsanacion` | fecha | `decisionTrasSubsanacion = ADMITIR` |
| `concedeApelacion` | select `SI`/`NO` | `hayRecurso = SI` |
| `fechaRemision2inst` | fecha | `concedeApelacion = SI` |
| `radicado2inst` | texto | `concedeApelacion = SI` |
| `fechaSustentacion` | fecha | `concedeApelacion = SI` |
| `fechaAudiencia2inst` | fecha | `concedeApelacion = SI` |
| `fechaSentencia2inst` | fecha | `concedeApelacion = SI` |
| `decisionSegundaInstancia` | select `CONFIRMA`/`REVOCA`/`MODIFICA` | `concedeApelacion = SI` |

New stage documents MUST be defined: `auto-admision-tras-subsanacion.pdf`, `apelacion.pdf`,
`escrito-sustentacion.pdf`, `auto-2inst.pdf`, `acta-2inst.pdf` (optional), `sentencia-2inst.pdf`.

#### Scenario: Second-instance fields are stage-only and gated by the granted appeal
- GIVEN the "Proceso Laboral" catalog type
- THEN `fechaRemision2inst`, `radicado2inst`, `fechaSustentacion`, `fechaAudiencia2inst`,
  `fechaSentencia2inst`, `decisionSegundaInstancia` are `soloFicha` with `mostrarSi: {campo:
  concedeApelacion, igualA: "SI"}`
- AND they never appear in the creation form

### Requirement: `fase` grouping label on laboral stages (optional presentation layer)
Each laboral `EtapaDef` MAY carry a `fase` ∈ {1..6} mapping to: 1 Demanda y admisión · 2
Traslado y contestación · 3 Audiencias · 4 Sentencia y recurso · 5 Segunda instancia · 6
Terminación/archivo. The label MUST NOT affect gating, ordering or validation — it only groups
stages for display (stepper agrupado). The UI MAY render only the fases applicable to the
proceso's `rol`/`tipoInstancia`.

#### Scenario: Phase label is presentation-only
- GIVEN a laboral etapa carrying `fase = 3`
- WHEN the workflow engine computes availability and deadlines
- THEN `fase` is ignored by the engine (no effect on `disponibleSi`, `orden` or `fechaLimite`)

## MODIFIED Requirements

### Requirement: Laboral demand intake is attached as PDF (no typed pretensiones/hechos)
The "Proceso Laboral" creation intake MUST NOT ask `pretensiones`/`hechos`; the demand is
attached as documents. The creation form MUST ask, in document order: `rol`, `tipoInstancia`,
`requierePoder`, the demand documents (`demanda.pdf` required; `pruebas.pdf`, `anexos.pdf`,
`radicacion.pdf` optional), and — only when `rol = Demandante` — `fechaRadicacion`, plus the
real columns `radicado` and `despachoJuzgado`. The full case cycle (calificación, contestación,
audiencias, sentencia, recurso, second instance) happens stage-by-stage on the ficha, never at
creation.

The recurso-de-rechazo fields (`recursoRechazo`, `fechaRecursoRechazo`,
`decisionRecursoRechazo`, `observacionesRecursoRechazo`) MUST be shown for **both** rejection
origins via `mostrarSi: {alguna: [{campo: decisionAuto, igualA: "RECHAZO"}, {campo:
decisionTrasSubsanacion, igualA: "RECHAZAR"}]}`.

#### Scenario: Creation form stays short and document-first
- GIVEN a new "Proceso Laboral"
- THEN the form asks rol, instancia, ¿poder?, the demand documents, and (demandante) fecha de
  radicación + radicado + juzgado — and nothing of the later stages

#### Scenario: Recurso fields appear for a reject after subsanación
- GIVEN a laboral proceso with `decisionTrasSubsanacion = RECHAZAR`
- THEN `recursoRechazo` and its dependent fields are shown (same fields as a direct `RECHAZO`)
