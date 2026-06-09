# Tramite Management Specification (delta)

## MODIFIED Requirements

### Requirement: Dynamic form validation
`validarDatos(esquema, datos)` MUST validate filled `datos` against the type's `esquemaFormulario`,
returning the list of missing required fields. It MUST honor **conditional** rules: a field is reported
missing only when it is **effectively required** AND **visible** (per `requeridoSi`/`mostrarSi`); a
hidden field MUST never be reported missing even if `requerido: true`. The same pure helper MUST be the
source of truth shared by the client `<FormularioDinamico>` (which uses it to hide/show fields and to
mark the dynamic red asterisk) and the server.

#### Scenario: Conditional required gates submission
- GIVEN a stage that requires `poderPdf` only when `requierePoder = true`
- WHEN `requierePoder = true` and `poderPdf` is empty
- THEN validation reports `poderPdf` missing and the API call is blocked

#### Scenario: Hidden required field does not block
- GIVEN a field `requerido: true` with `mostrarSi` not satisfied by current `datos`
- WHEN the form is submitted
- THEN validation passes (the hidden field is excluded)

### Requirement: Rule-gated stage transitions
A stage transition MUST be blocked when the target stage's effective required fields/documents
(including `requeridosSi` matches) are missing, returning 422 with which fields/documents are missing.
A stage carrying `disponibleSi` MUST only be offered/accepted as a next stage when its condition over
`datos` holds; attempting to move to a non-available stage MUST be rejected 422 with a reason. Entering
a stage with a `plazo` rule MUST derive `Proceso.fechaLimite` (see `proceso-vencimientos`). A `terminal`
stage MUST close the proceso.

#### Scenario: Value-guarded branch availability
- GIVEN a DdP at `radicada` with stages `respondida` (disponibleSi contestaron=SI), `reiteracion`
  (=PARCIAL), `escala_tutela` (=NO)
- WHEN `datos.contestaron = "NO"`
- THEN only `escala_tutela` is offered as a next stage; moving to `respondida` is rejected 422

#### Scenario: Entering a plazo stage sets the deadline
- GIVEN a DdP entering `radicada` with `fechaRadicacion` and `tipoPeticion` set
- WHEN the transition is applied
- THEN `fechaLimite` is derived and persisted

## ADDED Requirements

### Requirement: Derive a related proceso (escalation)
A stage carrying `accion: { tipo: 'crearDerivado', tipoDestinoNombre }` MUST, when invoked, create a new
`Proceso` of the named global `TipoProceso` in the same `empresaId`, with a fresh `codigoInterno`, its
own initial etapa, and `casoRelacionadoId` set to the origin proceso (using the existing
`casoRelacionado`/`derivados` relation). The action MUST be **idempotent**: at most one derived proceso
per `(casoRelacionadoId, tipoProcesoId)`; a repeat MUST return 409 with the existing derived proceso id.
The derived proceso MUST be tenant-scoped exactly like any other (no cross-despacho creation).

#### Scenario: DdP escalates to a linked tutela
- GIVEN a DdP at `escala_tutela` with `accion` targeting "Acción de Tutela"
- WHEN the derive action is invoked
- THEN a new "Acción de Tutela" proceso is created in the same despacho with `casoRelacionadoId` = DdP id

#### Scenario: Escalation is idempotent
- GIVEN a DdP that already derived a tutela
- WHEN the derive action is invoked again
- THEN the response is 409 referencing the existing tutela, and no duplicate is created

#### Scenario: Origin and derivado are linked both ways
- GIVEN a DdP that derived a tutela
- WHEN the DdP is fetched
- THEN the tutela appears under its `derivados`, and the tutela's `casoRelacionado` is the DdP
