# Tramite Management Specification

## Purpose
Define the lifecycle of a concrete legal case (`Tramite` / expediente): creating it from a catalog
type, filling and validating its dynamic form, moving it through rule-gated stages, attaching and
generating documents, and assigning a responsible lawyer — all scoped to the despacho. The despacho
is resolved per request from `req.user.sub` (the JWT carries only `{ sub, rol }`).

## Requirements

### Requirement: Create a trámite from a catalog type
A `USUARIO` MUST create a `Tramite` by choosing a visible `TipoTramite`. In a single transaction the
system MUST resolve the despacho from `req.user.sub`, set `empresaId`, record `creadoPorId`, assign a
per-empresa `codigoInterno`, copy the type's `jurisdiccion` onto the trámite, snapshot the type's
`esquemaVersion` into `tipoEsquemaVersion`, place the trámite in the type's entry stage, and create any
provided `ParteTramite` rows. Submitted `datos` MUST validate against the type's current
`esquemaFormulario`: every `requerido` field present, each value matching its field `tipo`,
select/multiselect values within `opciones`, and keys not in the schema rejected. The Colombian
first-class fields `radicado` (nullable — assigned by the court after filing), `despachoJuzgado`,
`cuantiaTipo`/`cuantiaSmlmv`/`cuantiaValor`, `instancia`, `proximaAudiencia`, and `casoRelacionadoId`
(links a tutela to its base case) are optional columns, not part of `datos`.

#### Scenario: Create with valid data
- GIVEN a visible type with one required text field
- WHEN a USUARIO creates a trámite providing that field
- THEN status is 201, a per-empresa `codigoInterno` is assigned, `radicado` is null, and the trámite
  is in the entry stage

#### Scenario: Link a tutela to its base case
- GIVEN an existing trámite of the despacho
- WHEN a USUARIO creates a tutela with `casoRelacionadoId` pointing to it
- THEN the tutela is created linked to that base case

#### Scenario: Missing required field
- GIVEN a type with a required field
- WHEN a USUARIO submits `datos` lacking it
- THEN the response status is 400 and no trámite is created

#### Scenario: Unknown key in datos
- GIVEN a type whose schema has no `foo` field
- WHEN `datos` includes `foo`
- THEN the response status is 400

#### Scenario: Type not visible to despacho
- GIVEN a type owned by another despacho
- WHEN a USUARIO references it on create
- THEN the response status is 404

#### Scenario: Atomic failure
- GIVEN a create whose party references a litigante of another despacho
- WHEN posted
- THEN status is 400 AND neither the trámite nor any party row is created

### Requirement: Trámite scoping
Every read/write of a `Tramite` MUST be scoped to the caller's despacho (resolved from
`req.user.sub`). A `USUARIO` MUST NOT access a trámite of another despacho (404 on miss). `Rol.ADMIN`
platform users are not despacho actors and MUST NOT create or own trámites.

#### Scenario: Cross-tenant read blocked
- GIVEN a trámite of despacho B
- WHEN a USUARIO of despacho A requests it by id
- THEN the response status is 404

### Requirement: List trámites with filters and pagination
`GET /tramites` MUST return only the caller's despacho's trámites, paginated, filterable by
`areaPractica`, `jurisdiccion`, `estado`, `responsableId`, `litiganteId`, and `radicado`, ordered by
`updatedAt` desc by default.

#### Scenario: Filter by estado
- GIVEN trámites in ABIERTO and CERRADO
- WHEN the USUARIO lists with `estado=ABIERTO`
- THEN only ABIERTO trámites of their despacho are returned

### Requirement: Dynamic form validation
`validarDatos(esquema, datos)` MUST validate filled `datos` against the type's `esquemaFormulario`,
returning the list of missing required fields. It MUST honor **conditional** rules: a field is reported
missing only when it is **effectively required** AND **visible** (per `requeridoSi`/`mostrarSi`); a
hidden field MUST never be reported missing even if `requerido: true`. The same pure helper MUST be the
source of truth shared by the client `<FormularioDinamico>` (which uses it to hide/show fields and to
mark the dynamic red asterisk) and the server. Editing `datos` after creation (`PATCH /procesos/:id`)
MUST validate against the schema but MAY allow incomplete drafts (required fields are enforced at stage
transition, not on save).

#### Scenario: Conditional required gates submission
- GIVEN a stage that requires `poderPdf` only when `requierePoder = true`
- WHEN `requierePoder = true` and `poderPdf` is empty
- THEN validation reports `poderPdf` missing and the API call is blocked

