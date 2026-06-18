# Tramite Management Specification — delta (form-indentacion-condicional)

## ADDED Requirements

### Requirement: Conditional fields are indented by dependency depth
The dynamic form renderer (`FormularioDinamico`) MUST indent each visible field by the depth
of its `mostrarSi` dependency chain: a field without `mostrarSi` is level 0 (no indent); a
field whose `mostrarSi` references a field at level N renders at level N+1, with a left visual
guide. This is presentation-only — it MUST NOT change validation, requiredness or stage gating —
and applies to every dynamic form (all grupos and any future catálogo), derived from the
existing conditions without seed changes.

#### Scenario: A revealed sub-option appears indented under the option that triggered it
- GIVEN a field "Decisión del juez sobre la reconvención" and a field
  "Decisión tras la subsanación (reconvención)" whose `mostrarSi` references it
- WHEN the first is set so the second appears
- THEN the second renders indented one level under the first
- AND a field that depends on that second one appears indented one more level
