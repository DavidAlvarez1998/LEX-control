# ui-transitions

Presentational capability: smooth, professional route transitions across both Next.js portals
(`lex-control-client`, `lex-control-admin`). Scope is restraint-first (subtle, fast,
consistent), native (View Transitions API, no animation dependency), and accessible.

## ADDED Requirements

### Requirement: Route transitions in the dashboard
The dashboard route group SHALL animate navigation between pages with a short cross-fade,
using the browser-native View Transitions API. The transition MUST animate only `opacity`
and/or `transform` (GPU-composited) and MUST complete within ~250ms.

#### Scenario: Navigating between dashboard pages
- **GIVEN** a user on a `(dashboard)` page in either portal
- **WHEN** they navigate to another `(dashboard)` page
- **THEN** the outgoing view cross-fades into the incoming view in ~200ms
- **AND** the transition uses the shared easing `cubic-bezier(0.22, 1, 0.36, 1)`
- **AND** login, activation and landing routes are unaffected

#### Scenario: View Transitions enabled via config
- **GIVEN** each portal's `next.config.ts`
- **THEN** `experimental.viewTransition` MUST be `true`
- **AND** a `src/app/(dashboard)/template.tsx` MUST wrap `children` so the transition
  re-triggers on every navigation (template remounts; layout does not)

### Requirement: Graceful fallback without View Transitions
The app MUST remain fully usable, with a subtle entrance fade, on browsers that do not support
the View Transitions API. The fallback MUST NOT depend on any third-party animation library.

#### Scenario: Browser without View Transitions support
- **GIVEN** a browser where `view-transition-name` is unsupported
- **WHEN** the user navigates within the dashboard
- **THEN** a CSS-keyframe entrance fade (≈`opacity`/`translateY`) plays instead, guarded by
  `@supports not (view-transition-name: none)`
- **AND** no navigation is blocked or visually broken

### Requirement: Consistent motion tokens
Transition duration and easing MUST be defined as shared CSS tokens in each portal's
`globals.css` and reused by the route transition and fallback, so motion is consistent.

#### Scenario: Single source for motion timing
- **GIVEN** `globals.css`
- **THEN** it defines `--lex-transition-dur` (≈200ms) and reuses the easing
  `cubic-bezier(0.22, 1, 0.36, 1)`
- **AND** `::view-transition-old(root)` / `::view-transition-new(root)` and the `@supports`
  fallback both reference that duration/easing

### Requirement: Respect reduced-motion preference
Users who request reduced motion MUST NOT receive route or shared-element transitions.

#### Scenario: prefers-reduced-motion is reduce
- **GIVEN** a user with `prefers-reduced-motion: reduce`
- **WHEN** they navigate within the dashboard
- **THEN** view transitions and the CSS fallback fade are disabled (page swaps instantly)
- **AND** this extends the existing reduced-motion block in `globals.css`

### Requirement: Route transition is the default for new dashboard views
New pages added under the `(dashboard)` route group MUST inherit the route transition
automatically, with no per-page wiring. This is guaranteed by construction because
`template.tsx` wraps the entire route group.

#### Scenario: A new dashboard page is added
- **GIVEN** a developer adds a new page under `src/app/(dashboard)/...`
- **WHEN** a user navigates to or from it
- **THEN** the cross-fade applies with no extra code in the new page
- **AND** the convention is documented in `CLAUDE.md` (Frontends section)

### Requirement: Reusable shared-element helper
Each portal MUST expose a helper `vtName(scope, id)` in `src/lib/view-transition.ts` that
returns a sanitized, unique `view-transition-name` **string**, usable both as the `name` prop
of React's `<ViewTransition>` and as a `view-transition-name` CSS value, so future list→detail
views can opt into the shared-element effect in one line on both the list item and the detail
container.

#### Scenario: Future list→detail view opts in
- **GIVEN** a list row and its detail container for the same entity id
- **WHEN** both use `vtName(scope, id)` with the same `scope` and `id`
  (`<ViewTransition name={vtName(scope, id)}>` or `style={{ viewTransitionName: vtName(...) }}`)
- **THEN** navigating between them morphs the named element
- **AND** distinct ids yield distinct, collision-free names (non-identifier chars sanitized)

### Requirement: Conditional form fields reveal smoothly
In the client dynamic forms, fields that appear because a condition (`mostrarSi`) became true
MUST animate in with a short fade + slight downward motion instead of appearing instantly. The
animation MUST run only when the field mounts (newly revealed), not on every keystroke, and
MUST NOT animate non-conditional base fields on initial form load. It MUST respect
`prefers-reduced-motion`.

#### Scenario: An option reveals dependent fields
- **GIVEN** a client dynamic form (`formulario-dinamico.tsx`, used by both creation and the
  ficha via `datos-proceso.tsx`)
- **WHEN** the user picks an option whose value satisfies another field's `mostrarSi`
- **THEN** each newly visible dependent field fades in with a ~200ms `lex-campo-in` animation
  (slight `translateY`), via the `lex-campo-reveal` class applied only when `campo.mostrarSi`
- **AND** fields already visible do not re-animate (React preserves them by `key`)
- **AND** with `prefers-reduced-motion: reduce`, the field appears instantly

### Requirement: Shared-element transition (showcase)
At least one navigation in the client portal SHALL use a shared-element transition via
`vtName`, to demonstrate the premium effect without a heavyweight animation library. Because
the `procesos` list is a table (rows, not cards), the showcase morphs the title rather than a
whole card.

#### Scenario: Process title morphs from list to detail
- **GIVEN** the client `procesos` list (table rows)
- **WHEN** the user opens a process detail (`procesos/[id]`)
- **THEN** the row title `<div>` and the ficha `PageHeader` `<h2>` share the same
  `view-transition-name` (inline `style={{ viewTransitionName: vtName("proceso-titulo", id) }}`,
  with `PageHeader` gaining an optional `titleStyle` prop applied to its `<h2>`) so the title
  morphs across the navigation
- **AND** if View Transitions is unsupported or reduced-motion is set, it degrades to the
  fallback fade / instant swap with no breakage
