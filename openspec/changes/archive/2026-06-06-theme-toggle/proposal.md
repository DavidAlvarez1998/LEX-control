# Proposal: Dark/Light Theme Toggle (Admin + Client)

## Intent
Both frontends (`lex-control-admin`, `lex-control-client`) render a single hardcoded light theme
built on Tailwind v4 utility classes (`slate-*`, `white`, `indigo`). Users want to switch between
a light ("white") and a dark theme with a visible toggle button. This change adds a class-based
dark mode to Tailwind, a persisted, no-flash theme selector, a toggle button in each app's topbar,
and `dark:` styling across the shared shell, UI primitives, and pages so both modes look correct.

## Scope

### In Scope
- Enable Tailwind v4 class-based dark mode in both apps via a `dark` custom variant toggled by a
  `.dark` class on `<html>`.
- A `ThemeToggle` button placed in the topbar of both apps (sun/moon icon), switching light ↔ dark.
- Persistence in `localStorage` and first-paint application (inline script in `layout.tsx`) so
  there is no flash of the wrong theme (FOUC) and no hydration mismatch.
- Initial theme resolution: stored preference if present, else the OS `prefers-color-scheme`.
- `dark:` variants applied to the shared shell (sidebar, topbar, dashboard layout), the UI
  primitives (`ui.tsx`: `PageHeader`, `Button`, `Card`, `StatCard`, `EmptyState`), and each
  app's pages (dashboard pages, `login`, `activar`) so all visible surfaces respond to the theme.

### Out of Scope
- Per-user theme preference persisted server-side / in the DB (`localStorage` only for now).
- A third "system/auto" tri-state in the UI (we follow the OS only as the *initial default*; the
  button itself toggles between explicit light and dark).
- Restyling or redesigning components beyond what dark mode requires.
- Theming the `@lex/db` layer (irrelevant — no UI).

## Capabilities

### New Capabilities
- `theme-toggle`: a client-selectable light/dark theme, persisted and applied without flash, with
  a toggle control in each frontend's topbar.

### Modified Capabilities
- None. Purely additive UI behavior; no API or data-model change.

## Approach
Add `@custom-variant dark (&:where(.dark, .dark *));` to each app's `globals.css` and set base
`color-scheme`/background/foreground for both modes. A tiny inline script in `layout.tsx` (runs
before paint) reads `localStorage["lex-theme"]` (or `prefers-color-scheme`) and adds `.dark` to
`<html>` — preventing FOUC; `<html>` gets `suppressHydrationWarning`. A `lib/theme.ts` helper
centralizes read/apply/toggle, and a `"use client"` `ThemeToggle` component (rendered in the
topbar) flips the class and persists the choice. Styling work is mechanical: add `dark:` variants
to the limited, consistent `slate`-based palette, starting with the shared shell + primitives
(which most pages compose) and then the page-level wrappers.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `*/src/app/globals.css` | Modified | `@custom-variant dark`; base light/dark colors + `color-scheme` |
| `*/src/app/layout.tsx` | Modified | Inline no-FOUC theme script; `suppressHydrationWarning`; dark body base |
| `*/src/lib/theme.ts` | New | Theme read/apply/toggle helpers + storage key |
| `*/src/components/theme-toggle.tsx` | New | `"use client"` toggle button (sun/moon) |
| `*/src/components/topbar.tsx` | Modified | Render `ThemeToggle`; dark variants |
| `*/src/components/sidebar.tsx` | Modified | Dark variants |
| `*/src/components/ui.tsx` | Modified | Dark variants on all primitives |
| `*/src/app/(dashboard)/layout.tsx` | Modified | Dark background |
| `*/src/app/(dashboard)/**/page.tsx`, `login`, `activar` | Modified | Dark variants on page wrappers |

`*` = applied symmetrically in both `lex-control-admin/` and `lex-control-client/`.

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Flash of wrong theme on load (FOUC) | Med | Apply `.dark` from an inline script in `<head>` before first paint |
| Hydration mismatch warning on `<html>` | Med | `suppressHydrationWarning` on `<html>`; class set by pre-hydration script |
| Missed surfaces look broken in dark | Med | Theme shared primitives + shell first (cover most UI), then sweep pages |
| Drift between the two apps | Low | Keep `lib/theme.ts` and `ThemeToggle` identical in both projects |

## Rollback Plan
Purely additive and client-only. Revert by removing `theme-toggle.tsx`, `lib/theme.ts`, the topbar
button, the inline script + `suppressHydrationWarning` in `layout.tsx`, and the `@custom-variant`
line. The `dark:` utility classes are inert without a `.dark` ancestor, so leftover variants are
harmless even if reverted partially. No DB or API change to undo.

## Dependencies
- Tailwind CSS v4 (already in both apps via `@tailwindcss/postcss`).
- No new npm packages (no `next-themes`; a ~10-line helper keeps the footprint minimal).

## Success Criteria
- [ ] A toggle button in each app's topbar switches the whole UI between light and dark.
- [ ] The choice persists across reloads and navigation (localStorage).
- [ ] No flash of the wrong theme on initial load; no hydration warning.
- [ ] With no stored choice, the app honors the OS `prefers-color-scheme` on first visit.
- [ ] Shell, primitives, and all pages are legible in both modes in both apps.
- [ ] `pnpm build` succeeds for both frontends.
