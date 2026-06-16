# Proposal: Procesos UX — deadline-first for Derecho de Petición & Tutela

## Intent
The proceso (trámite) module is functionally complete, but its UI/UX does not match how a Colombian
lawyer actually works a **Derecho de Petición** or **Acción de Tutela**: both are **deadline-driven**
(DdP 15/10/30 hábiles; tutela 10 to file the fallo, **3 to impugnar**, 20 for second instance), both
move through **stages with branches**, and both can chain into one another (DdP → reiteración → tutela)
as a single *caso*. Today that critical information is buried: the due date lives in a banner only on
`/procesos`, the case chain only shows inside a ficha when there is more than one node, the
reiterar/escalar decision is hidden under the "Etapas" card, and the list has no search.

This change is a **presentation/UX layer** improvement. It surfaces deadlines where the work happens,
makes the stage flow legible for the long/branched DdP and tutela paths, and turns the case chain and
the continuity decision (reiterar / escalar a tutela) into first-class, contextual UI. It is generic:
it operates on any `TipoProceso`, with DdP/tutela as the driving cases — judicial types benefit too.

## Why this is coherent with the design (SDD validation)
This change **does not alter any domain rule**. Every requirement it adds is a *presentation* of data
the backend already computes:
- `proceso-vencimientos` already derives `fechaLimite` and a `semaforo` bucket
  (`vencido` / `por_vencer` ≤3 hábiles / `al_dia`) via `GET /procesos/vencimientos`. This change
  consumes that on the home dashboard and as a list column — no new derivation, no schema.
- `tramite-management` already defines rule-gated stages with `disponibleSi` branches, the
  `crearDerivado` action (reiteración/escala), and the `casoRelacionadoId` chain
  (`GET /procesos/:id/caso`). This change makes those legible, not different.
- The two backend additions are **read-only filters** on the existing list endpoint (`q`,
  `responsableId`) — no new entity, no write path, no RBAC change (same `proceso.ver`).

Decisive for SDD: the stage state machine, the gates, the vencimiento math, the derivation
idempotency and the chain semantics are **untouched**. We only change what the user sees and how fast
they can act on it.

## Scope (five themes)

### A. Deadline-first surfacing
DdP/tutela live or die by the term. Today the due date is a banner on `/procesos` only.
- **List**: a `Vence` column with the semáforo (vencido / **vence hoy** / ≤3 hábiles / al día), and a
  default sort that floats the most urgent open procesos to the top.
- **Home**: a "Vencimientos de procesos" card (counts + the nearest few), next to the existing
  comercial alerts — today the home shows comercial alerts but **no proceso deadlines**.
- **Ficha**: the current stage shows its countdown (e.g. *"Vence en 2 días hábiles · 26 jun"*),
  reusing the already-derived `fechaLimite`.

### B. Find anything fast
- **Text search** over código / título / cliente / radicado on the list.
- **Filter by responsable** (abogado), alongside the existing área/estado filters.

### C. The caso is the unit (DdP → reiteración → tutela)
- The `CasoChain` shows the **current stage** inside each node (not only the global estado) and reads
  cleanly on mobile.
- The list **indicates** when a proceso is part of a multi-node caso (a small "caso" marker linking to
  the base), so a reiteración/tutela is never mistaken for an unrelated matter.

### D. The continuity decision is visible (reiterar / escalar a tutela)
For a DdP, the moment the entity answers (partial → **reiterar**; silence → **escalar a tutela**) is
*the* decision. Today the `crearDerivado` action is a small box at the bottom of the "Etapas" card.
This change promotes it to a clear, contextual **call-to-action** with copy that names what it does
(continuation vs escalation, already differentiated), shown when the active stage offers it.

### E. Stage clarity for long & branched flows
- Every stage shows its **plazo** (already in `reglas.plazoDias`) and the tutela's tight terms
  (impugnación = 3 días) are visually emphasized so they are not missed.
- For the DdP, the branch stages (respondida / reiteración / escala_tutela) are presented as the
  *mutually exclusive options* they are, driven by `contestaron`, with one line of guidance — instead
  of three rows that look equally takeable.

## Decisions
- **Presentation-only, generic.** No domain/stage/vencimiento rule changes; the work is in
  `lex-control-client` plus two read-only query params on the list endpoint. DdP/tutela drive the
  design but every type benefits.
- **Reuse the existing semáforo.** "Vence hoy" is derived in the UI from `fechaLimite === today`; the
  API buckets (`vencido`/`por_vencer`/`al_dia`) are not changed.
- **No new pages.** Deadlines are surfaced *in place* (list column + home card + ficha), not as a
  separate `/vencimientos` route — the lawyer already lives in the list and the home.
- **Case marker, not regrouping.** The list stays flat (sortable by urgency); a caso is *indicated*
  per row and fully shown in the ficha's `CasoChain`. We do not collapse rows into trees (keeps sort
  and pagination simple).
- **Forms rule still applies.** Any new required input marks its label with `*` and validates on
  submit before calling the API (per repo `apply` rule).

## Out of scope
- Any change to the stage state machine, gates, branch semantics, derivation idempotency, or the
  vencimiento math.
- A standalone `/vencimientos` dashboard route (the home card + list column cover the need; revisit if
  asked).
- Tree/collapse grouping of the list by caso, server-side full-text search infra, and saved views.
- Tutela-specific *new* fields or stages (medida provisional, cumplimiento/desacato as a distinct
  stage) — those are domain changes, not UX, and belong to a separate proposal.
- Admin portal (this is the tenant/client portal experience).

## Rollback
Fully additive and presentation-level. Reverting = drop the `q`/`responsableId` params from the list
endpoint and revert the client components (list column/search, home card, ficha countdown, CasoChain
stage label, derivation CTA). No schema, no data migration, no RBAC change; existing procesos and
their vencimientos are unaffected.