#### Scenario: Hidden required field does not block
- GIVEN a field `requerido: true` with `mostrarSi` not satisfied by current `datos`
- WHEN the form is submitted
- THEN validation passes (the hidden field is excluded)

### Requirement: Stage transitions — rule-gated, branched, terminal
Transitioning a `Proceso` to a target stage MUST satisfy that stage's effective `reglas` (all
`camposRequeridos` present in `datos`, all `documentosRequeridos` attached/generated, including those
added by a matching `requeridosSi`). A transition blocked by missing fields/documents MUST return 400
listing what is missing and MUST NOT change the stage. A stage carrying `disponibleSi` MUST only be
accepted as a next stage when its condition over `datos` holds; otherwise the move MUST be rejected 422
with a reason. Entering a stage whose rule defines a deadline (`plazoDesdeCampo`) MUST derive and persist
`Proceso.fechaLimite` (see `proceso-vencimientos`), without clobbering a manual override on re-entry.
Transitions MAY move backward or sideways (target rules validated independently); they are not
restricted to `orden+1`. Entering a `terminal` stage MUST set `estado = CERRADO`. Every successful
transition MUST append an `EtapaProceso` history entry (stage, user, timestamp, optional note).

#### Scenario: Transition blocked by missing document
- GIVEN a target stage requiring document "Demanda" not yet present
- WHEN a USUARIO advances the proceso to it
- THEN status is 400, the message names "Demanda", and the stage is unchanged

#### Scenario: Value-guarded branch availability
- GIVEN a DdP at `radicada` with stages `respondida` (disponibleSi contestaron=SI) and `escala_tutela`
  (=NO)
- WHEN `datos.contestaron = "NO"`
- THEN moving to `escala_tutela` succeeds and moving to `respondida` is rejected 422

#### Scenario: Entering a plazo stage sets the deadline
- GIVEN a DdP entering `radicada` with `fechaRadicacion` and `tipoPeticion` set
- WHEN the transition is applied
- THEN `fechaLimite` is derived and persisted

#### Scenario: Terminal stage closes the proceso
- GIVEN a terminal stage "Respondida"
- WHEN the proceso reaches it
- THEN `estado` becomes CERRADO

### Requirement: Derive a related proceso (escalation)
A stage carrying `accion: { tipo: 'crearDerivado', tipoDestinoNombre }` MUST, when invoked, create a new
`Proceso` of the named global `TipoProceso` in the same `empresaId`, with a fresh `codigoInterno`, its
own initial etapa, and `casoRelacionadoId` set to the origin proceso (using the existing
`casoRelacionado`/`derivados` relation). The action MUST be **idempotent**: at most one derived proceso
per `(casoRelacionadoId, tipoProcesoId)`; a repeat MUST return 409 with the existing derived proceso id.
The derived proceso MUST be tenant-scoped exactly like any other (no cross-despacho creation).

#### Scenario: DdP escalates to a linked tutela
- GIVEN a DdP at `escala_tutela` with `accion` targeting "Acción de tutela"
- WHEN the derive action is invoked
- THEN a new tutela proceso is created in the same despacho with `casoRelacionadoId` = DdP id

#### Scenario: Escalation is idempotent
- GIVEN a DdP that already derived a tutela
- WHEN the derive action is invoked again
- THEN the response is 409 referencing the existing tutela, and no duplicate is created

### Requirement: Estado lifecycle
`EstadoTramite` is ABIERTO | EN_PROCESO | SUSPENDIDO | CERRADO | ARCHIVADO. A CERRADO or ARCHIVADO
trámite MUST reject stage transitions (400) until reopened. Any `USUARIO` of the despacho MAY close,
reopen, or archive a trámite of their despacho.

#### Scenario: Closed trámite blocks transitions
- GIVEN a CERRADO trámite
- WHEN a USUARIO attempts a stage transition
- THEN the response status is 400

### Requirement: Schema-version pinning
A `Tramite` MUST validate `datos` against the `esquemaFormulario` of the version recorded in
`tipoEsquemaVersion`, not a later-edited catalog schema. Editing a `TipoTramite` MUST bump its
`esquemaVersion` and MUST NOT retroactively invalidate existing trámites.

#### Scenario: Catalog edit does not break in-flight trámites
- GIVEN a trámite opened under schema v1 and the type later edited to v2
- WHEN the trámite is read or transitioned
- THEN validation uses v1 and the trámite remains valid

### Requirement: Documents
A `USUARIO` MUST attach files (`DocumentoTramite`) to a trámite and MUST generate a document from one
of the type's templates. Generation MUST substitute placeholders (`datos.<key>`, `tramite.<field>`,
`parte.<rol>.<field>`) from the trámite and linked litigantes; an unresolved placeholder MUST render a
visible marker (not a silent blank) and MUST NOT fail. Generated output is an editable draft, not a
final pleading.

