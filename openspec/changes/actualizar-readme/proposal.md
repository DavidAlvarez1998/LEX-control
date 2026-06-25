# Proposal: Refresh the README docs to match the real platform

## Why

The documentation has drifted from reality:

- **Root `README.md`** still describes LEX Control as a platform that "manages client
  companies, the service catalog, and billing" (its one-line scope and the intro
  paragraph). That was true at the start. Today the platform also runs a full **legal
  process module** (procesos by jurisdicción: civil verbal/ejecutivo, laboral,
  constitucional/tutela, derecho de petición, catálogo data-driven + document engine),
  a **comercial/CRM module** (funnel, prospectos, comisiones, agenda), a **contable**
  module, **contratos**, **facturación**, and **external integrations** (Rama Judicial
  / CPNU actuaciones, notificaciones SES/SMS/llamadas, documental tecnovapp). A new
  reader gets a wrong mental model of what the system does and how big it is.
- **`lex-control-admin/README.md`** is still the untouched `create-next-app`
  boilerplate ("This is a Next.js project bootstrapped with create-next-app…"). It
  carries zero project-specific information.
- **`lex-control-api/` and `lex-control-client/` have no README at all**, so there is
  no per-project entry point describing each project's purpose and commands.

The good news: the operational parts of the root README (requisitos, clonar con
submodules, variables de entorno, primera vez, levantar todo, Docker, scripts del API,
trabajar con submodules) are **accurate and current** — including the recent Docker
section. This change is about fixing the *scope/description* drift and the
boilerplate/missing per-project READMEs, not rewriting the setup instructions.

## What changes

1. **Root `README.md` — scope refresh (keep the ops sections).**
   - Rewrite the intro paragraph + the ASCII summary so the "what this is" matches the
     real platform: a multi-tenant practice-management platform for law firms covering
     clientes/CRM, legal processes, billing, accounting, contracts and agenda — not
     just empresas/servicios/facturación.
   - Add a concise **"Módulos" / "Qué hace"** section listing the real functional areas
     (derived from the two apps' navigation: admin = Dashboard, Empresas, Servicios,
     Planes, Catálogo de procesos, Facturación, API, Usuarios, Comercial, Agenda;
     client = Inicio, Clientes, Agenda, Procesos, Servicios, Contable, Facturación,
     Contratos, Equipo, Mi Cuenta), each with a one-line description and a pointer to
     its `openspec/specs/` or `openspec/changes/` entry for detail.
   - Add a one-line pointer to `openspec/` as the source of truth for design/specs
     (per the project's memory convention).
   - Leave Requisitos, Clonar, Variables de entorno, Primera vez, Levantar todo,
     Docker, Scripts del API and Submodules **as they are** unless a quick re-check
     finds a stale fact.

2. **Per-project READMEs.** Each project is its own repo (git submodule), so its README
   lives in that repo:
   - **`lex-control-api/README.md`** (new): one-paragraph purpose (`@lex/db` Prisma
     data layer growing into an Express HTTP API on :4000), the scripts table (reuse
     the one already in the root README), and "see root README for full setup".
   - **`lex-control-admin/README.md`** (replace boilerplate): purpose (platform-ADMIN
     console on :3000), `pnpm dev/build/start/lint`, env contract (`API_PROXY_TARGET` /
     `NEXT_PUBLIC_API_URL`), pointer to root.
   - **`lex-control-client/README.md`** (new): purpose (tenant/CLIENTE portal on
     :3001), same shape as admin.
   - Keep these short — they should not duplicate the root README, only point to it.

## Scope / non-goals

- **Docs only.** No code, schema, config, or behavior changes.
- Not touching `CLAUDE.md` (separate doc; its "current state" note is also stale but
  out of scope here).
- Not reorganizing `openspec/` — only adding pointers to it from the README.

## Rollback plan

Pure documentation edits across the umbrella repo and three submodule repos. Rollback =
`git revert` (or `git checkout -- README.md`) in whichever repo(s) the edits landed; no
runtime impact, nothing to migrate.
