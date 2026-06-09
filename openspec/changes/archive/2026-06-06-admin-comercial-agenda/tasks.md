# Tasks — admin-comercial-agenda

## Phase 1 — Schema
- [x] 1.1 Add `model SeguimientoProspecto` to `schema.prisma` (reusing `TipoGestionComercial`); add `seguimientos SeguimientoProspecto[]` to `Prospecto`.
- [x] 1.2 `pnpm push` (db push to MySQL "LEX") + `pnpm generate`.

## Phase 2 — API
- [x] 2.1 `ventas.schemas.ts`: `createSeguimientoSchema`, `updateSeguimientoSchema`, `completarSeguimientoSchema`, `agendaQuery`.
- [x] 2.2 `ventas.router.ts`: nested `GET/POST /prospectos/:id/seguimientos` (reuse `cargarProspecto` scope; owner defaults from prospecto).
- [x] 2.3 `ventas.router.ts`: `seguimientoRoutes` — `PATCH /:id`, `POST /:id/completar`, `DELETE /:id` (scope via parent prospecto; COMERCIAL can't move `comercialId`).
- [x] 2.4 `ventas.router.ts`: `agendaRoutes` — `GET /` (range default today; `vencidas` block; prospecto summary join; COMERCIAL hard-scoped, ADMIN `comercialId` filter).
- [x] 2.5 `app.ts`: mount `/seguimientos` and `/agenda`.

## Phase 3 — Admin UI
- [x] 3.1 `lib/ventas.ts`: add `seguimientos(prospectoId)`, `addSeguimiento`, `updateSeguimiento`, `completarSeguimiento`, `deleteSeguimiento`, `agenda(params)` + types.
- [x] 3.2 Prospecto detail: Seguimiento **timeline** + add/schedule form + "Completar".
- [x] 3.3 New page `/agenda`: day navigation, `vencidas` section, day list grouped, one-click Completar; ADMIN comercial `<select>`.
- [x] 3.4 `lib/nav.tsx`: add **Agenda** nav item (icon) for ADMIN+COMERCIAL.

## Phase 5 — Admin team oversight (Equipo comercial)
- [x] 5.1 API: `GET /equipo-comercial` (ADMIN only) — comerciales + counters (prospectos/ganados/pendientesAgenda) via groupBy; mounted in app.ts.
- [x] 5.2 Admin: extract `DetalleProspecto`+`SeguimientoTimeline` to `components/prospecto-detalle.tsx` (shared).
- [x] 5.3 Admin: new `/comercial` page — team cards (search) → comercial detail with their prospectos (filter estado/canal, open with timeline) + their agenda (vencidas + hoy, completar).
- [x] 5.4 Admin: add `comercialId` filter to `/prospectos`; nav item "Equipo comercial" (ADMIN only).
- [x] 5.5 Tests: `/equipo-comercial` 403 for COMERCIAL, counters for ADMIN, empty list; live smoke (equipo + prospectos filter + agenda by comercial).

## Phase 4 — Verify
- [x] 4.1 New tests `tests/agenda.test.ts`: log-now vs schedule, owner default, per-comercial 404 scope, complete, agenda range + vencidas + admin filter. Full API suite green.
- [x] 4.2 `pnpm --dir lex-control-api build` clean; admin `tsc`/`pnpm build` clean.
- [x] 4.3 Live smoke against running API: schedule activity → appears in `/agenda` → completar → leaves agenda, shows in timeline.
