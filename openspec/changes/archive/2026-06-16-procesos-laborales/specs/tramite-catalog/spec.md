# Tramite Catalog — delta: grupo LABORAL + seeded "Proceso Laboral"

## ADDED Requirements

### Requirement: Labor portal group (`GrupoProceso.LABORAL`)
The system MUST add `LABORAL` to `GrupoProceso` (alongside `JUDICIAL`, `PETICION`,
`CONSTITUCIONAL`). A `TipoProceso.grupo = "LABORAL"` MUST surface in a dedicated client
portal section **"Procesos Laborales"** rendered **below "Acciones Constitucionales"**,
with its own route `/procesos-laborales` (the section route map `SECCION_RUTA` MUST map
`LABORAL → "/procesos-laborales"`). Labor types MUST NOT appear in the generic judicial
creation wizard `/procesos/nuevo` (which MUST filter `esJudicial && grupo === "JUDICIAL"`);
they are created from their own section. The section MUST be visible to the `JURIDICO`
role (and the firm admin) and MUST reuse the existing `proceso.ver/crear/editar`
permissions (no new RBAC).

#### Scenario: Labor type lands in its own section
- GIVEN a `TipoProceso` with `grupo = "LABORAL"`
- WHEN a JURIDICO user opens the portal
- THEN a "Procesos Laborales" nav item appears below "Acciones Constitucionales"
- AND its processes are listed under `/procesos-laborales`, not under `/procesos`

#### Scenario: Labor type is excluded from the generic judicial wizard
- GIVEN the `/procesos/nuevo` wizard that groups judicial types by jurisdicción
- WHEN it lists selectable types
- THEN types with `grupo = "LABORAL"` are not offered (only `esJudicial && grupo = "JUDICIAL"`)

#### Scenario: Detail route derives from grupo
- GIVEN a labor `Proceso` with `grupo = "LABORAL"`
- WHEN a link to it is built via `rutaProceso`
- THEN the URL is `/procesos-laborales/{id}`

### Requirement: Seeded "Proceso Laboral" type (ordinario, Ley 2452/2025)
The catalog MUST seed a single global `TipoProceso` named **"Proceso Laboral"** with
`grupo = "LABORAL"`, `jurisdiccion = "ORDINARIA_LABORAL"`, `esJudicial = true`, tagged
with área `laboral`. Its `esquemaFormulario` MUST open with two required `select` fields
that drive the whole flow: `rol` (`Demandante` | `Demandado`) and `tipoInstancia`
(`Única instancia` | `Doble instancia`). Because the type is judicial, the radicado
(23 dígitos), juzgado/corporación and cuantía are provided by the built-in judicial form
and MUST NOT be redefined in `esquemaFormulario`. The pre-existing shallow stub "Proceso
ordinario laboral de primera instancia" MUST be removed (or marked obsolete) so only one
ordinary-labor flow is offered.

#### Scenario: Creating a labor process asks rol and instancia first
- GIVEN the seeded "Proceso Laboral" type
- WHEN a user opens its creation form
- THEN `rol` and `tipoInstancia` are required selects shown before the rest of the fields
- AND the radicado/juzgado/cuantía come from the built-in judicial fields (not duplicated)

#### Scenario: Single ordinary-labor flow in the catalog
- GIVEN the catalog after seeding
- WHEN labor ordinary types are listed
- THEN "Proceso Laboral" is present and "Proceso ordinario laboral de primera instancia" is not offered

### Requirement: Field branching by `rol` and `tipoInstancia` uses single-condition gates
Every conditional field in "Proceso Laboral" (`mostrarSi` / `requeridoSi`) MUST reference
exactly one field (the engine evaluates equality only; no AND/OR). Fields specific to the
double-instance flow MUST gate on `tipoInstancia = "Doble instancia"`; fields that depend
on a prior choice (e.g. the reconvención decision) MUST gate on that prior choice (e.g.
`hayReconvencion = "SI"`), which is itself double-only, so no rule ever needs rol AND
instancia together.

#### Scenario: Reconvención fields are double-instance only
- GIVEN `tipoInstancia = "Única instancia"`
- WHEN the form is rendered
- THEN `hayReconvencion`, `decisionReconvencion` and the contestación-detail fields are hidden

#### Scenario: Reconvención decision depends on a single prior field
- GIVEN `tipoInstancia = "Doble instancia"` and `hayReconvencion = "SI"`
- WHEN the form is rendered
- THEN `decisionReconvencion` is shown (gated only on `hayReconvencion`, a single condition)
