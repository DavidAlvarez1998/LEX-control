# Tramite Management Specification — delta (laboral-flujo-doc)

## ADDED Requirements

### Requirement: Laboral workflow branches by rol × instancia per the source document
The "Proceso Laboral" workflow MUST follow the four flows of the source document
(`PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`): Demandante/Única, Demandante/Doble,
Demandado/Única, Demandado/Doble. Branching MUST be driven by `disponibleSi` on the etapas
(using AND/OR conditions over `rol` and `tipoInstancia`) and `mostrarSi` on the fields, NOT
by separate process types. The stage order MUST be: Presentación → Admisión (decisión del
auto) → [Subsanación | Recurso contra rechazo] → ¿Retiro art. 67? → Traslado y notificación →
Contestación (solo doble) → Preparación de audiencia → Citación → [Audiencia única | Audiencia
art. 77 + Audiencia art. 80] → Recurso (reposición en única / apelación en doble) →
Terminación/Archivo.

#### Scenario: Demandado/Única skips the admisión stage
- GIVEN a laboral proceso with `rol = Demandado` and `tipoInstancia = Única instancia`
- WHEN it advances from `presentacion`
- THEN the `admision` stage is not offered (it is skipped) and the next stage is `retiro`/`traslado`
- AND the audiencia is `audienciaUnica` and the post-sentence remedy is reposición

#### Scenario: Demandante/Doble walks art. 77 then art. 80
- GIVEN a laboral proceso with `rol = Demandante` and `tipoInstancia = Doble instancia`
- WHEN it reaches the audiencia phase
- THEN it offers `audienciaArt77` then `audienciaArt80` (not `audienciaUnica`)
- AND the contestación stage (reforma/reconvención + decisión del juez) is present
- AND the post-sentence remedy is apelación

### Requirement: Laboral deadlines follow the document ("créele al doc")
The laboral stages MUST compute `fechaLimite` per the document: contestación **10 días
hábiles** from `fechaNotificacion`; subsanación **5 días hábiles** from `fechaAdmision`;
recurso **3 días** from `fechaSentencia`. Business-day stages use `plazoTipoDias = "habiles"`
(Colombian holiday calendar already implemented).

#### Scenario: Contestación term is 10 business days from notification
- GIVEN a laboral proceso reaching the `traslado` stage with `fechaNotificacion` set
- THEN `fechaLimite` is 10 business days after `fechaNotificacion`

#### Scenario: Subsanación term is 5 business days from the inadmission
- GIVEN a laboral proceso whose `decisionAuto = INADMISIÓN` with `fechaAdmision` set
- WHEN it enters the `subsanacion` stage
- THEN `fechaLimite` is 5 business days after `fechaAdmision`