#### Scenario: Generate from template
- GIVEN a template "Demanda" with `{{datos.monto}}` and a trámite where `monto` = 5000
- WHEN the USUARIO generates it
- THEN a `DocumentoTramite` is produced with 5000 substituted in

### Requirement: Assign responsable
A trámite MAY have a `responsableId` referencing a `Usuario` of the same despacho. Assigning a user of
another despacho MUST be rejected with 400.

#### Scenario: Assign same-despacho lawyer
- GIVEN a lawyer of the same despacho
- WHEN set as `responsable`
- THEN the assignment succeeds

### Requirement: Procesos list supports text search and responsable filter
> ADDED by change `procesos-ux-ddp-tutela`.

`GET /procesos` MUST accept two optional read-only query params: `q` (free text matched case-insensitively against `codigoInterno`, `titulo`, the linked cliente `nombre`, and `radicado`) and `responsableId` (the abogado). Both MUST compose with the existing `area`/`estado` filters and remain hard-scoped to the token despacho (`WHERE { empresaId }`). The list UI MUST expose a search box and a responsable selector. No new permission is introduced (the existing `proceso.ver` gate applies).

#### Scenario: Find a DdP by its entity or title
- GIVEN procesos titled "DdP — EPS Salud Total" and "Tutela — Colpensiones"
- WHEN the user types "salud" in the search box
- THEN only the matching proceso(s) are listed, scoped to their despacho

#### Scenario: Filter by responsible lawyer
- GIVEN procesos assigned to abogados A and B
- WHEN the user selects abogado A in the responsable filter
- THEN only A's procesos show, and the filter composes with área/estado

#### Scenario: Search stays despacho-scoped
- GIVEN despacho X and despacho Y each have a proceso whose título contains "tutela"
- WHEN a user of despacho X searches "tutela"
- THEN only despacho X's proceso is returned

### Requirement: The list indicates a proceso belongs to a multi-node caso
> ADDED by change `procesos-ux-ddp-tutela`.

Each list row that is part of a caso with more than one node (i.e. it has a `casoRelacionadoId` or has derivados) MUST show a small "caso" indicator linking to the base proceso, so a reiteración or an escalated tutela is never read as an unrelated matter. The list stays flat and sortable (no tree collapse); the full chain is shown in the ficha.

#### Scenario: A reiteración is marked as part of its caso
- GIVEN a DdP and its reiteración (linked by `casoRelacionadoId`)
- WHEN the list renders the reiteración row
- THEN it shows a "caso" marker linking to the base DdP

#### Scenario: A standalone proceso shows no caso marker
- GIVEN a DdP with no base and no derivados
- WHEN the list renders its row
- THEN no caso marker is shown

### Requirement: Caso chain shows each node's current stage
> ADDED by change `procesos-ux-ddp-tutela`.

The `CasoChain` (rendered when the caso has more than one node) MUST show, for each node, its current stage name in addition to its estado and `fechaLimite`, and MUST remain legible on narrow viewports (horizontal scroll without clipping). The active node stays visually highlighted.

#### Scenario: Chain reads DdP → reiteración → tutela with stages
- GIVEN a caso DdP(terminada) → reiteración(radicada) → tutela(admisión)
- WHEN the ficha of any node renders the chain
- THEN each node shows its tipo, código, current stage, estado, and `fechaLimite`, with the open node highlighted

### Requirement: The continuity decision (reiterar / escalar) is a contextual CTA
> ADDED by change `procesos-ux-ddp-tutela`.

When the active stage defines a `crearDerivado` action, the ficha MUST present it as a prominent, clearly-labeled call-to-action (not a footnote of the stage list), with copy that distinguishes a **continuation of the same type** (DdP → reiteración: "Crear la reiteración") from an **escalation to another type** (DdP → tutela: "Crear {tipo}"), and that states the base proceso becomes the caso base. The CTA MUST respect the existing idempotency: once a derivado of that type exists, it links to it instead of creating a duplicate.

#### Scenario: Partial answer offers reiterar as a CTA
- GIVEN a DdP in the `reiteracion` stage (contestaron = PARCIAL)
- WHEN the ficha renders
- THEN a clear CTA offers "Crear la reiteración" describing it as a continuation linked as the same caso

#### Scenario: Silence offers escalar a tutela
- GIVEN a DdP in the `escala_tutela` stage (contestaron = NO)
- WHEN the ficha renders
- THEN a clear CTA offers "Crear Acción de tutela" described as an escalation of the same caso

