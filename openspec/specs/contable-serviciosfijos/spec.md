# Contable — Servicios Fijos Specification

> New capability introduced by change `contable-module`. Adds `ServicioFijo`, the per-period recurring fixed-bill table as a tenant-scoped leaf, with a period-uniqueness constraint and a date-passed vencimiento heuristic.

## ADDED Requirements

### Requirement: ServicioFijo recurring fixed bills per period as a tenant-scoped leaf
The system MUST store recurring fixed bills in `servicios_fijos`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), `periodo` String `'YYYY-MM'`, `tipoServicio` `TipoServicioFijo`, `proveedor` String, `valorFacturado` `Decimal(14,2)`, optional `fechaVencimiento`, optional `fechaPago`, `estadoPago` `EstadoServicioFijo @default(PENDIENTE)`, scalar `cuentaId?` (NO FK), optional `soporteFacturaUrl` (URL only), optional `observaciones` (Text). It is a TENANT-SCOPED LEAF (NO Cascade FK). It MUST declare `@@unique([empresaId, tipoServicio, proveedor, periodo])` and index `@@index([empresaId, periodo])`, `@@index([empresaId, estadoPago, fechaVencimiento])` (the vencimiento alert index). `VENCIDO` MAY also be DERIVED at read-time from `fechaVencimiento < now` for rows not yet `PAGADO`.

#### Scenario: Record the monthly internet bill
- GIVEN a user holding `contable.serviciofijo.crear` in despacho A
- WHEN they POST a `ServicioFijo` with `tipoServicio = INTERNET`, `proveedor`, `periodo = '2026-06'`, `valorFacturado`
- THEN it is created `estadoPago = PENDIENTE` with `empresaId` from the token

#### Scenario: One row per (tipo, proveedor, periodo)
- GIVEN a `ServicioFijo` already exists for `(empresaId, INTERNET, 'Claro', '2026-06')`
- WHEN a second identical row is created
- THEN it is rejected by the `@@unique([empresaId, tipoServicio, proveedor, periodo])`

#### Scenario: Vencido is a date-passed heuristic
- GIVEN a `ServicioFijo` with `estadoPago = PENDIENTE` and `fechaVencimiento` in the past
- WHEN the servicios-fijos block is computed
- THEN it surfaces as vencido (derived from `fechaVencimiento < now`), regardless of any external payment fact

