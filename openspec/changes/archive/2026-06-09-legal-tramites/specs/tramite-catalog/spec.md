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
A `TipoTramite` MUST carry `esquemaFormulario`: an ordered list of field definitions, each with
`key`, `label`, `tipo` (texto | textoLargo | numero | fecha | boolean | select | multiselect),
`requerido`, and `opciones` (required when `tipo` is select/multiselect). Field `key`s MUST be
unique within a type.

#### Scenario: Valid schema accepted
- GIVEN an ADMIN creating a type with two fields of unique keys
- WHEN the select field includes `opciones`
- THEN the type is created

#### Scenario: Select without options rejected
- GIVEN a field of `tipo` select with no `opciones`
- WHEN the type is submitted
- THEN the response status is 400

### Requirement: Staged workflow with rules
A `TipoTramite` MUST carry `etapas`: an ordered list of stages, each with `key`, `nombre`, `orden`,
and optional `reglas` (`camposRequeridos[]` referencing schema keys, `documentosRequeridos[]`
referencing template names, `plazoDias`). A type MUST define at least one stage; the first by
`orden` is the entry stage.

#### Scenario: Stages define order
- GIVEN a type with stages of `orden` 1, 2, 3
- WHEN it is created
- THEN the entry stage is the one with `orden` 1

#### Scenario: Rule references unknown field
- GIVEN a stage whose `camposRequeridos` lists a key absent from `esquemaFormulario`
- WHEN the type is submitted
- THEN the response status is 400

### Requirement: Document templates
A `TipoTramite` MAY have `PlantillaDocumento`s, each with `nombre` and `contenido` containing
`{{path}}` placeholders. Template names referenced by a stage's `documentosRequeridos` MUST exist
on the type.
