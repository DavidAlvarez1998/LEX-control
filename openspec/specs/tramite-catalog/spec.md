# Tramite Catalog Specification

## Purpose
Define the configurable catalog of legal process types (`TipoTramite`) for COLOMBIAN practice. Each
type belongs to a `jurisdiccion` (the procedural regime that drives its stages) and is tagged with one
or more `areaPractica` (how a firm organizes). Each type carries the dynamic intake form, the staged
workflow with rules, and document templates. The catalog is hybrid: platform-global types plus
per-despacho types.

## Requirements

### Requirement: Áreas de práctica and jurisdicciones
The system MUST distinguish `areaPractica` (a seeded, extensible set — e.g. civil, comercial, laboral,
administrativo, penal, familia, constitucional, tributario, inmobiliario, migratorio, seguridad
social) from `jurisdiccion` (a fixed procedural regime: ORDINARIA_CIVIL, ORDINARIA_LABORAL,
CONTENCIOSO_ADMIN, PENAL, CONSTITUCIONAL, FAMILIA). Every `TipoTramite` MUST belong to exactly one
`jurisdiccion` and MUST be tagged with at least one `areaPractica`. Seguridad social MUST route to
ORDINARIA_LABORAL; inmobiliario to ORDINARIA_CIVIL; migratorio and tributario to CONTENCIOSO_ADMIN.

#### Scenario: List áreas de práctica
- GIVEN any authenticated lawyer
- WHEN they request the áreas de práctica
- THEN the response lists the seeded areas

#### Scenario: Type carries jurisdiccion and area tags
- GIVEN a type for "Proceso ejecutivo"
- WHEN it is created with jurisdiccion ORDINARIA_CIVIL and areas [civil, comercial]
- THEN it appears under both the civil and comercial practice areas

### Requirement: Catalog ownership and visibility
A `TipoTramite` MUST have an optional `empresaId`: `null` = global (platform catalog), set = owned by
that despacho. A despacho user MUST see global types plus its own, and MUST NOT see another despacho's
types. Authorization (the JWT carries `{ sub, rol }`; per-request the user is loaded for the despacho
and the `esAdminEmpresa` flag):
- Global types (`empresaId = null`): only `Rol.ADMIN` MAY create/edit/delete (`requireRole(ADMIN)`).
- Despacho-owned types: only a `USUARIO` with `esAdminEmpresa = true` of that despacho MAY
  create/edit/delete; a regular `USUARIO` MAY read but not write.
Because MySQL treats NULL as distinct in unique indexes, global-type uniqueness MUST be enforced via a
non-null sentinel `empresaKey` (= `empresaId ?? ""`) carrying `@@unique([empresaKey, nombre])`, plus an
application-level pre-insert check.

#### Scenario: Despacho sees global plus own
- GIVEN a global type "Divorcio" and a despacho-owned type "Consulta exprés"
- WHEN a USUARIO of that despacho lists the catalog for FAMILIAR
- THEN both types are returned

#### Scenario: Isolation from other despachos
- GIVEN a type owned by despacho B
- WHEN a USUARIO of despacho A lists the catalog
- THEN despacho B's type is NOT returned

#### Scenario: Regular USUARIO cannot edit a global type
- GIVEN a `USUARIO` token (any `esAdminEmpresa`)
- WHEN they PATCH a global (`empresaId = null`) type
- THEN the response status is 403

#### Scenario: esAdminEmpresa edits only its own type
- GIVEN a `USUARIO` with `esAdminEmpresa = true` of despacho A
- WHEN they PATCH a type owned by despacho B
- THEN the response status is 404

#### Scenario: Duplicate global type rejected
- GIVEN a global type named "Proceso ejecutivo"
- WHEN an ADMIN creates another global type named "Proceso ejecutivo"
- THEN the response status is 409

### Requirement: Dynamic form schema
A `TipoProceso` MUST carry `esquemaFormulario`: an ordered list of field definitions, each with `key`,
`label`, `tipo` (texto | textoLargo | numero | fecha | boolean | select | multiselect), `requerido`,
and `opciones` (required when `tipo` is select/multiselect). Field `key`s MUST be unique.

Each field MAY additionally carry **conditional** keys (all optional; absent ⇒ unchanged behavior):
- `mostrarSi: { campo, igualA }` — the field is hidden unless `datos[campo]` equals `igualA` (string) or
  is included in `igualA` (string[]).
- `requeridoSi: { campo, igualA }` — the field is **additionally** required when the condition holds.

A field is **effectively required** iff (`requerido === true` OR `requeridoSi` holds) AND the field is
**visible** (`mostrarSi` absent or satisfied). Conditions use equality only (no AND/OR trees, no
arithmetic). A condition referencing a non-existent `campo` MUST be rejected at catalog save time.

#### Scenario: Existing type without conditional keys is unchanged
- GIVEN a `TipoProceso` whose fields use only `requerido`
- WHEN it is validated and rendered
- THEN behavior is identical to before this change (conditional keys absent)

#### Scenario: Conditional required field
- GIVEN a field `poderPdf` with `requeridoSi: { campo: "requierePoder", igualA: "true" }`
- WHEN `datos.requierePoder = true`
- THEN `poderPdf` is effectively required; WHEN `false` it is not

