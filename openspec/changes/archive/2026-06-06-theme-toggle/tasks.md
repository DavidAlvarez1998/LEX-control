# Tasks: Dark/Light Theme Toggle

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 350–500 (mostly mechanical `dark:` variants across 2 apps) |
| 400-line budget risk | Med |
| Delivery strategy | per-app batches; infra first, then styling sweep |

### Suggested Work Units

| Unit | Goal | Notes |
|------|------|-------|
| 1 | Theme infra (both apps): Tailwind dark variant, `lib/theme.ts`, inline no-FOUC script, `ThemeToggle`, topbar wiring | Functional toggle even before full styling |
| 2 | Styling sweep: dark variants on shell + `ui.tsx` primitives | Covers most of the UI |
| 3 | Styling sweep: page-level wrappers (`login`, `activar`, dashboard pages) | Residual literal classes |

## Phase 1: Theme infrastructure (per app — admin + client)

- [x] 1.1 `globals.css`: add `@custom-variant dark (&:where(.dark, .dark *));`; set base body
      background/foreground and `color-scheme` for light and `.dark`.
- [x] 1.2 `lib/theme.ts`: `Theme` type, `THEME_KEY`, `getStoredTheme`, `systemTheme`,
      `resolveTheme`, `applyTheme`, `setTheme` (per design.md).
- [x] 1.3 `layout.tsx`: add `suppressHydrationWarning` to `<html>`; inject the inline no-FOUC
      `<script>` in `<head>`; add dark base classes to `<body>`.
- [x] 1.4 `components/theme-toggle.tsx`: `"use client"` button; reads state on mount; sun icon in
      dark / moon icon in light; `onClick` calls `setTheme(...)`.
- [x] 1.5 `components/topbar.tsx`: render `<ThemeToggle />` in the right-hand controls group.

## Phase 2: Styling sweep — shell + primitives (per app)

- [x] 2.1 `components/ui.tsx`: dark variants for `PageHeader`, `Button` (all variants), `Card`,
      `StatCard`, `EmptyState`, icon wrappers.
- [x] 2.2 `components/sidebar.tsx`: left permanently dark by design (already `bg-slate-900`); reads
      correctly against the `slate-950` shell in both modes — no variants needed.
- [x] 2.3 `components/topbar.tsx`: dark variants (header bg/border, title, search input, icon button).
- [x] 2.4 `(dashboard)/layout.tsx`: dark background for the app shell + main content area.

## Phase 3: Styling sweep — pages (per app)

- [x] 3.1 `login/page.tsx` and `activar/page.tsx`: dark variants on card/inputs/text.
- [x] 3.2 Admin dashboard pages: `page.tsx`, `empresas`, `servicios`, `usuarios`, `facturacion`,
      `api` — dark variants on section wrappers, tables, forms, badges.
- [x] 3.3 Client dashboard pages: `page.tsx`, `cuenta`, `servicios`, `facturacion`, `soporte` —
      dark variants on section wrappers, tables, forms, badges.

## Phase 4: Verify

- [x] 4.1 `pnpm --dir lex-control-admin build` and `pnpm --dir lex-control-client build` compile clean.
- [ ] 4.2 Manual: in each app, toggle light↔dark; reload (persists); fresh visit honors OS; no
      flash; both modes legible on every page.
