# ui-tooltip

Shared presentational capability: a reusable `Tooltip` primitive in both portals' `ui.tsx`,
the project standard for explaining controls on hover/focus (preferred over the native `title`).

## ADDED Requirements

### Requirement: Reusable Tooltip primitive
Both portals (`lex-control-client`, `lex-control-admin`) MUST export an identical `Tooltip`
component from `src/components/ui.tsx`. It MUST wrap arbitrary `children`, accept `content`
(ReactNode), an optional `side` (`top` default | `bottom` | `left` | `right`) and an optional
`className`. The tooltip MUST NOT intercept pointer events on the trigger and MUST be theme-aware
(legible en claro y oscuro).

#### Scenario: Showing the tooltip on hover
- **GIVEN** a `Tooltip` wrapping a button with `content="Explicación"`
- **WHEN** the user hovers the button
- **THEN** the styled bubble with "Explicación" becomes visible near the button (on the `side` requested)
- **AND** clicking the button still works (the tooltip does not block the click)

#### Scenario: Keyboard accessibility
- **GIVEN** a `Tooltip` wrapping a focusable control
- **WHEN** the control receives keyboard focus
- **THEN** the tooltip becomes visible
- **AND** the bubble has `role="tooltip"`

#### Scenario: Not clipped by the sidebar/topbar (portal)
- **GIVEN** a `Tooltip` inside a page whose ancestors create a stacking/overflow context (the dashboard content area)
- **WHEN** it shows
- **THEN** the bubble MUST render in a portal to `document.body` with `position: fixed` and a z-index above the sidebar/topbar, so it is NOT hidden behind them
- **AND** its position is computed from the trigger's bounding rect for the requested `side`

#### Scenario: Appears after a short delay
- **GIVEN** the user hovers the trigger
- **WHEN** less than ~450ms have passed
- **THEN** the tooltip is NOT yet visible
- **AND** if the pointer leaves before the delay elapses, it never shows (the pending timer is cleared)

#### Scenario: Identical in both portals
- **GIVEN** the `Tooltip` in `lex-control-client` and in `lex-control-admin`
- **THEN** their props, markup and styling MUST match (same standard, no per-portal drift)

### Requirement: Prefer Tooltip over the native title attribute
New UI that needs an on-hover/on-focus explanation SHALL use `<Tooltip>` instead of the HTML
`title` attribute. `title` MAY remain only for trivial cases or non-React surfaces.

#### Scenario: Clientes "Míos" / "Todos" toggle
- **GIVEN** the Clientes view in the client portal
- **WHEN** the user hovers "Míos" or "Todos"
- **THEN** a `Tooltip` explains each view (Míos = clientes que llevas tú; Todos = toda la cartera del despacho)
- **AND** the buttons no longer rely on the native `title` attribute
