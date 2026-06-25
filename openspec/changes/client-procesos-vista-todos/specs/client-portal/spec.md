# Client Portal Specification — delta (client-procesos-vista-todos)

## ADDED Requirements

### Requirement: Procesos landing offers three sibling views
The client portal `/procesos` landing MUST present a single toggle with three views —
**Jurisdicción**, **Todos**, **Míos** — controlled by the `vista` query param
(`jurisdiccion` | `todos` | `mios`). `jurisdiccion` MUST be the default (an absent or unknown
`vista` resolves to `jurisdiccion`) and MUST render the existing catalog tree grouped by
jurisdicción unchanged. The previous `seccion` view (catalog grouped by `grupo`) MUST be removed.

#### Scenario: Default view is jurisdicción
- GIVEN a user opens `/procesos` with no `vista` param
- WHEN the page renders
- THEN the catalog tree grouped by jurisdicción is shown and the "Jurisdicción" toggle is active

#### Scenario: Sección view is gone
- GIVEN a user navigates to `/procesos?vista=seccion`
- WHEN the page renders
- THEN it falls back to the default jurisdicción view (no "Sección" option is offered)

### Requirement: "Todos" view lists all processes deadline-first
The `vista=todos` view MUST render a flat, paginated list of all the tenant's processes ordered:
overdue (`vencido`) first, then due-soon (`por_vencer`), then on-time with a deadline (`al_dia`
ascending by `fechaLimite`), then processes without a deadline, then closed/archived processes
(visually de-emphasized) last. Each row MUST link to the process detail and MUST show the deadline
with its semáforo color and the estado badge. The existing área/estado/búsqueda filters and the
vencimientos banner MUST remain available. Ordering MUST be preserved across pages (i.e. ordering is
applied server-side, not only within the current page).

#### Scenario: Overdue processes appear first
- GIVEN the tenant has an overdue process and an on-time process
- WHEN the user opens `/procesos?vista=todos`
- THEN the overdue process is listed above the on-time process

#### Scenario: Closed processes sink to the bottom
- GIVEN an open process with a deadline and a CERRADO process
- WHEN the list renders
- THEN the CERRADO process appears after all open processes, visually de-emphasized

#### Scenario: Order holds across pagination
- GIVEN more processes than one page
- WHEN the user advances to a later page
- THEN the global deadline-first order continues (no per-page re-sorting)

### Requirement: "Míos" view and `/mis-procesos` redirect
The `vista=mios` view MUST show the same deadline-first flat list filtered to processes whose
responsable is the current user. The standalone route `/mis-procesos` MUST redirect to
`/procesos?vista=mios` so a single implementation backs both entry points.

#### Scenario: Míos filters to the current user
- GIVEN the user is the responsable of some processes and not of others
- WHEN they open `/procesos?vista=mios`
- THEN only the processes they are responsible for are listed, deadline-first

#### Scenario: Legacy route redirects
- GIVEN a user navigates to `/mis-procesos`
- WHEN the request resolves
- THEN they are redirected to `/procesos?vista=mios`
