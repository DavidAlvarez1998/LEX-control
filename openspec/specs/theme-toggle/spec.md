# Spec: Theme Toggle

## ADDED Requirements

### Requirement: Theme toggle control in each frontend
Each frontend (admin and client) MUST present a visible control in the topbar that switches the
application between a light theme and a dark theme.

#### Scenario: Toggling from light to dark
- **Given** the app is displayed in the light theme
- **When** the user activates the theme toggle in the topbar
- **Then** the entire UI MUST switch to the dark theme
- **And** the toggle MUST reflect the new state (e.g. show the opposite-mode icon)

#### Scenario: Toggling from dark to light
- **Given** the app is displayed in the dark theme
- **When** the user activates the theme toggle
- **Then** the entire UI MUST switch to the light theme

### Requirement: Theme preference persistence
The selected theme MUST persist across reloads and client-side navigation within the same browser.

#### Scenario: Choice survives a reload
- **Given** the user has selected the dark theme
- **When** the user reloads the page or navigates to another route
- **Then** the app MUST remain in the dark theme

### Requirement: First-paint application without flash
The stored (or default) theme MUST be applied before the first paint, so no flash of the wrong
theme occurs, and the initial render MUST NOT produce a hydration mismatch.

#### Scenario: Dark user loads the app
- **Given** the user's stored preference is dark
- **When** the user opens the app fresh
- **Then** the first painted frame MUST already be dark (no light flash)

### Requirement: OS preference as the initial default
When the user has no stored theme preference, the app MUST adopt the operating system's
`prefers-color-scheme` as the initial theme; once the user toggles, their explicit choice takes
precedence.

#### Scenario: First visit on a dark-mode OS
- **Given** the user has never chosen a theme in this app
- **And** the OS reports a dark color-scheme preference
- **When** the user first opens the app
- **Then** the app MUST display the dark theme

#### Scenario: Explicit choice overrides OS preference
- **Given** the OS reports a dark color-scheme preference
- **And** the user has explicitly selected the light theme
- **When** the user reopens the app
- **Then** the app MUST display the light theme

### Requirement: Both themes legible across the UI
Every visible surface — the shell (sidebar, topbar, content area), shared UI primitives, and all
pages including `login` and `activar` — MUST be legible (sufficient text/background contrast) in
both light and dark themes in both apps.

#### Scenario: Dark theme on every page
- **Given** the dark theme is active
- **When** the user visits any dashboard page, the login page, or the activation page
- **Then** text, borders, and surfaces MUST render with dark-appropriate colors (no white-on-white
  or unreadable low-contrast regions)
