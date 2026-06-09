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