### Requirement: Enums TipoServicioFijo, EstadoServicioFijo
The system MUST define `TipoServicioFijo { AGUA, LUZ, GAS, INTERNET, TELEFONO, ARRIENDO, SOFTWARE, MANTENIMIENTO, VIGILANCIA, OTRO }` and `EstadoServicioFijo { PAGADO, PENDIENTE, VENCIDO } @default(PENDIENTE)`. Additive; MUST NOT modify any existing enum.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoServicioFijo` and `EstadoServicioFijo` exist with the listed members AND no existing enum is changed

### Requirement: Tenancy and permiso gating mirror the clientes router
Every servicio-fijo endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `cuentaId` on CREATE/PATCH, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave (`contable.serviciofijo.ver`/`.crear`/`.editar`). The `contable` módulo gate applies.

#### Scenario: Scoped by token empresaId
- GIVEN a user of despacho A
- WHEN they GET `/contable/servicios-fijos?periodo=2026-06`
- THEN only despacho A's rows are returned (hard `WHERE { empresaId }`)

### Requirement: ServicioFijoRecurrente template defines a recurring fixed bill once
> ADDED by change `contable-servicios-fijos-recurrentes`.

The system MUST store recurring templates in `servicios_fijos_recurrentes`: `id` (cuid), `empresaId` (denormalized, NO FK), `tipoServicio` `TipoServicioFijo`, `proveedor` String, `valorEstimado` `Decimal(14,2)`, `frecuencia` `FrecuenciaServicioFijo @default(MENSUAL)`, `diaPago` Int (1..31), `mesPago` Int? (1..12, REQUIRED when `frecuencia = ANUAL`), scalar `cuentaId?` (NO FK), `activo` `Boolean @default(true)`, optional `observaciones` (Text). It is a TENANT-SCOPED LEAF (NO Cascade FK beyond `empresa`). It MUST declare `@@unique([empresaId, tipoServicio, proveedor])` and index `@@index([empresaId, activo])`. The enum `FrecuenciaServicioFijo { MENSUAL, ANUAL }` MUST exist (additive). `ServicioFijo` MUST gain a scalar `recurrenteId?` (NO FK) tracing the template that generated it, with `@@index([empresaId, recurrenteId])`.

#### Scenario: Create a monthly template
- GIVEN a user holding `contable.serviciofijo.crear` in despacho A
- WHEN they POST a template with `tipoServicio`, `proveedor`, `valorEstimado`, `frecuencia = MENSUAL`, `diaPago = 5`
- THEN it is created `activo = true` with `empresaId` from the token

#### Scenario: Annual template requires mesPago
- GIVEN a POST/PATCH with `frecuencia = ANUAL` and no `mesPago`
- WHEN it is validated
- THEN it is rejected (400) — `mesPago` is mandatory for ANUAL

### Requirement: Generate the period instances from active templates (idempotent)
> ADDED by change `contable-servicios-fijos-recurrentes`.

The system MUST expose `POST /contable/servicios-fijos-recurrentes/generar` `{ periodo }` (gated by `contable.serviciofijo.crear`, token `empresaId`) that materializes one `ServicioFijo` per applicable active template: **MENSUAL** applies to every period; **ANUAL** applies ONLY when `month(periodo) == mesPago`. Each generated instance copies `valorEstimado → valorFacturado`, sets `estadoPago = PENDIENTE`, carries `recurrenteId` and the template `cuentaId`, and computes `fechaVencimiento` from `periodo` + `diaPago` CLAMPED to the last day of that month (e.g. day 31 in February → 28/29). Generation MUST be IDEMPOTENT: it MUST NOT duplicate rows that already exist for `(empresaId, tipoServicio, proveedor, periodo)` (`skipDuplicates`). The response reports `{ candidatas, generadas, omitidas }`.

#### Scenario: Monthly applies, annual only in its month
- GIVEN an active MENSUAL template (day 5) and an active ANUAL template (mesPago = 11, day 20)
- WHEN generating periodo `2026-06`
- THEN only the MENSUAL template is a candidate, with `fechaVencimiento = 2026-06-05`
- AND WHEN generating periodo `2026-11` THEN both apply

#### Scenario: Re-generating the same period creates no duplicates
- GIVEN the instances for periodo `2026-06` already exist
- WHEN generación is run again for `2026-06`
- THEN `generadas = 0` and `omitidas` accounts for the skipped rows (the `@@unique` is respected)

### Requirement: VENCIDO is derived at read-time, never stored
> ADDED by change `contable-servicios-fijos-recurrentes`.

`GET /contable/servicios-fijos` MUST return, per row, a DERIVED boolean `vencido = (estadoPago != PAGADO AND fechaVencimiento != null AND fechaVencimiento < now)`. It MUST NOT mutate the stored `estadoPago` (a pending overdue bill stays `PENDIENTE` in the DB and surfaces as vencido only in the read). A `PAGADO` row past its `fechaVencimiento` is NOT vencido.

#### Scenario: Pending overdue bill surfaces as vencido
- GIVEN a `ServicioFijo` `estadoPago = PENDIENTE` with `fechaVencimiento` in the past
- WHEN the servicios-fijos list is read
- THEN the row carries `vencido = true` AND its stored `estadoPago` is still `PENDIENTE`

#### Scenario: Paid or not-yet-due bills are not vencido
- GIVEN a `PAGADO` row with a past `fechaVencimiento`, and a `PENDIENTE` row with a future one
- WHEN the list is read
- THEN both carry `vencido = false`

### Requirement: soporteFacturaUrl is editable from the instance form
> ADDED by change `contable-servicios-fijos-recurrentes`.

The servicio-fijo create/edit form MUST expose `soporteFacturaUrl` (a URL string to the bill support), persisted through the existing create/update endpoints. When set, the UI MUST offer a link to open it.

#### Scenario: Capture and persist the bill support URL
- GIVEN a user editing a `ServicioFijo`
- WHEN they set `soporteFacturaUrl = https://…/factura.pdf` and save
- THEN it is stored and returned on the next read, with an "open support" link in the UI