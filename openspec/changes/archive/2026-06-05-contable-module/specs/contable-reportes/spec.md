# Contable — Reportes (Derived) Specification

> New capability introduced by change `contable-module`. Adds `GET /contable/reportes?periodo=YYYY-MM`, a fully DERIVED monthly P&L computed from per-block Prisma aggregates. There are NO stored report rows and NO scheduler; the 4 source expense tables are summed SEPARATELY to avoid double-counting.

## ADDED Requirements

### Requirement: Reports are derived aggregates, never stored rows
The system MUST expose `GET /contable/reportes?periodo=YYYY-MM` returning a derived monthly P&L computed on read and scoped by `empresaId` from the token + the period date range. It MUST NOT persist any report row and MUST NOT require a scheduler/cron. Each block MUST be one Prisma aggregate/groupBy. It MUST be gated by `requireAuth` + `requirePermiso("contable.reporte.ver")` (ADMINISTRADOR-only, `soloAdmin`). The `contable` módulo gate applies.

#### Scenario: No report table
- GIVEN the pushed schema
- WHEN the tables are inspected
- THEN there is no reportes table; the P&L is produced only by the read endpoint

#### Scenario: Scoped by token empresaId
- GIVEN a user of despacho A
- WHEN they GET `/contable/reportes?periodo=2026-06`
- THEN only despacho A's data feeds the aggregates (every underlying query hard-filters `{ empresaId }`)

### Requirement: Monthly P&L with the 4-table separate-sum doctrine (no double-count)
The report MUST compute: `totalIngresosMes = SUM(Ingreso.valorRecibido WHERE month = periodo AND estadoPago IN {PAGADO, PARCIAL})`; `totalEgresosMes = SUM(Egreso.valorGasto PAGADO) + SUM(Nomina.valorNetoPagar PAGADO) + SUM(CajaMenorMovimiento SALIDA - REPOSICION) + SUM(ServicioFijo.valorFacturado PAGADO)` for the month — the 4 source tables summed SEPARATELY (single documented doctrine, NO settling-Egreso, so no double-count); `utilidadNeta = totalIngresosMes - totalEgresosMes`; `totalGastosProceso = groupBy(procesoId) SUM(Egreso.valorGasto WHERE tipoGasto = POR_PROCESO)` (grouped by `procesoId`, `radicado` as a display key to dodge null-radicado drift). It MUST also include a cartera block (SUM derived `saldoPendiente` + breakdown by `estadoCartera`), a caja-menor block (derived saldos), a servicios-fijos block (sum by `estadoPago` + vencidos), and a bolsas block (list derived `saldoActual`).

#### Scenario: Egresos summed across 4 tables without double-counting
- GIVEN in periodo `'2026-06'` an `Egreso` GENERAL of 100000, a PAGADO `Nomina` of 2000000, a `CajaMenorMovimiento` SALIDA of 50000, and a PAGADO `ServicioFijo` of 150000
- WHEN `totalEgresosMes` is computed
- THEN it equals 2300000 (each table summed once, separately) and NO settling-Egreso was emitted for the Nomina/CajaMenor/ServicioFijo

#### Scenario: Per-proceso costs grouped by procesoId
- GIVEN several POR_PROCESO `Egreso` rows for the same `procesoId` with a later-filed `radicado`
- WHEN `totalGastosProceso` is computed
- THEN they are grouped by `procesoId` (stable) with `radicado` shown as a display key only

#### Scenario: PRIMA_EXITO cartera excluded from saldo aggregation
- GIVEN a cartera whose plan is `PRIMA_EXITO` with a null `valorTotalAcordado`
- WHEN the cartera block aggregates `saldoPendiente`
- THEN that cartera is reported as 'indeterminado' and excluded from the al_dia/vencido totals

### Requirement: Export is out of scope for v1
Excel/PDF export of the report MUST be out of scope for v1 (the `export_excel` módulo is a flag only). The endpoint returns JSON only.

#### Scenario: Report returns JSON, not a file
- GIVEN a user requesting `/contable/reportes?periodo=2026-06`
- WHEN the report is produced
- THEN it returns a derived JSON P&L and does NOT generate an Excel/PDF file