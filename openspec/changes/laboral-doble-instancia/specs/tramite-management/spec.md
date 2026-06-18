# Tramite Management Specification — delta (laboral-doble-instancia)

> Se apoya en el change `laboral-flujo-doc` (estado real del flujo laboral) y lo refina. Los
> nombres de requisito MODIFIED corresponden a los que introduce ese change.

## MODIFIED Requirements

### Requirement: Laboral workflow branches by rol × instancia per the source document
The "Proceso Laboral" workflow MUST follow the four flows of the source document
(`PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`): Demandante/Única, Demandante/Doble,
Demandado/Única, Demandado/Doble. Branching MUST be driven by `disponibleSi` (AND/OR over
`rol`, `tipoInstancia` and outcome fields) and `mostrarSi` on fields, NOT by separate process
types.

The stage order MUST be: Presentación → (Demandante) Calificación del auto → [Subsanación →
Recurso de rechazo | Recurso de rechazo] → ¿Retiro art. 67? → Traslado y notificación →
(Doble) Contestación → **Preparación de audiencia → Citación** (Doble) / **Citación →
Preparación de audiencia** (Única) → [Audiencia única | Audiencia art. 77 → Audiencia art. 80]
→ Sentencia → Recurso (reposición en única / apelación en doble) → (Doble, si se concede la
apelación) Segunda instancia → Terminación/Archivo.

The Preparación↔Citación order MUST depend on `tipoInstancia`: in **doble** Preparación comes
before Citación; in **única** Citación comes before Preparación. This MUST be modeled with
instance-gated stage variants sharing the same campos.

#### Scenario: Double-instance orders preparación before citación
- GIVEN a laboral proceso with `tipoInstancia = "Doble instancia"`
- WHEN it advances past `contestacion`
- THEN `preparacionAudiencia` is offered before `citacionAudiencia`

#### Scenario: Single-instance orders citación before preparación
- GIVEN a laboral proceso with `tipoInstancia = "Única instancia"`
- WHEN it advances past `traslado`
- THEN `citacionAudiencia` is offered before `preparacionAudiencia`

### Requirement: Calificación del auto — only the demandante decides; the demandado records it
The calificación-with-decision (decisión del auto ∈ {`ADMISIÓN`, `INADMISIÓN`, `RECHAZO`} con
sus ramas de subsanación y recurso de rechazo) MUST be available **only when `rol =
Demandante`** — it is *our* demand being calificada. When `rol = Demandado` and `tipoInstancia
= Doble instancia`, the `admision` stage MUST appear as a **record only** (`fechaAdmision` +
`auto-calificacion.pdf`) WITHOUT requiring `decisionAuto` nor opening subsanación/recurso de
rechazo. When `rol = Demandado` and `tipoInstancia = Única instancia`, there MUST be no
admisión stage at all (the flow goes presentación → retiro/traslado).

#### Scenario: Demandado/Doble records the admission without a decision
- GIVEN a laboral proceso with `rol = Demandado`, `tipoInstancia = Doble instancia` at `admision`
- THEN `fechaAdmision` and `auto-calificacion.pdf` are recorded
- AND `decisionAuto` is NOT required and `subsanacion`/`recurso_rechazo` are NOT offered

#### Scenario: Demandado/Única has no admisión stage
- GIVEN a laboral proceso with `rol = Demandado`, `tipoInstancia = Única instancia`
- WHEN advancing from `presentacion`
- THEN `admision` is skipped and the next stage is `retiro`/`traslado`

### Requirement: Rechazo (directo o tras subsanación) routes through the recurso
A rejection MUST route through the `recurso_rechazo` stage in **both** origins: directly when
`decisionAuto = RECHAZO`, and after an inadmisión when `decisionTrasSubsanacion = RECHAZAR`.
The same recurso fields (`recursoRechazo`, `fechaRecursoRechazo`, `decisionRecursoRechazo`,
`observacionesRecursoRechazo`) are reused (a proceso is direct-reject XOR reject-after-subsanación).
`recurso_rechazo` MUST have a higher `orden` than `subsanacion` so it is reachable from both
`admision` and `subsanacion`. When `recursoRechazo = NO` or `decisionRecursoRechazo =
DESFAVORABLE`, the terminal `archivado_rechazo` MUST become available; when
`decisionRecursoRechazo = FAVORABLE`, the workflow MUST continue (retiro/traslado).

