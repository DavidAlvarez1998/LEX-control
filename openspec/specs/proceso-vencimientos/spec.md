# Proceso Vencimientos Specification

## Purpose
Derive and track **legal deadlines** on a `Proceso` from its stage rules, computed in **Colombian
business days** (días hábiles) honoring national holidays, and expose a deadline-status query so a
despacho can see what is al día / por vencer / vencido. This makes deadlines like the *derecho de
petición* term ("automático dependiendo del tipo") a first-class, queryable property instead of a
manual text field.

## Requirements

### Requirement: Colombian business-day calculation
The system MUST compute Colombian national holidays (festivos) for any given year algorithmically:
fixed-date festivos; Emiliani festivos shifted to the following Monday (Ley 51/1983); and
Easter-relative festivos (Jueves/Viernes Santo on their day; Ascensión, Corpus Christi, Sagrado Corazón
shifted to Monday). A día hábil MUST exclude Saturdays, Sundays, and festivos. The calculation MUST be
pure (a function of the year only) and unit-tested against an explicit expected festivo set for at least
2024–2027.

#### Scenario: Emiliani holiday lands on Monday
- GIVEN Reyes Magos (Jan 6) falls on a non-Monday in some year
- WHEN festivos for that year are computed
- THEN the holiday is recorded on the following Monday, not on Jan 6

#### Scenario: Business day excludes weekend and festivo
- GIVEN a date that is a Saturday, and a date that is a festivo
- WHEN `esDiaHabil` is evaluated for each
- THEN both return false

#### Scenario: Add business days skips holidays
- GIVEN a start date and a span that crosses a weekend and one festivo
- WHEN `sumarDiasHabiles(start, n)` is computed
- THEN the result advances `n` business days, skipping the weekend and the festivo

### Requirement: Stage deadline rule derives `fechaLimite`
A `TipoProceso` etapa rule MAY carry `plazoDesdeCampo` (a `fecha` field key), `plazoTipoDias`
('habiles'|'calendario'), and `plazoDiasPorValorDe: { campo, mapa }`, EXTENDING the existing
informational `plazoDias`. A `fechaLimite` MUST be derived **only when `plazoDesdeCampo` is present**;
the term is `plazoDiasPorValorDe.mapa[datos[campo]]` if set, otherwise `plazoDias`. When a `Proceso`
enters such an etapa, the system MUST compute `fechaLimite = datos[plazoDesdeCampo] + term`, using
business-day or calendar-day arithmetic per `plazoTipoDias`. A rule with only `plazoDias` (no
`plazoDesdeCampo`) MUST NOT derive a deadline (unchanged informational behavior). If the source field
(`datos[plazoDesdeCampo]`) is empty, `fechaLimite` MUST be left null without error. The
`Proceso.fechaLimite` column MUST be additive and nullable.

#### Scenario: Derecho de petición documental term
- GIVEN a DdP proceso with `tipoPeticion = "Documental"` and `fechaRadicacion = 2026-02-02`
- WHEN it enters the `radicada` stage (plazo: business days, diasPorValorDe General/Documental/Consulta = 15/10/30)
- THEN `fechaLimite` is set to 2026-02-02 plus 10 business days, holidays honored

#### Scenario: Missing source date yields no deadline
- GIVEN a proceso entering a plazo stage with `fechaRadicacion` empty
- WHEN the stage transition is applied
- THEN `fechaLimite` remains null and the transition succeeds

#### Scenario: Manual override is not silently clobbered
- GIVEN a proceso whose `fechaLimite` was manually edited
- WHEN it re-enters the same plazo stage
- THEN the system MUST NOT overwrite the manual value without the recompute being explicitly requested

### Requirement: Deadline-status query
The system MUST expose a despacho-scoped query returning open procesos bucketed by `fechaLimite`
relative to today: `vencido` (before today), `por_vencer` (within 3 business days), `al_dia`
(otherwise, including null). The query MUST be scoped by `empresaId` from the JWT and MUST NOT return
another despacho's procesos.

#### Scenario: Buckets reflect the deadline
- GIVEN procesos with fechaLimite in the past, within 2 business days, and far in the future
- WHEN the deadline-status query runs for that despacho
- THEN they are returned under `vencido`, `por_vencer`, and `al_dia` respectively

#### Scenario: Tenant isolation
- GIVEN an open proceso owned by despacho B with an imminent deadline
- WHEN a user of despacho A runs the deadline-status query
- THEN despacho B's proceso is NOT returned

### Requirement: Procesos list shows the vencimiento with a semáforo column
> ADDED by change `procesos-ux-ddp-tutela`.

The procesos list MUST render a `Vence` column for every row, showing the proceso's `fechaLimite` (or "—" when none) with a color that reflects its urgency: red for `vencido` (fechaLimite before today) and for **vence hoy** (fechaLimite === today), amber for `por_vencer` (within 3 business days), and neutral for `al_día`. The list MUST default-sort open procesos so the most urgent (soonest/overdue `fechaLimite`) appear first; procesos without `fechaLimite` and closed/archived procesos sort after the dated open ones. The semáforo classification MUST reuse the existing derivation; "vence hoy" is a UI refinement derived from `fechaLimite === today`, not a new API bucket.

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
> ADDED by change `procesos-ux-ddp-tutela`.

The tenant home MUST show a "Vencimientos de procesos" summary that reads the existing `GET /procesos/vencimientos` and presents the count of `vencido` and `por_vencer` procesos plus a short list (a few nearest), each linking to its ficha, with red/amber emphasis. It MUST appear alongside the existing comercial alerts (it does not replace them). When there are no overdue or soon-due procesos, the section MUST collapse (no empty card noise).

#### Scenario: Lawyer sees due procesos on login
- GIVEN the despacho has 2 overdue and 1 soon-due proceso
- WHEN a user opens the home
- THEN a "Vencimientos de procesos" card shows "2 vencidos · 1 por vencer" and links to those fichas

#### Scenario: Quiet when nothing is due
- GIVEN no proceso is overdue or due within 3 business days
- WHEN the home renders
- THEN the proceso-vencimientos card is not shown

### Requirement: Ficha shows the active stage countdown
> ADDED by change `procesos-ux-ddp-tutela`.

On a proceso ficha, the current stage MUST display its remaining term derived from the already-stored `fechaLimite` (e.g. "Vence en 2 días hábiles · 26 jun", or "Vencido hace 1 día" in red), so the lawyer sees the live deadline next to the stage they are working, not only as a data field.

#### Scenario: DdP shows the 15-day term counting down
- GIVEN a DdP in `radicada` with `fechaLimite` 2 business days away
- WHEN the ficha renders
- THEN the active stage shows "Vence en 2 días hábiles · <fecha>" in amber

#### Scenario: Overdue is unmistakable
- GIVEN a proceso whose `fechaLimite` is past
- WHEN the ficha renders
- THEN the active stage shows the overdue state in red