#### Scenario: Existing derivado is linked, not duplicated
- GIVEN the reiteración already exists for a DdP
- WHEN the lawyer returns to the base DdP
- THEN the CTA shows "abrir expediente →" to the existing reiteración and does not offer to create another

### Requirement: Stage flow is legible for long and branched paths
> ADDED by change `procesos-ux-ddp-tutela`.

The stage stepper MUST show each stage's plazo when defined (`reglas.plazoDias` + `plazoTipoDias`), and MUST visually emphasize very short terms (e.g. the tutela impugnación = 3 días) so they are not missed. For branch stages that share an order and are mutually exclusive by `disponibleSi` (DdP respondida / reiteración / escala_tutela, keyed on `contestaron`), the UI MUST present only the applicable branch(es) as takeable and MUST make clear that they are alternatives driven by the response outcome — unavailable branches stay visible but dimmed/non-clickable (already the behavior), with one line of guidance.

#### Scenario: Tutela's 3-day impugnación term is emphasized
- GIVEN a tutela in `falloPrimeraInstancia` with the next stage `impugnacion` (3 días)
- WHEN the stepper renders
- THEN the impugnación term is shown and visually emphasized as a tight deadline

#### Scenario: DdP branches reflect the response
- GIVEN a DdP where `contestaron = PARCIAL`
- WHEN the stepper renders the order-2 branches
- THEN `reiteración` is takeable while `respondida` and `escala_tutela` are dimmed/non-clickable, with guidance that the path follows the response outcome

### Requirement: A field-blocked stage transition opens and marks the form
> ADDED by change `procesos-etapa-guia-campos`.

When the user clicks a stage and the move is rejected because required FIELDS are missing (the `400` `faltantes`), the ficha MUST scroll to the proceso form, put it in edit mode, and visually mark each missing field (required-asterisk + per-field error state) by passing the missing field keys to the form. The marks MUST clear per-field as each one receives a value (the highlight is filtered against the current draft). A short pointer message MUST replace the raw key list. This applies to any `TipoProceso` (DdP, tutela, judicial).

#### Scenario: DdP radicación block opens the form with both fields marked
- GIVEN a DdP whose `radicada` stage requires `fechaRadicacion` and `nroRadicado`, both empty
- WHEN the lawyer clicks the `radicada` stage
- THEN the view scrolls to the form, the form is in edit mode, and `fechaRadicacion` and `nroRadicado` are marked as required/missing

#### Scenario: A marked field clears as it is filled
- GIVEN the form is showing `nroRadicado` marked as missing
- WHEN the lawyer types a value into `nroRadicado`
- THEN that field's missing mark clears while still-empty required fields stay marked

#### Scenario: Tutela behaves the same
- GIVEN a tutela stage requiring fields that are empty
- WHEN the lawyer clicks that stage
- THEN the form opens and each missing field is marked (same mechanism, no type-specific code)

### Requirement: A document-blocked stage transition routes to the form (inline documents)
> ADDED by change `procesos-etapa-guia-campos`.

When the move is rejected because required DOCUMENTS are missing (the `400` `documentosFaltantes`), the ficha MUST scroll to the proceso form (in edit mode) — where each required document is an inline field of type archivo under its key — and show a short message naming the missing documents, rather than printing the raw list under the stage only. Because the documents are inline form fields, opening + scrolling to the form is sufficient (no separate documentos panel to highlight).

#### Scenario: Missing poder.pdf routes to the form
- GIVEN a DdP whose next stage requires `poder.pdf` and it is not attached
- WHEN the lawyer clicks that stage
- THEN the view scrolls to the form in edit mode with the message "Faltan documentos: poder.pdf — súbelos en el formulario"

#### Scenario: Mixed field+document block guides to the form for both
- GIVEN a stage that requires both a missing field and a missing document
- WHEN the lawyer clicks it
- THEN the form opens in edit mode, missing fields are marked, and the missing documents are named in the pointer message

### Requirement: Creation form hides stage-only fields (`soloFicha`)
> ADDED by change `peticion-tramite-flow`.

A field in `esquemaFormulario` MAY declare `soloFicha: true`. Such a field MUST NOT render in the
**creation** form and MUST NOT be validated as required at creation. It MUST render in the **ficha** form
so it can be filled while advancing stages. Fields not marked `soloFicha` render at creation as before.

