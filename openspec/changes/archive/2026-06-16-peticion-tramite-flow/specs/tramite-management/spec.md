# Tramite Management — delta: entity-trámite (petición) flow

## ADDED Requirements

### Requirement: Creation form hides stage-only fields (`soloFicha`)
A field in `esquemaFormulario` MAY declare `soloFicha: true`. Such a field MUST NOT render in the
**creation** form and MUST NOT be validated as required at creation. It MUST render in the **ficha** form
so it can be filled while advancing stages. Fields not marked `soloFicha` render at creation as before.

#### Scenario: Radication fields absent at creation
- GIVEN a `Derecho de Petición` whose `fechaRadicacion`, `nroRadicado`, `contestaron` are `soloFicha`
- WHEN a USUARIO opens the creation form
- THEN those fields are not shown and do not block submission
- AND they appear in the ficha when advancing to the Radicación / Respuesta stages

### Requirement: Two radicado dates for entity-trámites
An entity-trámite MUST distinguish two dates: `fechaRadicado` ("Fecha de radicación de solicitud"),
captured at creation as a reference and NOT driving any term; and `fechaRadicacion` ("Fecha de radicación
del proceso"), the entity's acuse-de-recibo date that MUST be the `plazoDesdeCampo` from which the legal
term is computed. `nroRadicado` MUST represent the radicado number assigned by the receiving entity.

#### Scenario: Term runs from the entity's radication date
- GIVEN a `Derecho de Petición` of type "General" (15 días hábiles)
- WHEN `fechaRadicacion` is set at the Radicación stage
- THEN `fechaLimite` is computed from `fechaRadicacion`, not from `fechaRadicado`

### Requirement: Auto-generated title for non-judicial trámites
When the trámite's `TipoProceso.esJudicial = false`, the system MUST auto-generate `titulo` as
`"{TipoProceso.nombre} — {entidad}"` and MUST hide the manual title field at creation. The title MUST be
editable from the ficha. Judicial types keep the manual title.

#### Scenario: DdP title derived from entity
- GIVEN a non-judicial `Derecho de Petición` with `entidad = "Colpensiones"`
- WHEN it is created without a manual title
- THEN `titulo` is `"Derecho de Petición — Colpensiones"`

### Requirement: Reiteración templates require a derived trámite
A `PlantillaDocumento` whose `contenido` references `{{casoBase...}}` MUST only be offered by
`GET /procesos/:id/plantillas` and accepted by `POST /procesos/:id/documentos/generar` and `/render`
when the trámite has `casoRelacionadoId != null`. On the original trámite it MUST be hidden, and direct
generation MUST be rejected with 422.

#### Scenario: Reiteración template hidden on the original
- GIVEN an original `Derecho de Petición` (no `casoRelacionadoId`)
- WHEN the document generator lists templates
- THEN "Reiteración de la petición" is not listed
- AND generating it returns 422

#### Scenario: Reiteración template available on the derivative
- GIVEN a reiterated `Derecho de Petición` (`casoRelacionadoId` set)
- WHEN the document generator lists templates
- THEN "Reiteración de la petición" is listed and can be generated

### Requirement: Derivative inherits the responsible lawyer
When `POST /procesos/:id/derivar` creates a `crearDerivado` trámite (reiteración or tutela), the new
trámite MUST inherit `responsableId` from the base trámite.

#### Scenario: Reiteración keeps the base lawyer
- GIVEN a `Derecho de Petición` whose `responsable` is lawyer L
- WHEN a reiteración is derived from it
- THEN the derivative's `responsableId` equals L

## MODIFIED Requirements

### Requirement: Response stage naming
The response stage of entity-trámites MUST be labelled **"Respuesta"** (previously "Contestación"). Its
rules MUST require, when `contestaron = SI`, the fields `fechaRespuesta` and the document `respuesta.pdf`;
when `contestaron = PARCIAL`, the fields `fechaRespuestaParcial` and `queFalto` plus `respuesta.pdf`, and
MAY offer an optional `recurso.pdf`. The informational field `respuestaDeFondo` MUST NOT be required (it
was removed as redundant with `contestaron`).

#### Scenario: Optional recurso on partial response
- GIVEN a `Reclamación Administrativa` at the "Respuesta" stage with `contestaron = PARCIAL`
- WHEN the response is recorded
- THEN `recurso.pdf` is offered as an optional document (not blocking)
