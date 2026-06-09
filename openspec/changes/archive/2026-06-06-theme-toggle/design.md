# Design: Dark/Light Theme Toggle

## Decision 1 — Class-based dark mode (`.dark` on `<html>`), not `prefers-color-scheme` media
**Choice:** Toggle a `.dark` class on `<html>` and gate styles with a Tailwind `dark` custom variant.
**Rationale:** A media-query-only dark mode cannot be overridden by a user-facing button. The user
explicitly wants a *button*, so the theme must be user-controlled and persisted. OS preference is
used only to pick the initial default. Tailwind v4 expresses this with:
```css
@custom-variant dark (&:where(.dark, .dark *));
```
`:where(...)` keeps specificity at 0 so `dark:` variants don't unexpectedly outrank base utilities.

## Decision 2 — No `next-themes`; a ~10-line `lib/theme.ts` helper
**Rationale:** The need is small (one boolean, localStorage, an inline script). A dependency adds
surface area and version coupling for two apps with no workspace tooling. Keeping it local also
makes the two apps trivially identical.

```ts
// lib/theme.ts (identical in both apps)
export type Theme = "light" | "dark";
export const THEME_KEY = "lex-theme";

export function getStoredTheme(): Theme | null {
  if (typeof window === "undefined") return null;
  const v = window.localStorage.getItem(THEME_KEY);
  return v === "light" || v === "dark" ? v : null;
}

export function systemTheme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function resolveTheme(): Theme {
  return getStoredTheme() ?? (typeof window !== "undefined" ? systemTheme() : "light");
}

export function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
}

export function setTheme(theme: Theme) {
  window.localStorage.setItem(THEME_KEY, theme);
  applyTheme(theme);
}
```

## Decision 3 — No-FOUC inline script in `layout.tsx`, before paint
**Rationale:** React renders after hydration; if we set `.dark` only from a `useEffect`, a
light-themed first paint flashes for dark users. We inject a synchronous `<script>` in the server
`layout.tsx` that resolves and applies the theme before the body paints. `<html>` gets
`suppressHydrationWarning` because the class it carries at hydration time was set by that script,
not by React.

```tsx
// layout.tsx — inside <head>, before children render
const themeScript = `(function(){try{var t=localStorage.getItem('lex-theme');
if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
if(t==='dark')document.documentElement.classList.add('dark');}catch(e){}})();`;
// <html lang="en" suppressHydrationWarning ...>
//   <head><script dangerouslySetInnerHTML={{ __html: themeScript }} /></head>
```
The literal storage key (`lex-theme`) is duplicated in the inline string because the script must be
self-contained (no imports) to run before the bundle loads — it stays in sync with `THEME_KEY`.

## Decision 4 — `ThemeToggle` lives in the topbar, hydration-safe
**Rationale:** The topbar is already a `"use client"` component present on every dashboard page and
is the conventional home for such controls. The button reads its initial state in a `useEffect`
(post-mount) to avoid SSR/CSR mismatch — before mount it renders a neutral icon. Clicking calls
`setTheme(next)` and updates local state for the icon.

```tsx
// components/theme-toggle.tsx ("use client")
// mounted? show sun in dark / moon in light; onClick -> setTheme(theme==='dark'?'light':'dark')
```

## Decision 5 — Styling sweep order: variant, not redesign
**Rationale:** The palette is small and consistent (mostly `slate-*`, `white`, accent `indigo`).
We add `dark:` companions rather than introducing a semantic token layer (which would churn every
class with no extra benefit at this size). Sweep order maximizes coverage per edit:
1. `globals.css` base colors (body bg/fg) — the canvas.
2. `ui.tsx` primitives + shell (`sidebar`, `topbar`, dashboard `layout`) — composed by most pages.
3. Page-level wrappers (`(dashboard)/**`, `login`, `activar`) — residual literal classes.

Mapping convention (light → dark):
| Light | Dark |
|-------|------|
| `bg-white` / `bg-slate-50` | `dark:bg-slate-900` / `dark:bg-slate-950` |
| `bg-slate-100` | `dark:bg-slate-800` |
| `border-slate-200` / `-100` | `dark:border-slate-700` / `-800` |
| `text-slate-800` / `-700` | `dark:text-slate-100` / `-200` |
| `text-slate-600` / `-500` | `dark:text-slate-300` / `-400` |
| `text-slate-400` | `dark:text-slate-500` |
| accents (`indigo`, `emerald`, `rose`) | left as-is (legible on both) |

## Verification
- `pnpm --dir lex-control-admin build` and `pnpm --dir lex-control-client build` compile clean.
- Manual: toggle in each app; reload (persists); first visit honors OS; no flash; both modes legible.
