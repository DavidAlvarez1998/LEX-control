# Tramite Catalog Specification — delta (tutela-creacion-simple)

## MODIFIED Requirements

### Requirement: Tutela creation form is petition-like, not judicial-scaffolded
The creation form for an offensive "Acción de tutela" (the tutela we file —
`grupo === CONSTITUCIONAL` and `clienteOpcional !== true`) MUST NOT render the generic
judicial scaffolding that other litigation types use. Specifically it MUST NOT show:
- the **"Rol procesal del cliente"** selector — the client is always the **accionante**;
- the **"Datos judiciales"** card (radicado de 23 dígitos, juzgado, **cuantía** y valor) —
  a tutela has no cuantía, and its "radicado de la tutela" is a tracking field
  (`radicadoTutela`, `soloFicha`) filled later in the ficha;
- the **"Contraparte y otras partes"** card (litigantes con rol procesal) — the accionado is
  captured by the text field `entidadAccionada` ("Autoridad o particular accionado").

When the tutela is saved, the client's role MUST be persisted as `ACCIONANTE`.

The "Acción de Tutela (Recibida)" (defensive, `clienteOpcional: true`) is OUT OF SCOPE and
MUST keep its current behavior.

#### Scenario: Creating an offensive tutela hides judicial scaffolding
- GIVEN a lawyer creating an "Acción de tutela" (CONSTITUCIONAL, not clienteOpcional)
- WHEN the creation form renders
- THEN it does NOT show the "Rol procesal del cliente" selector
- AND it does NOT show the "Datos judiciales" card (cuantía/radicado 23díg/juzgado)
- AND it does NOT show the "Contraparte y otras partes" card

#### Scenario: Client is saved as accionante
- GIVEN an offensive tutela being created with a selected client
- WHEN the proceso is saved
- THEN the client party is persisted with rol `ACCIONANTE`

#### Scenario: Defensive received tutela is unchanged
- GIVEN a lawyer creating an "Acción de Tutela (Recibida)" (clienteOpcional)
- WHEN the creation form renders
- THEN the form behaves exactly as before this change

### Requirement: Tutela attachments are uploadable right after the client
After selecting the client, the offensive tutela creation form MUST surface the document
slots modeled in the `radicacion` stage so the lawyer can attach them at intake: `demanda.pdf`
(required) plus `pruebas.pdf` and `anexos.pdf` (optional). Both required AND optional attached
documents MUST be uploaded when the proceso is created (not only the required ones), so that
"subir Demanda, Pruebas y Anexos" works at creation time.

#### Scenario: Demanda, pruebas y anexos se ofrecen al crear
- GIVEN a lawyer creating an offensive tutela with a client already selected
- WHEN the form renders the documents section
- THEN it shows "Demanda" (required), "Pruebas" (opcional) y "Anexos" (opcional)

#### Scenario: Optional attachments are persisted at creation
- GIVEN a tutela being created with `pruebas.pdf` and/or `anexos.pdf` attached
- WHEN the proceso is created
- THEN those optional documents are uploaded and linked to the new proceso
- AND not silently dropped because they are optional
