# Tramite Catalog Specification (delta)

## MODIFIED Requirements

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
save time (422).

#### Scenario: Existing plazoDias-only stage stays informational
- GIVEN a seeded stage with `reglas.plazoDias = 10` and no `plazoDesdeCampo`
- WHEN a proceso enters it
- THEN no `fechaLimite` is derived (behavior unchanged from before this change)

#### Scenario: Stage plazo by field value
- GIVEN a stage with `plazoDesdeCampo = "fechaRadicacion"` and `plazoDiasPorValorDe = { campo: "tipoPeticion", mapa: { Documental: 10 } }`
- WHEN the stage is saved
- THEN it is accepted and the mapa drives the deadline term at runtime

#### Scenario: Derive action names a real global type
- GIVEN a stage with `accion: { tipo: "crearDerivado", tipoDestinoNombre: "Acción de Tutela" }`
- WHEN no global type "Acción de Tutela" exists
- THEN the catalog save is rejected 422

## ADDED Requirements

### Requirement: Seeded constitucional types (DdP + Tutela)
The global catalog MUST seed two CONSTITUCIONAL `TipoProceso` rows available to every despacho:
**"Derecho de Petición"** and **"Acción de Tutela"**, with the esquemaFormulario, etapas, plazo rules
(DdP: 15/10/30 business days by tipoPeticion), conditional rules (poder, contestaron branches), and the
DdP `escala_tutela` derive action targeting "Acción de Tutela".

#### Scenario: DdP available to a despacho
- GIVEN a fresh despacho
- WHEN it lists the CONSTITUCIONAL catalog
- THEN "Derecho de Petición" and "Acción de Tutela" (global) are present

#### Scenario: Both seed under the Constitucional area
- GIVEN the seeded "Derecho de Petición" and "Acción de Tutela"
- WHEN their jurisdicción and áreas are inspected
- THEN both have `jurisdiccion = CONSTITUCIONAL` and are tagged with the `constitucional` áreaPractica

#### Scenario: Seeded DdP carries the term mapa
- GIVEN the seeded "Derecho de Petición"
- WHEN its `radicada` stage is inspected
- THEN it carries `plazoDesdeCampo = "fechaRadicacion"`, `plazoTipoDias = "habiles"`, and
  `plazoDiasPorValorDe` with terms 15/10/30 for General/Documental/Consulta
