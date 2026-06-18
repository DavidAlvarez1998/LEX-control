# Tramite Catalog Specification — delta (tutela-seguimiento-flujo)

## MODIFIED Requirements

### Requirement: Named document slots are uploadable in the ficha for types without DdP anchors
The proceso ficha (`procesos/[id]`, shared by peticiones and acciones constitucionales) MUST
let the user upload the **named documents** declared by a type's stages
(`documentosRequeridos`/`documentosOpcionales`/`requeridosSi`/`opcionalesSi`) directly in the
edit form, even for types that do NOT have the DdP anchor fields (`requierePoder`,
`queSolicita`, `contestaron`, `contestada`).

`DatosProceso` MUST render a "Documentos del proceso" block listing every document for the
current `datos` that is NOT already shown in an anchored block, each with an inline upload
control (`BotonSubirDoc`, real upload). For DdP-style types (all docs anchored) this set is
empty and the ficha MUST be unchanged. The list MUST grow with case progress (it is derived
from `documentos…DeEtapas(etapas, borrador)`).

#### Scenario: Tutela ficha lets you attach its tracking documents
- GIVEN a tutela being tracked in its ficha
- WHEN the lawyer edits the form and sets `admitida = SI`
- THEN an "Auto admisorio" upload slot appears in the "Documentos del proceso" block
- AND setting `falloPrimera` shows a "Sentencia" upload slot
- AND each can be uploaded inline (not only attached by URL)

#### Scenario: DdP ficha is unchanged
- GIVEN a Derecho de Petición ficha
- WHEN the edit form renders
- THEN its documents still appear under their anchored fields (requierePoder / contestaron)
- AND no duplicate "Documentos del proceso" block appears (the unanchored set is empty)

### Requirement: Tutela tracking documents are contextual (appear as the case advances)
The tutela stages MUST surface tracking documents as optional attachments conditioned on the
case state, mirroring the client doc, instead of fixed required documents:
- `admision`: `auto_admisorio.pdf` only when `admitida = SI`.
- `falloPrimeraInstancia`: `sentencia.pdf` only when `falloPrimera ∈ {Favorable, Desfavorable}`.
- `impugnacion`: `impugnacion.pdf` optional (the stage is already gated by `impugnada = SI`).
- `falloSegundaInstancia`: `sentencia_segunda.pdf` when `impugnada = SI`; plus
  `escrito_desacato.pdf` and `fallo_desacato.pdf` when `incidenteDesacato = SI`.
- `radicacion`: `demanda.pdf` REMAINS required (the tutela cannot be filed without it);
  `pruebas.pdf`/`anexos.pdf` stay optional.

This supersedes, for tutela only, the prior rule that recording the fallo required
`sentencia.pdf` and that admisión required `auto_admisorio.pdf` (now contextual optionals).

#### Scenario: Auto admisorio appears only after admisión
- GIVEN a tutela where `admitida` is empty
- THEN no "Auto admisorio" slot is offered
- WHEN `admitida = SI`
- THEN the "Auto admisorio" slot is offered (optional)

### Requirement: Tutela captures the impugnación date
The tutela schema MUST include `fechaImpugnacion` (type `fecha`, `soloFicha`,
`mostrarSi: impugnada = SI`) so that answering "¿Se impugnó el fallo? = Sí" reveals a date
field, per the client doc (impugnación term: 3 días hábiles from notification).

#### Scenario: Impugnación date shown when impugnada
- GIVEN a tutela ficha
- WHEN `impugnada = SI`
- THEN a "Fecha de la impugnación" field is shown
- AND it is hidden when `impugnada` is NO or empty
