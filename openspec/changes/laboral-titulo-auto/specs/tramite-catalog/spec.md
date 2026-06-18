# Tramite Catalog Specification — delta (laboral-titulo-auto)

## MODIFIED Requirements

### Requirement: Auto-generated case title for constitutional actions
For types in grupo CONSTITUCIONAL (tutela), the client creation form MUST auto-generate the
case title as `"{tipo.nombre} — {entidad}"` and hide the manual "Título del caso" field,
the same way DdP (PETICION) does. The entidad MUST be sourced from `entidad` (DdP) or
`entidadAccionada` (tutela). The title MUST remain editable afterward in the ficha.

For types in **grupo LABORAL** (Proceso Laboral, Ley 2452/2025) the creation form MUST also
auto-generate the title and hide the manual field, but as a **two-party litigation** rather
than a trámite against an entity: `"{tipo.nombre} — {demandante} vs. {demandado}"`. The
ordering MUST be derived from the `rol` field ("Demandante" / "Demandado", the side the firm
represents) so the title is always demandante-first: if the firm represents the demandado, the
client name goes second. The opposing party (demandado/demandante) MUST be sourced from the
loaded partes (the one marked `DEMANDADO`, else the first parte); since it is optional at
creation, when absent the title MUST fall back to `"{tipo.nombre} — {cliente}"`. The title MUST
remain editable afterward in the ficha.

Other judicial types (grupo JUDICIAL: civil…) MUST keep a manual title.

## ADDED Requirements

### Requirement: Laboral party-role selectors are limited to demandante/demandado
For types in grupo LABORAL (Proceso Laboral, Ley 2452/2025 — an ordinary two-party suit),
the "Rol procesal del cliente" selector and the contraparte/partes "Rol procesal" selector
MUST offer only `DEMANDANTE` and `DEMANDADO`. The full `RolParte` list (EJECUTANTE, EJECUTADO,
ACCIONANTE, ACCIONADO, IMPUTADO, ACUSADO, VICTIMA, TERCERO, APODERADO, OTRO) belongs to other
jurisdictions (ejecutivo, constitucional, penal…) and MUST NOT be offered for a laboral
process. Other judicial types keep the full list.

#### Scenario: Laboral client role selector shows only two options
- GIVEN a lawyer is creating a "Proceso Laboral" (grupo LABORAL)
- WHEN the "Rol procesal del cliente" selector is opened
- THEN only "Demandante" and "Demandado" are offered
- AND the same applies to the contraparte's "Rol procesal" selector

#### Scenario: Non-laboral judicial type keeps the full role list
- GIVEN a lawyer is creating an executive or criminal process
- WHEN a party-role selector is opened
- THEN the full RolParte list (incl. ejecutante, acusado, víctima…) is offered

#### Scenario: Tutela created from scratch gets an auto title
- GIVEN a lawyer creates an "Acción de tutela" with `entidadAccionada = "Colpensiones"`
- WHEN the proceso is created
- THEN its título is "Acción de tutela — Colpensiones" without the lawyer typing it
- AND the título can be edited later in the ficha

#### Scenario: Laboral as demandante gets a demandante-vs-demandado title
- GIVEN a lawyer creates a "Proceso Laboral" with `rol = "Demandante"`, client "Juan Pérez"
  and a parte DEMANDADO "Aseguradora XYZ"
- WHEN the proceso is created without a manual title
- THEN its título is "Proceso Laboral — Juan Pérez vs. Aseguradora XYZ"

#### Scenario: Laboral as demandado keeps demandante-first ordering
- GIVEN a lawyer creates a "Proceso Laboral" with `rol = "Demandado"`, client "Empresa ABC"
  and a parte DEMANDADO "María Gómez" (the employee suing)
- WHEN the proceso is created
- THEN its título is "Proceso Laboral — María Gómez vs. Empresa ABC"

#### Scenario: Laboral without an opposing party yet
- GIVEN a lawyer creates a "Proceso Laboral" with client "Juan Pérez" and no partes
- WHEN the proceso is created
- THEN its título is "Proceso Laboral — Juan Pérez"
- AND the contraparte can be added later in the ficha
