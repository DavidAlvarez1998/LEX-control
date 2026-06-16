# Tramite Management — delta (proceso UX for DdP & Tutela)

> Change `procesos-ux-ddp-tutela`. Extends `tramite-management` with presentation requirements: list
> search/filter, a visible caso indicator and stage-aware chain, a promoted continuity CTA
> (reiterar/escalar), and stage-flow legibility for the long (tutela) and branched (DdP) paths. The
> stage state machine, gates, branch semantics (`disponibleSi`), derivation idempotency, and chain
> data are UNCHANGED — only their presentation is added, plus two read-only list query params.

## ADDED Requirements

### Requirement: Procesos list supports text search and responsable filter
`GET /procesos` MUST accept two optional read-only query params: `q` (free text matched
case-insensitively against `codigoInterno`, `titulo`, the linked cliente `nombre`, and `radicado`) and
`responsableId` (the abogado). Both MUST compose with the existing `area`/`estado` filters and remain
hard-scoped to the token despacho (`WHERE { empresaId }`). The list UI MUST expose a search box and a
responsable selector. No new permission is introduced (the existing `proceso.ver` gate applies).

#### Scenario: Find a DdP by its entity or title
- GIVEN procesos titled "DdP — EPS Salud Total" and "Tutela — Colpensiones"
- WHEN the user types "salud" in the search box
- THEN only the matching proceso(s) are listed, scoped to their despacho

#### Scenario: Filter by responsible lawyer
- GIVEN procesos assigned to abogados A and B
- WHEN the user selects abogado A in the responsable filter
- THEN only A's procesos show, and the filter composes with área/estado

#### Scenario: Search stays despacho-scoped
- GIVEN despacho X and despacho Y each have a proceso whose título contains "tutela"
- WHEN a user of despacho X searches "tutela"
- THEN only despacho X's proceso is returned

### Requirement: The list indicates a proceso belongs to a multi-node caso
Each list row that is part of a caso with more than one node (i.e. it has a `casoRelacionadoId` or has
derivados) MUST show a small "caso" indicator linking to the base proceso, so a reiteración or an
escalated tutela is never read as an unrelated matter. The list stays flat and sortable (no tree
collapse); the full chain is shown in the ficha.

#### Scenario: A reiteración is marked as part of its caso
- GIVEN a DdP and its reiteración (linked by `casoRelacionadoId`)
- WHEN the list renders the reiteración row
- THEN it shows a "caso" marker linking to the base DdP

#### Scenario: A standalone proceso shows no caso marker
- GIVEN a DdP with no base and no derivados
- WHEN the list renders its row
- THEN no caso marker is shown

### Requirement: Caso chain shows each node's current stage
The `CasoChain` (rendered when the caso has more than one node) MUST show, for each node, its current
stage name in addition to its estado and `fechaLimite`, and MUST remain legible on narrow viewports
(horizontal scroll without clipping). The active node stays visually highlighted.

#### Scenario: Chain reads DdP → reiteración → tutela with stages
- GIVEN a caso DdP(terminada) → reiteración(radicada) → tutela(admisión)
- WHEN the ficha of any node renders the chain
- THEN each node shows its tipo, código, current stage, estado, and `fechaLimite`, with the open
  node highlighted

### Requirement: The continuity decision (reiterar / escalar) is a contextual CTA
When the active stage defines a `crearDerivado` action, the ficha MUST present it as a prominent,
clearly-labeled call-to-action (not a footnote of the stage list), with copy that distinguishes a
**continuation of the same type** (DdP → reiteración: "Crear la reiteración") from an **escalation to
another type** (DdP → tutela: "Crear {tipo}"), and that states the base proceso becomes the caso base.
The CTA MUST respect the existing idempotency: once a derivado of that type exists, it links to it
instead of creating a duplicate.

#### Scenario: Partial answer offers reiterar as a CTA
- GIVEN a DdP in the `reiteracion` stage (contestaron = PARCIAL)
- WHEN the ficha renders
- THEN a clear CTA offers "Crear la reiteración" describing it as a continuation linked as the same caso

#### Scenario: Silence offers escalar a tutela
- GIVEN a DdP in the `escala_tutela` stage (contestaron = NO)
- WHEN the ficha renders
- THEN a clear CTA offers "Crear Acción de tutela" described as an escalation of the same caso

#### Scenario: Existing derivado is linked, not duplicated
- GIVEN the reiteración already exists for a DdP
- WHEN the lawyer returns to the base DdP
- THEN the CTA shows "abrir expediente →" to the existing reiteración and does not offer to create another

### Requirement: Stage flow is legible for long and branched paths
The stage stepper MUST show each stage's plazo when defined (`reglas.plazoDias` + `plazoTipoDias`), and
MUST visually emphasize very short terms (e.g. the tutela impugnación = 3 días) so they are not missed.
For branch stages that share an order and are mutually exclusive by `disponibleSi` (DdP
respondida / reiteración / escala_tutela, keyed on `contestaron`), the UI MUST present only the
applicable branch(es) as takeable and MUST make clear that they are alternatives driven by the
response outcome — unavailable branches stay visible but dimmed/non-clickable (already the behavior),
with one line of guidance.

#### Scenario: Tutela's 3-day impugnación term is emphasized
- GIVEN a tutela in `falloPrimeraInstancia` with the next stage `impugnacion` (3 días)
- WHEN the stepper renders
- THEN the impugnación term is shown and visually emphasized as a tight deadline

#### Scenario: DdP branches reflect the response
- GIVEN a DdP where `contestaron = PARCIAL`
- WHEN the stepper renders the order-2 branches
- THEN `reiteración` is takeable while `respondida` and `escala_tutela` are dimmed/non-clickable, with
  guidance that the path follows the response outcome
