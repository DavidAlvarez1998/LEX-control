# Tasks: contable-module

> PROPOSAL — not applied. Builds on the APPLIED `foundations-roles-plans-clientes` (Cliente, contable
> Modulo esBaseline=false, RolEmpresa.CONTABLE, requirePermiso módulo-gate + RBAC, the COMERCIAL-array
> seed idiom), the APPLIED+ARCHIVED `comercial-funnel` (ContratoComercial, ConfiguracionCobro,
> ModalidadCobro enum, the saldoPendiente serializer placeholder), and `legal-tramites` (Proceso, radicado).
> `Cliente`/`Proceso` are anchors and are NOT redefined (only virtual back-relations). `ConfiguracionCobro`/
> `ContratoComercial` are READ-only (contable NEVER writes comercial). DDL via `prisma db push` (repo has
> NO migrations dir) — never `prisma migrate dev` against the live DB. No backfill (all new tables start
> empty; the first Cartera/Ingreso row is lazy).

## Review Workload Forecast
- **Changed-lines budget: High** (~900–1200 lines: 17 enums + 8 models in `schema.prisma`, a `CONTABLE` permiso array + RBAC in `seed-foundations.ts`, the contable router/schemas/service, the derived serializers — saldoActual/saldoRestante/cartera saldoPendiente — the estadoCartera recompute on Ingreso write, and the monthly report's 4-table separate aggregates).
- **Chained PRs recommended: Yes** — split along the eight capabilities plus the cross-cutting schema/seed.
- **Suggested split:** Phase 1 (schema + push + permiso seed) → Phase 2 (ingresos + egresos) → Phase 3 (nomina + cajamenor + serviciosfijos) → Phase 4 (cuentas + derived bolsa balances) → Phase 5 (cartera — the comercial saldo-resolution loop) → Phase 6 (reportes) → Phase 7 (verify). Cartera (Phase 5) depends on ingresos (valorPagado) and the read-only comercial join, so keep it after Phase 2 and chained.

## Phase 0 — Confirm scope
- [ ] 0.1 Q1 estadoCartera persistence — confirm STORE `estadoCartera` label (recomputed on Ingreso write) while money stays derived (recommend YES; one indexable label, no money drift). [Affects Phase 5.]
- [ ] 0.2 Q2 nómina staff ref — confirm scalar `empleadoId` (NO FK, → `Usuario.id` today) + required `nombreEmpleado` snapshot, NO contable `Empleado` entity now (recommend YES; login-less/seat-free staff). [Blocks Phase 3 schema.]
- [ ] 0.3 Q3 cartera grain — confirm per-contrato head (`@unique contratoId` + `@unique configuracionCobroId`), `procesoId` an attribute (recommend YES; matches the 1:1 ConfiguracionCobro↔ContratoComercial spine). [Blocks Phase 5.]
- [ ] 0.4 Q4 valorTotalAcordado — confirm frozen SNAPSHOT at cartera-open + explicit re-sync action (recommend YES; mirrors cobroSnapshot immutability).
- [ ] 0.5 Q5 expense aggregation — confirm the 4 source tables summed SEPARATELY, NO settling-Egreso, Egreso limited to costs not covered by typed tables (recommend YES; one documented helper).
- [ ] 0.6 Q6 Ingreso↔plan linkage — confirm prefer `configuracionCobroId`, fall back to `clienteId`(+`procesoId`); general income (configCobroId null) INCLUDED in totalIngresosMes, EXCLUDED from cartera (recommend YES).
- [ ] 0.7 Q7 totalGastosProceso grouping — confirm groupBy `procesoId`, `radicado` display-only (recommend YES; dodge null-radicado drift).
- [ ] 0.8 Q8 caja menor shape — confirm `CajaMenor` header + `CajaMenorMovimiento` (cajaId Cascade) (recommend YES; cleanest derived saldo, the only satellite-of-satellite).
- [ ] 0.9 Q9 documents — confirm inline `soporte*Url` for v1, reserve `DocumentoContable` name (recommend YES; one soporte per row in v1).

## Phase 1 — Backend: schema, db push, permiso seed
- [ ] 1.1 `schema.prisma`: 17 enums — `TipoCobroIngreso`, `MetodoPago` (shared), `EstadoPagoIngreso`, `TipoGastoEgreso`, `CategoriaEgreso`, `EstadoGastoEgreso`, `TipoVinculacion`, `EstadoPagoNomina`, `CategoriaCajaMenor`, `TipoMovCaja`, `EstadoCajaMenor`, `TipoServicioFijo`, `EstadoServicioFijo`, `TipoCuentaBancaria`, `EstadoCuentaBancaria`, `EstadoCartera`. REUSE `ModalidadCobro` from comercial (do NOT redefine). Money `Decimal(14,2)`, pct `Decimal(5,2)`.
- [ ] 1.2 `schema.prisma`: `Ingreso` (`@@map("ingresos")`) — `clienteId` SOLE FK Cascade; scalar `procesoId`/`contratoId`/`configuracionCobroId`/`cuentaId`/`registradoPorId` (NO FK); `radicado` snapshot; indexes `[empresaId, fechaIngreso]`, `[clienteId]`, `[empresaId, procesoId]`, `[empresaId, radicado]`, `[configuracionCobroId]`, `[empresaId, estadoPago]`.
- [ ] 1.3 `schema.prisma`: `Egreso` (`@@map("egresos")`) — tenant-scoped LEAF (NO Cascade FK; all refs scalar); `tipoGasto`/`categoriaGasto`; indexes `[empresaId, fechaGasto]`, `[empresaId, categoriaGasto]`, `[empresaId, radicado]`, `[empresaId, procesoId]`.
- [ ] 1.4 `schema.prisma`: `Nomina` (`@@map("nominas")`) — tenant-scoped LEAF; scalar `empleadoId` (NO FK) + REQUIRED `nombreEmpleado` snapshot; `periodo 'YYYY-MM'`; all money `Decimal(14,2)`; indexes `[empresaId, periodo]`, `[empresaId, empleadoId]`. NO contable `Empleado` entity.
- [ ] 1.5 `schema.prisma`: `CajaMenor` (`@@map("cajas_menores")`) tenant-scoped LEAF + `movimientos` back-relation; index `[empresaId]`. `CajaMenorMovimiento` (`@@map("caja_menor_movimientos")`) — `cajaId` SOLE FK Cascade; scalar `procesoId`/`responsableId`; indexes `[cajaId, fechaMovimiento]`, `[empresaId]`.
- [ ] 1.6 `schema.prisma`: `ServicioFijo` (`@@map("servicios_fijos")`) — tenant-scoped LEAF; `@@unique([empresaId, tipoServicio, proveedor, periodo])`; indexes `[empresaId, periodo]`, `[empresaId, estadoPago, fechaVencimiento]`.
- [ ] 1.7 `schema.prisma`: `CuentaBancaria` (`@@map("cuentas_bancarias")`) — tenant-scoped LEAF; `saldoInicial Decimal(14,2) @default(0)` ONLY (no stored saldoActual); indexes `[empresaId]`, `[empresaId, estadoCuenta]`.
- [ ] 1.8 `schema.prisma`: `Cartera` (`@@map("cartera")`) — `clienteId` SOLE FK Cascade; scalar `contratoId @unique`/`configuracionCobroId @unique`/`procesoId`/`responsableId` (NO FK); `valorTotalAcordado Decimal(14,2)?` snapshot; `tipoCobro ModalidadCobro` (reuse); `estadoCartera` maintained label; indexes `@@unique([contratoId])`, `@@unique([configuracionCobroId])`, `[empresaId, estadoCartera]`, `[clienteId]`, `[empresaId, fechaProximoPago]`. Schema comment: valorPagado/saldoPendiente DERIVED, never stored.
- [ ] 1.9 Add virtual back-relations on `Cliente` (`ingresos Ingreso[]`, `cartera Cartera[]`) and `CajaMenor` (`movimientos`) — relation fields only, NO column changes to `clientes`/existing tables. `prisma format` + `prisma validate` clean.
- [ ] 1.10 `prisma db push` + `prisma generate`. Verify 8 tables created, no errno-150 (only Ingreso→Cliente, Cartera→Cliente, CajaMenorMovimiento→CajaMenor cascade), no existing column/enum changed (ModalidadCobro unchanged), existing tests still green. (NO `prisma migrate dev`, NO backfill.)
- [ ] 1.11 `seed-foundations.ts`: add a `CONTABLE` array (mirror the existing `COMERCIAL` array) → `PERMISOS.push({ clave, nombre, modulo: "contable" })` + RBAC loop; main MODULOS/PERMISOS/RBAC loops unchanged. Claves: `contable.ingreso.{ver,crear,editar}`, `contable.egreso.{ver,crear,editar}`, `contable.nomina.{ver,crear,editar}`, `contable.cajamenor.{ver,crear,editar}`, `contable.serviciofijo.{ver,crear,editar}`, `contable.cuenta.{ver,crear,editar}` (`soloAdmin`), `contable.cartera.ver` (`soloAdmin`), `contable.reporte.ver` (`soloAdmin`). RBAC `[ADMINISTRADOR, CONTABLE]` EXCEPT the `soloAdmin` claves → `[ADMINISTRADOR]`. Idempotent upserts; re-run safe.

## Phase 2 — contable-ingresos + contable-egresos
- [ ] 2.1 `src/modules/contable/contable.schemas.ts` + `contable.router.ts` (mounted `/contable` in `app.ts`): Ingreso CRUD — `empresaId` from `req`, hard WHERE, `assertSameEmpresa` on `clienteId`/`procesoId`/`contratoId`/`configuracionCobroId`/`cuentaId`/`registradoPorId`; snapshot `radicado` from the referenced `Proceso` at insert. Gated by `requirePermiso("contable.ingreso.{ver,crear,editar}")`.
- [ ] 2.2 Egreso CRUD — `contable.egreso.*`; tenant-scoped leaf (no Cascade); `tipoGasto GENERAL/POR_PROCESO`; `assertSameEmpresa` on `clienteId`/`procesoId`/`cuentaId`/`responsableId`/`registradoPorId`. Document the no-settling-Egreso doctrine in the service.
- [ ] 2.3 Append-only discipline: Ingreso/Egreso edits are corrections (audited), not history-rewrites; `estadoPago`/`estadoGasto` transitions validated.

## Phase 3 — contable-nomina + contable-cajamenor + contable-serviciosfijos
- [ ] 3.1 Nomina CRUD — `contable.nomina.*`; `assertSameEmpresa` on `empleadoId` (and assert it is firm staff, NOT a platform ADMIN with `empresaId=null`) when set; require `nombreEmpleado`/`cargo`/`tipoVinculacion` snapshot; `assertSameEmpresa` on `cuentaId`; `valorNetoPagar` frozen COP.
- [ ] 3.2 CajaMenor header CRUD — `contable.cajamenor.*`; `assertSameEmpresa` on `responsableId`. CajaMenorMovimiento CRUD — `cajaId` Cascade root; `assertSameEmpresa` on `cajaId`/`procesoId`/`responsableId`.
- [ ] 3.3 `contable.service.ts`: CajaMenor `saldoActual` = `montoInicial - SUM(SALIDA) + SUM(REPOSICION)`; movement `saldoRestante` running balance DERIVED in serializer ordered by `fechaMovimiento` — NEVER stored (no race).
- [ ] 3.4 ServicioFijo CRUD — `contable.serviciofijo.*`; `@@unique([empresaId, tipoServicio, proveedor, periodo])`; `VENCIDO` derived from `fechaVencimiento < now` for non-PAGADO rows; `assertSameEmpresa` on `cuentaId`.

## Phase 4 — contable-cuentas (bolsas + derived saldoActual)
- [ ] 4.1 CuentaBancaria CRUD — `contable.cuenta.*` (ADMINISTRADOR-only); store ONLY `saldoInicial`; `assertSameEmpresa` on `responsableId`.
- [ ] 4.2 `contable.service.ts`: derive `saldoActual = saldoInicial + SUM(Ingreso PAGADO by cuentaId) - SUM(Egreso PAGADO by cuentaId)` (optionally minus PAGADO Nomina/ServicioFijo by cuentaId) — read-time, never stored.
- [ ] 4.3 App-level Restrict on delete: block deleting a `CuentaBancaria` while any Ingreso/Egreso/Nomina/ServicioFijo/movimiento references it via `cuentaId`; `INACTIVA`/`CONCILIACION_PENDIENTE` is the soft-disable path.

## Phase 5 — contable-cartera (THE COMERCIAL SALDO-RESOLUTION LOOP)
- [ ] 5.1 `POST /contable/cartera` (`contable.cartera.ver`, ADMINISTRADOR-only): one head per cobro plan; `@unique contratoId`/`configuracionCobroId`; `assertSameEmpresa` on `clienteId`/`procesoId`/`contratoId`/`configuracionCobroId`/`responsableId`.
- [ ] 5.2 Snapshot `valorTotalAcordado` from the READ-only `ConfiguracionCobro` by `modalidadCobro` (FIJO→valorFijo; CUOTALITIS/CUOTA_MIXTA→numeroCuotas*valorCuota (+valorFijo if mixed); PRIMA_EXITO→null/contingent; fallback `ContratoComercial.valorAcordado`); `tipoCobro` denormalized from `ModalidadCobro`. **FLAG**: this READS comercial; contable NEVER writes comercial.
- [ ] 5.3 Explicit re-sync action — re-read `ConfiguracionCobro` to refresh `valorTotalAcordado` on demand; plan edits never silently move the snapshot.
- [ ] 5.4 `contable.service.ts` derived cartera: `valorPagado = SUM(Ingreso WHERE configuracionCobroId match OR (clienteId+procesoId) AND estadoPago IN {PAGADO,PARCIAL})`; `saldoPendiente = valorTotalAcordado - valorPagado`; both DERIVED, never stored. General income (`configuracionCobroId = null`) EXCLUDED from cartera math.
- [ ] 5.5 Maintain the ONE label `estadoCartera` (derived LABEL, not money): recompute inside the SAME request on every Ingreso write — `PAGADO` if saldo<=0; `PARCIAL` if 0<valorPagado<total; `VENCIDO` if saldo>0 AND fechaProximoPago<now; `AL_DIA` otherwise. PRIMA_EXITO/contingent → `saldoPendiente` null/'indeterminado', excluded from aggregation.
- [ ] 5.6 Shared `valorPagado`/`saldoPendiente` helper the comercial serializer MAY call to backfill its `saldoPendiente` placeholder; `GET /contable/cartera` returns derived saldos. **FLAG**: the one comercial↔contable coupling, read-only from contable's side.

## Phase 6 — contable-reportes (DERIVED monthly P&L)
- [ ] 6.1 `GET /contable/reportes?periodo=YYYY-MM` (`contable.reporte.ver`, ADMINISTRADOR-only): hard `WHERE { empresaId }` + month range; one Prisma aggregate/groupBy per block; JSON only (no Excel/PDF — `export_excel` is a flag).
- [ ] 6.2 `totalIngresosMes` (Ingreso PAGADO/PARCIAL); `totalEgresosMes` = Egreso PAGADO + Nomina PAGADO + (CajaMenorMovimiento SALIDA - REPOSICION) + ServicioFijo PAGADO — 4 tables summed SEPARATELY (no settling-Egreso, no double-count); `utilidadNeta = ingresos - egresos`.
- [ ] 6.3 `totalGastosProceso` = groupBy `procesoId` SUM(Egreso POR_PROCESO), `radicado` display-only; plus cartera block (SUM derived saldoPendiente + breakdown by estadoCartera, PRIMA_EXITO excluded), caja-menor block, servicios-fijos block (by estadoPago + vencidos), bolsas block (derived saldoActual list).

## Phase 7 — Verify
- [ ] 7.1 `tsc --noEmit` clean after `prisma generate`.
- [ ] 7.2 `pnpm test` — existing suite still green + new contable tests: tenancy isolation (cross-empresa cuentaId/procesoId/configuracionCobroId rejected), no errno-150, Ingreso clienteId Cascade, Egreso leaf no-FK, Nomina snapshot survives empleado deactivation + platform-ADMIN rejected, CajaMenor derived running balance, ServicioFijo period @unique, CuentaBancaria derived saldoActual + delete-blocked-while-referenced, Cartera one-per-contract + snapshot no-drift + estadoCartera recompute on Ingreso write + general income excluded + PRIMA_EXITO indeterminate, report 4-table separate-sum (no double-count), CONTABLE rep cannot create cuenta/cartera/reporte (ADMINISTRADOR-only), contable never writes comercial.
- [ ] 7.3 Live (on a non-prod copy first): `db push` + re-run seed (idempotent); module gate (`contable` not contracted → 403 "Módulo no contratado", `esAdminEmpresa` does NOT bypass); end-to-end: Ingreso against a contracted ConfiguracionCobro → Cartera estadoCartera PAGADO + comercial saldoPendiente backfilled; monthly report derives utilidadNeta.

## Notes
- DDL: repo uses `prisma db push` (no `prisma/migrations/`). Rollback = manual DROP of the 8 new tables (FK-dependency order: `cartera`, `ingresos`, `caja_menor_movimientos`, `cajas_menores`, `egresos`, `nominas`, `servicios_fijos`, `cuentas_bancarias`) + 16 new enums (do NOT drop `ModalidadCobro` — owned by comercial). Test on a non-prod copy first; `db push` can warn on data loss.
- Env/perms: `lex-control-api/.env` (DATABASE_URL) is write-blocked per repo memory — push/seed use the existing connection without editing `.env`.
- `Cliente`/`Proceso` are NEVER redefined: no columns, no enum changes — only virtual back-relations on `Cliente` (`ingresos`, `cartera`). `ConfiguracionCobro`/`ContratoComercial` are READ-only; contable NEVER writes into comercial.
- DERIVE doctrine is absolute: `saldoActual`/`saldoRestante`/`valorPagado`/`saldoPendiente`/`totalIngresosMes`/`utilidadNeta` are computed in the read/serializer layer, NEVER persisted (matches comercial-alertas). The ONLY maintained column is `Cartera.estadoCartera` (a derived label, recomputed on Ingreso write) for an indexable vencido-alert filter. NO scheduler.
- No double-counting: the 4 source expense tables (Egreso, Nomina, CajaMenorMovimiento, ServicioFijo) are INDEPENDENT and summed SEPARATELY; Egreso holds only costs not covered by a typed table; NO settling-Egreso emission.
- Nómina staff = scalar `empleadoId` (NO FK, → `Usuario.id` today, future `Empleado.id` later) + required `nombreEmpleado` snapshot; NO contable `Empleado` entity (collides with future HR módulo; payroll subjects may be login-less / must not consume seats).
- RBAC: `[ADMINISTRADOR, CONTABLE]` for ingreso/egreso/nomina/cajamenor/serviciofijo; `[ADMINISTRADOR]` only (`soloAdmin`) for cuenta config, cartera gestión, and reporte. The `contable` módulo gate (esBaseline=false → 403 "Módulo no contratado") is already in place; `esAdminEmpresa` does NOT bypass it.
- Documents: inline `soporte*Url String?` per table (`soportePagoUrl`, `soporteGastoUrl`, `comprobantePagoUrl`, `soporteUrl`, `soporteFacturaUrl`) — URLs only, no upload infra. `DocumentoContable` is a reserved name only (Q9), not built in v1.