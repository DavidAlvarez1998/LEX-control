# Tramite Management — delta: labor ordinary workflow (rol × instancia)

## ADDED Requirements

### Requirement: Stage sequence branches by `tipoInstancia`
The "Proceso Laboral" workflow MUST share early stages for both instancias and branch the
later stages by `tipoInstancia` using `disponibleSi` (a single equality condition per
stage). Stages sharing the same `orden` with different `disponibleSi` are alternative
branches of the same step. The double-instance flow MUST expose `contestacion` (orden 4),
`audienciaArt77` (orden 7) and `audienciaArt80` (orden 8); the single-instance flow MUST
expose `audienciaUnica` (orden 7) instead, and MUST NOT expose `contestacion`,
`audienciaArt77` or `audienciaArt80`. Both flows share `presentacion` (0), `admision` (1),
`traslado` (3), `preparacionAudiencia` (5), `citacionAudiencia` (6), `sentencia` (9) and
the terminal `terminada` (10).

#### Scenario: Single-instance skips the double-instance stages
- GIVEN a "Proceso Laboral" with `tipoInstancia = "Única instancia"`
- WHEN the next available stages are computed after `traslado`
- THEN `contestacion`, `audienciaArt77` and `audienciaArt80` are NOT offered
- AND after `citacionAudiencia` the next stage is `audienciaUnica`, then `sentencia`

#### Scenario: Double-instance walks the full audiencia chain
- GIVEN a "Proceso Laboral" with `tipoInstancia = "Doble instancia"`
- WHEN advancing the workflow
- THEN the path includes `contestacion` (orden 4) and `audienciaArt77` → `audienciaArt80` (orden 7 → 8) before `sentencia`

### Requirement: Admisión branches (admisión / inadmisión+subsanación / rechazo+recurso)
At `admision` the user MUST record `decisionAdmision` ∈ {`ADMISIÓN`, `INADMISIÓN`,
`RECHAZO`}. When `decisionAdmision = INADMISIÓN`, the `subsanacion` stage (orden 2) MUST
become available and MUST compute `fechaLimite` as **5 días hábiles** from
`fechaInadmision` (`plazoDesdeCampo: fechaInadmision`, `plazoTipoDias: habiles`,
`plazoDias: 5`); it records `decisionTrasSubsanacion` ∈ {`ADMISIÓN`, `RECHAZO`}. When
`decisionAdmision = RECHAZO`, the `recurso_rechazo` stage (orden 2) MUST become available
to record `recursoRechazo` and `decisionRecursoRechazo`. A conditional deadline MUST only
be declared on stages whose source date field is guaranteed present (so `derivarFechaLimite`
never receives an empty source).

#### Scenario: Inadmisión opens subsanación with a 5-business-day deadline
- GIVEN `decisionAdmision = "INADMISIÓN"` with `fechaInadmision` set
- WHEN the case advances to `subsanacion`
- THEN `fechaLimite` is `fechaInadmision` + 5 días hábiles (Colombian holidays applied)

#### Scenario: Admisión directa skips the subsanación branch
- GIVEN `decisionAdmision = "ADMISIÓN"`
- WHEN the next stages are computed
- THEN neither `subsanacion` nor `recurso_rechazo` is offered

### Requirement: Traslado runs the 10-business-day contestación term
The `traslado` stage MUST compute `fechaLimite` as **10 días hábiles** from
`fechaNotificacion` (`plazoDesdeCampo: fechaNotificacion`, `plazoTipoDias: habiles`,
`plazoDias: 10`), representing the term for the defendant to answer the demand.

#### Scenario: Contestación deadline derived from notification date
- GIVEN `fechaNotificacion` is set at the `traslado` stage
- WHEN `fechaLimite` is derived
- THEN it equals `fechaNotificacion` + 10 días hábiles

### Requirement: Contestación, reforma and reconvención (double-instance)
At `contestacion` (double-instance only), when `contestaron = SI` the stage MUST require
`fechaContestacion` and the document `contestacion.pdf`; when `contestaron = NO` it MUST
require the document `auto-silencio.pdf`. When `hayReforma = SI` it MUST offer
`demanda-reformada.pdf` as optional, and when `hayReconvencion = SI` it MUST offer
`reconvencion.pdf` as optional and expose `decisionReconvencion` ∈ {`ADMITIR`, `INADMITIR`,
`RECHAZAR`}. Documents declared optional MUST NOT block stage advance.

#### Scenario: Answered demand requires the contestación document
- GIVEN a double-instance case at `contestacion` with `contestaron = SI`
- WHEN completing the stage
- THEN `fechaContestacion` and `contestacion.pdf` are required

#### Scenario: Reconvención offered without blocking
- GIVEN `hayReconvencion = SI`
- WHEN the stage is shown
- THEN `reconvencion.pdf` is offered as optional and `decisionReconvencion` is captured

### Requirement: Sentencia, recurso and retiro/archivo terminals
At `sentencia` the user MUST record `decisionSentencia` ∈ {`Favorable`, `Desfavorable`},
the document `sentencia.pdf`, and `hayRecurso`. When `hayRecurso = SI` the system MUST
offer the recurso document and capture `decisionRecurso`; the recurso is labelled
**reposición** in single-instance and **apelación** in double-instance (term: en audiencia
o por escrito dentro de **3 días calendario**, derived at `sentencia` from `fechaSentencia`
— `plazoTipoDias: calendario`; the source document does not qualify these as hábiles).
At any point before sentencia, when `hayRetiro = SI`
(art. 67) the terminal `archivado` stage MUST become available; otherwise the workflow
ends at the terminal `terminada`.

#### Scenario: Retiro de la demanda archives the process
- GIVEN a "Proceso Laboral" with `hayRetiro = SI`
- WHEN the available stages are computed
- THEN the terminal `archivado` is offered with resultado "Demanda retirada y archivada (art. 67)"

#### Scenario: Recurso offered after an adverse judgment
- GIVEN `decisionSentencia = "Desfavorable"` and `hayRecurso = SI`
- WHEN the sentencia stage is completed
- THEN the recurso document is offered and `decisionRecurso` is captured (no blocking)