#### Scenario: Hidden field is never required
- GIVEN a field with `mostrarSi: { campo: "contestaron", igualA: "PARCIAL" }` and `requerido: true`
- WHEN `datos.contestaron = "SI"`
- THEN the field is hidden and is NOT reported as missing

#### Scenario: Condition references unknown field rejected
- GIVEN a catalog save where a field's `mostrarSi.campo` is not a defined field key
- WHEN the type is created/updated
- THEN the response status is 422

### Requirement: Staged workflow with rules
A `TipoProceso` MUST carry `etapas`: an ordered list of `{ key, nombre, orden, terminal?, reglas? }`.
`reglas` MAY include `camposRequeridos`, `documentosRequeridos`, and `plazoDias` (positive int — the
EXISTING informational term, unchanged) and MAY additionally include (all optional):
- `requeridosSi: [{ si: { campo, igualA }, camposRequeridos?, documentosRequeridos? }]` — extra required
  fields/documents that apply only when the condition holds.
- `plazoDesdeCampo` (a `fecha` field key), `plazoTipoDias` ('habiles' | 'calendario', default
  'calendario'), and `plazoDiasPorValorDe: { campo, mapa }` — a deadline derivation that EXTENDS
  `plazoDias` (see `proceso-vencimientos`). A `fechaLimite` is derived only when `plazoDesdeCampo` is
  present; the term is `plazoDiasPorValorDe.mapa[datos[campo]]` if set, else `plazoDias`. A rule with
  only `plazoDias` (every seeded tipo today) stays informational — no derivation, no behavior change.
- An etapa MAY carry `disponibleSi: { campo, igualA }` — gating which next stages are offered.
- An etapa MAY carry `accion: { tipo: 'crearDerivado', tipoDestinoNombre }` — a derive action (see
  `tramite-management`).

Rule field references (`camposRequeridos`, `requeridosSi[].si.campo`, `plazoDesdeCampo`,
`disponibleSi.campo`, `plazoDiasPorValorDe.campo`) MUST reference defined field keys;
`accion.tipoDestinoNombre` MUST name an existing global `TipoProceso`. Violations MUST be rejected at
save time (422). The first stage by `orden` is the entry stage; a type MUST define at least one stage.

#### Scenario: Existing plazoDias-only stage stays informational
- GIVEN a seeded stage with `reglas.plazoDias = 10` and no `plazoDesdeCampo`
- WHEN a proceso enters it
- THEN no `fechaLimite` is derived (behavior unchanged from before this change)

#### Scenario: Stage plazo by field value
- GIVEN a stage with `plazoDesdeCampo = "fechaRadicacion"` and `plazoDiasPorValorDe = { campo: "tipoPeticion", mapa: { Documental: 10 } }`
- WHEN the stage is saved
- THEN it is accepted and the mapa drives the deadline term at runtime

#### Scenario: Rule references unknown field
- GIVEN a stage whose `camposRequeridos` lists a key absent from `esquemaFormulario`
- WHEN the type is submitted
- THEN the response status is 422

#### Scenario: Derive action names a real global type
- GIVEN a stage with `accion: { tipo: "crearDerivado", tipoDestinoNombre: "Acción de Tutela" }`
- WHEN no global type "Acción de Tutela" exists
- THEN the catalog save is rejected 422

### Requirement: Document templates
A `TipoProceso` MAY have `PlantillaDocumento`s, each with `nombre` and `contenido` containing
`{{path}}` placeholders. Template names referenced by a stage's `documentosRequeridos` MUST exist
on the type.

### Requirement: Seeded constitucional types (DdP + Tutela)
The global catalog MUST seed two CONSTITUCIONAL `TipoProceso` rows available to every despacho:
**"Derecho de Petición"** and **"Acción de tutela"**, with the esquemaFormulario, etapas, plazo rules
(DdP: 15/10/30 business days by tipoPeticion), conditional rules (poder, contestaron branches), and the
DdP `escala_tutela` derive action targeting "Acción de tutela".

#### Scenario: DdP available to a despacho
- GIVEN a fresh despacho
- WHEN it lists the CONSTITUCIONAL catalog
- THEN "Derecho de Petición" and "Acción de tutela" (global) are present

#### Scenario: Both seed under the Constitucional area
- GIVEN the seeded "Derecho de Petición" and "Acción de tutela"
- WHEN their jurisdicción and áreas are inspected
- THEN both have `jurisdiccion = CONSTITUCIONAL` and are tagged with the `constitucional` áreaPractica

#### Scenario: Seeded DdP carries the term mapa
- GIVEN the seeded "Derecho de Petición"
- WHEN its `radicada` stage is inspected
- THEN it carries `plazoDesdeCampo = "fechaRadicacion"`, `plazoTipoDias = "habiles"`, and
  `plazoDiasPorValorDe` with terms 15/10/30 for General/Documental/Consulta

### Requirement: Labor portal group (`GrupoProceso.LABORAL`)
> ADDED by change `procesos-laborales`.

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
> ADDED by change `procesos-laborales`.

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
> ADDED by change `procesos-laborales`.

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