#### Scenario: Reject after subsanación opens the recurso (not a direct archive)
- GIVEN `decisionAuto = INADMISIÓN` and `decisionTrasSubsanacion = RECHAZAR`
- WHEN the next stages are computed
- THEN `recurso_rechazo` is offered (NOT a direct jump to `archivado_rechazo`)

#### Scenario: Favorable recurso continues the process
- GIVEN a rejection with `decisionRecursoRechazo = FAVORABLE`
- WHEN the next stages are computed
- THEN the workflow continues to `retiro`/`traslado` and `archivado_rechazo` is NOT offered

## ADDED Requirements

### Requirement: Auto admisorio recorded after a successful subsanación
When `decisionTrasSubsanacion = ADMITIR`, the `subsanacion` stage MUST require
`fechaAdmisionTrasSubsanacion` and the document `auto-admision-tras-subsanacion.pdf`, then
continue the workflow to `retiro`/`traslado`.

#### Scenario: Admisión after subsanación captures its own auto
- GIVEN `decisionAuto = INADMISIÓN` and `decisionTrasSubsanacion = ADMITIR`
- WHEN completing the `subsanacion` stage
- THEN `fechaAdmisionTrasSubsanacion` and `auto-admision-tras-subsanacion.pdf` are required
- AND the workflow continues to `retiro`/`traslado`

### Requirement: Appeal is recorded in two steps (interpone → concede)
For double-instance, after the sentencia the workflow MUST capture both `hayRecurso`
(¿se interpone la apelación?) and, when `hayRecurso = SI`, `concedeApelacion` (¿el juez la
concede?). When `hayRecurso = NO` or `concedeApelacion = NO`, the workflow MUST end at
`terminada` (1ª instancia en firme). Only when `concedeApelacion = SI` MUST the second-instance
stages become available.

#### Scenario: Appeal not granted ends the process
- GIVEN a double-instance sentencia with `hayRecurso = SI` and `concedeApelacion = NO`
- WHEN the next stages are computed
- THEN the workflow ends at `terminada` and no second-instance stage is offered

### Requirement: Second instance (double-instance, when the appeal is granted)
When `concedeApelacion = SI`, the workflow MUST offer, in order, the second-instance stages
before `terminada`: `remision2inst` (remisión/reparto al Tribunal: `fechaRemision2inst`,
`radicado2inst`), `sustentacion2inst` (`fechaSustentacion` + `escrito-sustentacion.pdf` +
`auto-2inst.pdf`), `audiencia2inst` (`fechaAudiencia2inst` + optional `acta-2inst.pdf`), and
`sentencia2inst` (`fechaSentencia2inst` + `sentencia-2inst.pdf` + `decisionSegundaInstancia` ∈
{`CONFIRMA`, `REVOCA`, `MODIFICA`}). These stages MUST be gated `disponibleSi: {campo:
concedeApelacion, igualA: "SI"}` and therefore never appear in single-instance flows. The
second-instance stages MUST NOT declare blocking `fechaLimite` deadlines (the document does
not set terms there).

#### Scenario: Granted appeal walks the full second instance
- GIVEN a double-instance proceso with `concedeApelacion = SI`
- WHEN advancing the workflow after `recurso`
- THEN it offers `remision2inst` → `sustentacion2inst` → `audiencia2inst` → `sentencia2inst`
- AND `sentencia2inst` records `decisionSegundaInstancia` ∈ {CONFIRMA, REVOCA, MODIFICA} before `terminada`

#### Scenario: Single-instance never reaches the second instance
- GIVEN a laboral proceso with `tipoInstancia = "Única instancia"`
- THEN none of `remision2inst`/`sustentacion2inst`/`audiencia2inst`/`sentencia2inst` is ever offered
