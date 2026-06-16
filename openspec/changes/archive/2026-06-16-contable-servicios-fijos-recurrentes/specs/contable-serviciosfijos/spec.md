# Contable — Servicios Fijos · delta (recurrentes)

> Change `contable-servicios-fijos-recurrentes`. Extends the existing `contable-serviciosfijos`
> capability with a recurring-template model and a period-generation endpoint.

## ADDED Requirements

### Requirement: ServicioFijoRecurrente template defines a recurring fixed bill once
The system MUST store recurring templates in `servicios_fijos_recurrentes`: `id` (cuid), `empresaId`
(denormalized, NO FK), `tipoServicio` `TipoServicioFijo`, `proveedor` String, `valorEstimado`
`Decimal(14,2)`, `frecuencia` `FrecuenciaServicioFijo @default(MENSUAL)`, `diaPago` Int (1..31),
`mesPago` Int? (1..12, REQUIRED when `frecuencia = ANUAL`), scalar `cuentaId?` (NO FK), `activo`
`Boolean @default(true)`, optional `observaciones` (Text). It is a TENANT-SCOPED LEAF (NO Cascade FK
beyond `empresa`). It MUST declare `@@unique([empresaId, tipoServicio, proveedor])` and index
`@@index([empresaId, activo])`. The enum `FrecuenciaServicioFijo { MENSUAL, ANUAL }` MUST exist
(additive). `ServicioFijo` MUST gain a scalar `recurrenteId?` (NO FK) tracing the template that
generated it, with `@@index([empresaId, recurrenteId])`.

#### Scenario: Create a monthly template
- GIVEN a user holding `contable.serviciofijo.crear` in despacho A
- WHEN they POST a template with `tipoServicio`, `proveedor`, `valorEstimado`, `frecuencia = MENSUAL`, `diaPago = 5`
- THEN it is created `activo = true` with `empresaId` from the token

#### Scenario: Annual template requires mesPago
- GIVEN a POST/PATCH with `frecuencia = ANUAL` and no `mesPago`
- WHEN it is validated
- THEN it is rejected (400) — `mesPago` is mandatory for ANUAL

### Requirement: Generate the period instances from active templates (idempotent)
The system MUST expose `POST /contable/servicios-fijos-recurrentes/generar` `{ periodo }` (gated by
`contable.serviciofijo.crear`, token `empresaId`) that materializes one `ServicioFijo` per applicable
active template: **MENSUAL** applies to every period; **ANUAL** applies ONLY when `month(periodo) ==
mesPago`. Each generated instance copies `valorEstimado → valorFacturado`, sets `estadoPago = PENDIENTE`,
carries `recurrenteId` and the template `cuentaId`, and computes `fechaVencimiento` from `periodo` +
`diaPago` CLAMPED to the last day of that month (e.g. day 31 in February → 28/29). Generation MUST be
IDEMPOTENT: it MUST NOT duplicate rows that already exist for `(empresaId, tipoServicio, proveedor,
periodo)` (`skipDuplicates`). The response reports `{ candidatas, generadas, omitidas }`.

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
`GET /contable/servicios-fijos` MUST return, per row, a DERIVED boolean `vencido = (estadoPago !=
PAGADO AND fechaVencimiento != null AND fechaVencimiento < now)`. It MUST NOT mutate the stored
`estadoPago` (a pending overdue bill stays `PENDIENTE` in the DB and surfaces as vencido only in the
read). A `PAGADO` row past its `fechaVencimiento` is NOT vencido.

#### Scenario: Pending overdue bill surfaces as vencido
- GIVEN a `ServicioFijo` `estadoPago = PENDIENTE` with `fechaVencimiento` in the past
- WHEN the servicios-fijos list is read
- THEN the row carries `vencido = true` AND its stored `estadoPago` is still `PENDIENTE`

#### Scenario: Paid or not-yet-due bills are not vencido
- GIVEN a `PAGADO` row with a past `fechaVencimiento`, and a `PENDIENTE` row with a future one
- WHEN the list is read
- THEN both carry `vencido = false`

### Requirement: soporteFacturaUrl is editable from the instance form
The servicio-fijo create/edit form MUST expose `soporteFacturaUrl` (a URL string to the bill support),
persisted through the existing create/update endpoints. When set, the UI MUST offer a link to open it.

#### Scenario: Capture and persist the bill support URL
- GIVEN a user editing a `ServicioFijo`
- WHEN they set `soporteFacturaUrl = https://…/factura.pdf` and save
- THEN it is stored and returned on the next read, with an "open support" link in the UI