#### Scenario: Radication fields absent at creation
- GIVEN a `Derecho de Petición` whose `fechaRadicacion`, `nroRadicado`, `contestaron` are `soloFicha`
- WHEN a USUARIO opens the creation form
- THEN those fields are not shown and do not block submission
- AND they appear in the ficha when advancing to the Radicación / Respuesta stages

### Requirement: Two radicado dates for entity-trámites
> ADDED by change `peticion-tramite-flow`.

An entity-trámite MUST distinguish two dates: `fechaRadicado` ("Fecha de radicación de solicitud"),
captured at creation as a reference and NOT driving any term; and `fechaRadicacion` ("Fecha de radicación
del proceso"), the entity's acuse-de-recibo date that MUST be the `plazoDesdeCampo` from which the legal
term is computed. `nroRadicado` MUST represent the radicado number assigned by the receiving entity.

#### Scenario: Term runs from the entity's radication date
- GIVEN a `Derecho de Petición` of type "General" (15 días hábiles)
- WHEN `fechaRadicacion` is set at the Radicación stage
- THEN `fechaLimite` is computed from `fechaRadicacion`, not from `fechaRadicado`

### Requirement: Auto-generated title for non-judicial trámites
> ADDED by change `peticion-tramite-flow`.

When the trámite's `TipoProceso.esJudicial = false`, the system MUST auto-generate `titulo` as
`"{TipoProceso.nombre} — {entidad}"` and MUST hide the manual title field at creation. The title MUST be
editable from the ficha. Judicial types keep the manual title.

#### Scenario: DdP title derived from entity
- GIVEN a non-judicial `Derecho de Petición` with `entidad = "Colpensiones"`
- WHEN it is created without a manual title
- THEN `titulo` is `"Derecho de Petición — Colpensiones"`

### Requirement: Reiteración templates require a derived trámite
> ADDED by change `peticion-tramite-flow`.

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
> ADDED by change `peticion-tramite-flow`.

When `POST /procesos/:id/derivar` creates a `crearDerivado` trámite (reiteración or tutela), the new
trámite MUST inherit `responsableId` from the base trámite.

#### Scenario: Reiteración keeps the base lawyer
- GIVEN a `Derecho de Petición` whose `responsable` is lawyer L
- WHEN a reiteración is derived from it
- THEN the derivative's `responsableId` equals L

### Requirement: Response stage naming
> ADDED by change `peticion-tramite-flow` (renames the prior "Contestación" stage to "Respuesta").

The response stage of entity-trámites MUST be labelled **"Respuesta"** (previously "Contestación"). Its
rules MUST require, when `contestaron = SI`, the fields `fechaRespuesta` and the document `respuesta.pdf`;
when `contestaron = PARCIAL`, the fields `fechaRespuestaParcial` and `queFalto` plus `respuesta.pdf`, and
MAY offer an optional `recurso.pdf`. The informational field `respuestaDeFondo` MUST NOT be required (it
was removed as redundant with `contestaron`).

#### Scenario: Optional recurso on partial response
- GIVEN a `Reclamación Administrativa` at the "Respuesta" stage with `contestaron = PARCIAL`
- WHEN the response is recorded
- THEN `recurso.pdf` is offered as an optional document (not blocking)

### Requirement: Send channel and proof when answering a received petition
> ADDED by change `ddp-recibido-completion`.

For `Derecho de Petición Recibido`, when we record that the petition was answered, the "Respuesta" stage
MUST require the send channel `medioRespuesta` for `contestada = SI` and `contestada = PARCIAL` (alongside
`fechaContestacion` and the `respuesta.pdf` document). The system MUST offer an optional proof-of-sending
document that depends on the channel: `acuse-correo.pdf` when `medioRespuesta = "Correo electrónico"`, and
`constancia-envio.pdf` when `medioRespuesta = "Físico"`. The proof document MUST NOT block stage advance.

#### Scenario: Answer by email
- GIVEN a `Derecho de Petición Recibido` at the "Respuesta" stage
- WHEN `contestada = SI` and `medioRespuesta = "Correo electrónico"`
- THEN `fechaContestacion`, `medioRespuesta` and `respuesta.pdf` are required to complete the stage
- AND `acuse-correo.pdf` is offered as an optional document

#### Scenario: Answer physically
- GIVEN a `Derecho de Petición Recibido` at the "Respuesta" stage
- WHEN `contestada = SI` and `medioRespuesta = "Físico"`
- THEN `constancia-envio.pdf` is offered as an optional document

#### Scenario: Channel is mandatory to complete the response
- GIVEN `contestada = SI` with `fechaContestacion` and `respuesta.pdf` provided
- WHEN `medioRespuesta` is empty
- THEN the stage cannot be completed until `medioRespuesta` is set
