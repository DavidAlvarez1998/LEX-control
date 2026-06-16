# Tramite Catalog Specification — delta (tutela-form-hibrida)

## MODIFIED Requirements

### Requirement: Tutela schema is creation-light, ficha-complete (hybrid)
The "Acción de tutela" type (grupo CONSTITUCIONAL) MUST keep a **short creation form** that
mirrors the client requirements doc: at creation the only substantive field is
`entidadAccionada` ("Autoridad o particular accionado"), which MUST be visible and required.
All other substantive fields (`derechosFundamentales`, `hechos`, `pretension`,
`existeOtroMedioDefensa`, `perjuicioIrremediable`, `medidaProvisional`, `juramentoNoTutela`,
`fechaPresentacion`) and all tracking fields (`radicadoTutela`, `admitida`,
`fechaAutoAdmisorio`, `falloPrimera`, `fechaFallo`, `impugnada`, `falloSegunda`,
`incidenteDesacato`, `fechaIncidenteDesacato`) MUST be `soloFicha: true` and
`requerido: false`: hidden at creation, editable in the ficha as the case advances.

These fields MUST continue to EXIST in the schema (not be deleted) so the `DEMANDA_TUTELA`
document template can still generate the writ when a lawyer chooses to fill them in the ficha.
The document-generation capability MUST be preserved.

#### Scenario: Creating a tutela shows a short form
- GIVEN a lawyer creating an "Acción de tutela"
- WHEN the creation form renders
- THEN it shows `entidadAccionada` (required) and the client/accionante selector
- AND it does NOT show hechos, pretensión, derechos fundamentales, juramento, ni los campos de seguimiento

#### Scenario: Substantive fields remain available for document generation
- GIVEN a tutela already created
- WHEN the lawyer edits the proceso form in the ficha
- THEN hechos, pretensión, derechos fundamentales y demás campos están disponibles para llenar
- AND generating the demanda from the `DEMANDA_TUTELA` template uses those values

### Requirement: Tutela stage gating follows the "attach, don't type" model
The tutela workflow MUST gate stage advancement on attached documents rather than on typing
the substantive intake. Etapa `radicacion` MUST require only `entidadAccionada` plus the
existing `demanda.pdf` document; it MUST NOT require `hechos`/`pretension`/
`derechosFundamentales`/`existeOtroMedioDefensa`. Etapa `falloPrimeraInstancia` MUST NOT
require `pretension`; recording the fallo requires the existing `sentencia.pdf`. The document
slots already modeled in the stages (`demanda.pdf`, `pruebas.pdf`, `anexos.pdf`,
`auto_admisorio.pdf`, `sentencia.pdf`, `impugnacion.pdf`, `sentencia_segunda.pdf`,
`escrito_desacato.pdf`, `fallo_desacato.pdf`) MUST remain unchanged.

#### Scenario: Advance radicación by attaching the demanda
- GIVEN a tutela in etapa `radicacion` with `entidadAccionada` set
- WHEN the lawyer attaches `demanda.pdf` and advances
- THEN the stage advances WITHOUT requiring hechos/pretensión/derechos to be typed

### Requirement: Auto-generated case title for constitutional actions
For types in grupo CONSTITUCIONAL (tutela), the client creation form MUST auto-generate the
case title as `"{tipo.nombre} — {entidad}"` and hide the manual "Título del caso" field,
the same way DdP (PETICION) does. The entidad MUST be sourced from `entidad` (DdP) or
`entidadAccionada` (tutela). The title MUST remain editable afterward in the ficha. Other
judicial types (grupo JUDICIAL: laboral, civil…) MUST keep a manual title.

#### Scenario: Tutela created from scratch gets an auto title
- GIVEN a lawyer creates an "Acción de tutela" with `entidadAccionada = "Colpensiones"`
- WHEN the proceso is created
- THEN its título is "Acción de tutela — Colpensiones" without the lawyer typing it
- AND the título can be edited later in the ficha
