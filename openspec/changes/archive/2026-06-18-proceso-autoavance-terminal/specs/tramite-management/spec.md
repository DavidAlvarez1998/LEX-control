# Tramite Management Specification — delta (proceso-autoavance-terminal)

## ADDED Requirements

### Requirement: Auto-advance jumps to a decided terminal
On saving a proceso's `datos`, in addition to the conservative step-by-step auto-advance, the
engine MUST advance directly to a **terminal** stage when ALL of: the terminal carries a
`disponibleSi` that is satisfied by the current `datos`; the terminal's `orden` is greater than
the current stage's; it is the **only** terminal whose `disponibleSi` is satisfied; and the
terminal's own required fields/documents (if any) are present. The intermediate stages' pending
requirements MUST NOT block this jump (a withdrawal/rejection/settlement ends the process
regardless of unfinished paperwork). This MUST run only as a fallback to the conservative
advance (which is unchanged), and MUST NOT apply to terminals without `disponibleSi` (e.g. a
natural `terminada`, which still requires walking the flow).

#### Scenario: Withdrawal archives immediately from any earlier stage
- GIVEN a "Proceso Laboral" at `presentacion` with no admisión paperwork uploaded
- WHEN `datos` are saved with `hayRetiro = "SI"`
- THEN the proceso jumps to the terminal `archivado` and `estado` becomes `CERRADO`

#### Scenario: No decided terminal does not close the process
- GIVEN a proceso whose saved `datos` satisfy no terminal's `disponibleSi`
- WHEN `datos` are saved
- THEN the proceso does not jump to any terminal (it only advances conservatively)

#### Scenario: Two satisfied terminals do not auto-jump
- GIVEN `datos` that satisfy the `disponibleSi` of two different terminal stages
- WHEN `datos` are saved
- THEN no terminal jump occurs (the choice is left to the user)

### Requirement: Advancing a stage first persists unsaved form edits
In the proceso ficha, when the user triggers a stage transition while the form holds unsaved
edits, the UI MUST first persist those edits (tolerant save — incomplete drafts allowed) so the
transition is evaluated against the latest diligenced data. If that save auto-advanced the
proceso to the requested stage (or closed it), the UI MUST NOT issue a redundant move; otherwise
it proceeds with the transition, surfacing the existing block-and-guide behavior when data is
still missing.

#### Scenario: Clicking advance saves typed-but-unsaved data first
- GIVEN the form has unsaved edits that complete the requirements of the next stage
- WHEN the user clicks that stage in the stepper
- THEN the edits are saved first and the proceso advances (no "missing data" block)

#### Scenario: Still-missing data after the save guides the user back to the form
- GIVEN the unsaved edits do NOT complete the next stage's requirements
- WHEN the user clicks that stage
- THEN after saving, the transition is blocked and the form opens highlighting what is missing
