# Tramite Management Specification — delta (laboral-ficha-ux)

## ADDED Requirements

### Requirement: Laboral ficha groups fields by stage (presentation only)
In the detail (ficha) of a "Proceso Laboral" (grupo LABORAL), the editable data form MUST
present the fields **grouped into sections by stage**, in the flow order, each with a heading
and its fields in a **single column** — instead of a flat two-column grid. A section MUST be
shown only when its stage is available given the current `datos` (reusing the existing
`disponibleSi`/`mostrarSi`). Each document upload MUST remain inline under the field that
enables it (existing anchoring).

This is a presentation-only change: field requiredness, stage gating, save validation,
auto-advance, deadlines and document rules are unchanged. Other grupos (PETICION,
CONSTITUCIONAL, JUDICIAL) keep their current rendering.

#### Scenario: Admisión fields read top-to-bottom in their own section
- GIVEN a laboral proceso in the ficha, editing
- WHEN the form renders
- THEN "Decisión del auto", "Fecha del auto" and "Auto de calificación (PDF)" appear together under a "Calificación de la demanda" heading, in a single column (not split into left option / right date)

#### Scenario: Non-applicable sections are hidden
- GIVEN a laboral proceso in única instancia
- THEN the "Contestación (reforma / reconvención)" section (doble-instancia only) is not shown
- AND a proceso whose auto was not "INADMISIÓN" does not show the "Subsanación" section
