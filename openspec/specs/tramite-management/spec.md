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
