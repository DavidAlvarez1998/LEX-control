# Tramite Catalog Specification — delta (laboral-flujo-doc)

## MODIFIED Requirements

### Requirement: Condition objects support AND/OR composition
A `Condicion` (used by `disponibleSi`, `mostrarSi`, `requeridoSi`, `requeridosSi[].si`,
`opcionalesSi[].si`) MUST support three forms, evaluated by the same `evaluarCondicion`
helper in both the API (`src/modules/procesos/esquema.ts`) and the client
(`lib/procesos.ts`, incl. the inline use in `procesos/[id]/page.tsx`):

- **Leaf** `{ campo: string; igualA: string | string[] }` — equality, array-aware for
  multiselect (passes if any selected value is in `igualA`). Unchanged from today.
- **AND** `{ todas: Condicion[] }` — passes iff every sub-condition passes.
- **OR** `{ alguna: Condicion[] }` — passes iff any sub-condition passes.

Composition MUST nest. Existing single-field conditions (DdP, tutela, current types) MUST keep
working unchanged. No other part of the engine (auto-advance, gating, plazo derivation) changes
its behavior; it only evaluates the richer condition.

#### Scenario: AND condition gates a stage on two fields
- GIVEN an etapa with `disponibleSi = { todas: [{campo:"rol",igualA:"Demandado"}, {campo:"tipoInstancia",igualA:"Única instancia"}] }`
- WHEN `datos = { rol:"Demandado", tipoInstancia:"Única instancia" }`
- THEN the etapa is available
- AND WHEN `datos.tipoInstancia = "Doble instancia"` THEN it is not available

#### Scenario: OR condition keeps the admisión stage for three of four flows
- GIVEN the laboral `admision` etapa with `disponibleSi = { alguna: [{campo:"rol",igualA:"Demandante"}, {campo:"tipoInstancia",igualA:"Doble instancia"}] }`
- THEN it is available for Demandante/Única, Demandante/Doble and Demandado/Doble
- AND it is NOT available for Demandado/Única

#### Scenario: Legacy single-field condition still works
- GIVEN an existing condition `{campo:"contestaron", igualA:["SI","PARCIAL","NO"]}`
- THEN `evaluarCondicion` evaluates it exactly as before this change

### Requirement: Proceso Laboral schema mirrors the source document
The global `TipoProceso` "Proceso Laboral" (grupo LABORAL, Ley 2452/2025) MUST model the
demanda as **attached documents**, not typed fields: `demanda.pdf` (required), `pruebas.pdf`
and `anexos.pdf` (optional), `poder.pdf` when `requierePoder` is true. The fields
`pretensiones` and `hechos` MUST be removed from the schema. The creation intake MUST be
limited to `rol`, `tipoInstancia`, `requierePoder`, the demanda documents, `fechaRadicacion`
(shown only when `rol = Demandante`), and the court `# radicado` + `juzgado`. All other
fields (admisión, contestación, audiencia, sentencia, recurso…) MUST be `soloFicha` and
captured stage by stage in the ficha, in the order of the source document.

#### Scenario: Laboral creation form is short and document-driven
- GIVEN a lawyer creates a "Proceso Laboral"
- WHEN the creation form renders
- THEN it asks rol, tipo de instancia, ¿requiere poder?, the demanda documents (demanda/pruebas/anexos), fecha de radicación (only if Demandante) and # radicado + juzgado — in that order
- AND it does NOT ask `pretensiones` or `hechos`

#### Scenario: Document-decision auto is captured at the admisión stage
- GIVEN a laboral proceso in the `admision` stage
- THEN the stage requires `decisionAuto` (ADMISIÓN | INADMISIÓN | RECHAZO) and the attached `auto-admision.pdf`
- AND choosing INADMISIÓN opens the `subsanacion` branch (5 días hábiles) while RECHAZO opens the `recurso_rechazo` branch
