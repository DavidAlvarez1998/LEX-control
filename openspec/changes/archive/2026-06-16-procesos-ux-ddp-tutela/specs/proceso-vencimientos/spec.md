# Proceso Vencimientos — delta (deadline-first surfacing)

> Change `procesos-ux-ddp-tutela`. Extends the existing `proceso-vencimientos` capability with
> presentation requirements that surface the already-derived `fechaLimite`/`semaforo` where the work
> happens (procesos list, home dashboard, ficha) and add a UI-derived "vence hoy" state. It does NOT
> change the vencimiento derivation, the business-day math, or the API buckets.

## ADDED Requirements

### Requirement: Procesos list shows the vencimiento with a semáforo column
The procesos list MUST render a `Vence` column for every row, showing the proceso's `fechaLimite`
(or "—" when none) with a color that reflects its urgency: red for `vencido` (fechaLimite before
today) and for **vence hoy** (fechaLimite === today), amber for `por_vencer` (within 3 business days),
and neutral for `al_día`. The list MUST default-sort open procesos so the most urgent (soonest/overdue
`fechaLimite`) appear first; procesos without `fechaLimite` and closed/archived procesos sort after
the dated open ones. The semáforo classification MUST reuse the existing derivation; "vence hoy" is a
UI refinement derived from `fechaLimite === today`, not a new API bucket.

#### Scenario: Overdue proceso floats to the top in red
- GIVEN an open DdP whose `fechaLimite` is yesterday and another whose `fechaLimite` is in 10 days
- WHEN the user opens the procesos list
- THEN the overdue DdP appears above the other, its `Vence` cell shows the date in red

#### Scenario: Vence hoy is distinguished from por vencer
- GIVEN a tutela whose `fechaLimite` is today (impugnación, 3-day term elapsing)
- WHEN the list renders
- THEN its `Vence` cell is red and labeled as venciendo hoy, distinct from amber por-vencer rows

#### Scenario: Procesos without a deadline do not crowd the urgent ones
- GIVEN a proceso in `borrador` with no `fechaLimite`
- WHEN the list is sorted by urgency
- THEN it shows "—" in `Vence` and is ordered after the dated open procesos

### Requirement: Home dashboard surfaces proceso deadlines
The tenant home MUST show a "Vencimientos de procesos" summary that reads the existing
`GET /procesos/vencimientos` and presents the count of `vencido` and `por_vencer` procesos plus a
short list (a few nearest), each linking to its ficha, with red/amber emphasis. It MUST appear
alongside the existing comercial alerts (it does not replace them). When there are no overdue or
soon-due procesos, the section MUST collapse (no empty card noise).

#### Scenario: Lawyer sees due procesos on login
- GIVEN the despacho has 2 overdue and 1 soon-due proceso
- WHEN a user opens the home
- THEN a "Vencimientos de procesos" card shows "2 vencidos · 1 por vencer" and links to those fichas

#### Scenario: Quiet when nothing is due
- GIVEN no proceso is overdue or due within 3 business days
- WHEN the home renders
- THEN the proceso-vencimientos card is not shown

### Requirement: Ficha shows the active stage countdown
On a proceso ficha, the current stage MUST display its remaining term derived from the already-stored
`fechaLimite` (e.g. "Vence en 2 días hábiles · 26 jun", or "Vencido hace 1 día" in red), so the lawyer
sees the live deadline next to the stage they are working, not only as a data field.

#### Scenario: DdP shows the 15-day term counting down
- GIVEN a DdP in `radicada` with `fechaLimite` 2 business days away
- WHEN the ficha renders
- THEN the active stage shows "Vence en 2 días hábiles · <fecha>" in amber

#### Scenario: Overdue is unmistakable
- GIVEN a proceso whose `fechaLimite` is past
- WHEN the ficha renders
- THEN the active stage shows the overdue state in red
