# Tasks — admin-comercial-ventas

## Phase 1 — Schema
- [x] 1.1 `Rol += COMERCIAL`; `Usuario.porcentajeComision Decimal(5,2)?`.
- [x] 1.2 Enums `CanalEntrada`, `EstadoProspecto`, `EstadoComision`.
- [x] 1.3 Models `Prospecto` (scalar no-FK plan/comercial refs; `empresaId` unique FK SetNull) and
      `Comision` (scalar no-FK refs; `prospectoId` unique). `Empresa.prospecto Prospecto?` back-ref.
- [x] 1.4 `pnpm generate` + `pnpm push` (additive).

## Phase 2 — API (`modules/ventas/`)
- [x] 2.1 `ventas.schemas.ts`: create/update prospecto, ganar, perder, comision patch (zod).
- [x] 2.2 `prospectos.router` GET/POST/GET:id/PATCH + `/:id/ganar` + `/:id/perder`. Role scoping:
      `requireRole(ADMIN, COMERCIAL)`; COMERCIAL hard-scoped to `comercialId = sub`; only ADMIN sets
      `comercialId`; PATCH cannot set GANADO/PERDIDO directly. App-validate `planInteresId`/`planVendidoId`/`comercialId`.
- [x] 2.3 Win transaction: create Empresa + Suscripcion + Comision; default plan = planInteres, price
      = plan.precioMensual; commission = fixed override else precioVenta × comercial.porcentajeComision.
      Guard double-win (unique → 409).
- [x] 2.4 `comisiones.router` GET (scoped) + PATCH (ADMIN: PAGADA+fechaPago / ANULADA).
- [x] 2.5 (optional) `GET /ventas/reporte`: counts + monto vendido + comisiones por estado + by canal.
- [x] 2.6 Mount `/prospectos`, `/comisiones` (and `/ventas` if reporte) in `app.ts`.

## Phase 3 — Tests (`tests/ventas.test.ts`)
- [x] 3.1 COMERCIAL sees only own prospectos/comisiones; cannot reassign; cannot mark comisión paid.
- [x] 3.2 Create validates plan/canal; advance funnel; PATCH cannot set GANADO.
- [x] 3.3 Win creates Empresa+Suscripcion+Comision (% from rate); fixed-amount override; double-win 409.
- [x] 3.4 Lose sets PERDIDO + motivo. ADMIN marks comisión PAGADA (fechaPago set).
- [x] 3.5 Existing suite still green.

## Phase 4 — Admin UI (`lex-control-admin`)
- [x] 4.1 `lib/ventas.ts` (types + enums + api). Platform-role guard component (by `rol`).
- [x] 4.2 `/prospectos`: list filterable by estado/canal + create modal + detail (advance / Ganar /
      Perder). Money via the admin MoneyInput (explicit className per repo note).
- [x] 4.3 `/comisiones`: table + ADMIN "Marcar pagada".
- [x] 4.4 Usuarios screen: `COMERCIAL` in rol select + `porcentajeComision` field (shown for COMERCIAL).
- [x] 4.5 Nav entries `Prospectos`, `Comisiones`.

## Phase 5 — Verify
- [x] 5.1 `pnpm --dir lex-control-api build` clean; `pnpm test` green (+ new ventas tests).
- [x] 5.2 Admin `pnpm build` clean.
