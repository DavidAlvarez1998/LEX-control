# Tasks: Refresh the README docs

## 1. Verify current scope before writing

- [x] 1.1 Re-read the admin nav (`lex-control-admin/src/lib/nav.tsx`) and client nav
      (`lex-control-client/src/lib/nav.tsx`) to confirm the live module list.
- [x] 1.2 Spot-check the root README ops sections (env vars, scripts table, Docker
      commands) against the actual files; note any stale fact to fix in passing.
      → ops sections accurate; no stale fact found.

## 2. Root README (umbrella repo)

- [x] 2.1 Rewrite the intro paragraph + ASCII summary to reflect the real platform
      scope (practice-management: clientes/CRM, procesos legales, facturación,
      contable, contratos, agenda — multi-tenant law firms).
- [x] 2.2 Add a **"Módulos"** section: admin modules + client modules, one line each,
      each pointing to its `openspec/specs/` or `openspec/changes/` entry.
- [x] 2.3 Add a one-line pointer to `openspec/` as the source of truth for design/specs.
- [x] 2.4 Apply any stale-fact fixes found in 1.2 (only if needed). → none needed.

## 3. Per-project READMEs (each in its own submodule repo)

- [x] 3.1 `lex-control-api/README.md` (new): purpose + scripts table + link to root.
- [x] 3.2 `lex-control-admin/README.md`: replace create-next-app boilerplate with
      purpose (:3000 ADMIN console) + commands + env contract + link to root.
- [x] 3.3 `lex-control-client/README.md` (new): purpose (:3001 CLIENTE portal) +
      commands + env contract + link to root.

## 4. Wrap-up

- [x] 4.1 Proofread (links resolve, ports/commands correct, Spanish consistent).
- [ ] 4.2 Commit per repo (submodules first, then bump pointers in the umbrella;
      follow the submodule workflow in the root README).
- [ ] 4.3 Archive this change in `openspec/` once applied.
