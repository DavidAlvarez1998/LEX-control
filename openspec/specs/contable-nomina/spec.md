# Contable — Nómina Specification

> New capability introduced by change `contable-module`. Adds the per-period `Nomina` payroll table as a tenant-scoped leaf with a scalar `empleadoId` (NO FK) plus a required staff snapshot — deliberately NO contable `Empleado` entity (the future HR módulo owns that).

## ADDED Requirements

### Requirement: Nomina per-period payroll as a tenant-scoped leaf with a staff snapshot
The system MUST store payroll in `nominas`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), scalar `empleadoId?` (String, NO FK — MAY point at `Usuario.id` today, future `Empleado.id` later), `nombreEmpleado` String (REQUIRED snapshot, survives deactivation / login-less staff), optional `cargo`, `tipoVinculacion` `TipoVinculacion`, `periodo` String `'YYYY-MM'`, optional `fechaIngreso` (employee tenure), `salarioHonorarios` `Decimal(14,2)`, optional `auxilioTransporte` `Decimal(14,2)`, optional `bonificaciones` `Decimal(14,2)`, optional `descuentos` `Decimal(14,2)`, `valorNetoPagar` `Decimal(14,2)` (captured/frozen COP — NO SMMLV indexing), optional `fechaPago`, `estadoPago` `EstadoPagoNomina @default(PENDIENTE)`, scalar `cuentaId?` (NO FK, the paying bolsa) OR free-text `cuentaBancaria` String?, optional `comprobantePagoUrl` (URL only), optional `observaciones` (Text). It is a TENANT-SCOPED LEAF (NO Cascade FK; all references scalar). It MUST index `@@index([empresaId, periodo])`, `@@index([empresaId, empleadoId])`. The system MUST NOT introduce a contable `Empleado` entity; the snapshot makes the row self-contained.

#### Scenario: Payroll for a login-less staff member
- GIVEN a messenger who has NO `Usuario` login
- WHEN a `Nomina` is created with `empleadoId = null`, a required `nombreEmpleado`, `cargo`, and `tipoVinculacion`
- THEN the row is valid and self-contained (no seat consumed, no `Empleado` entity)

#### Scenario: Snapshot survives deactivation
- GIVEN a `Nomina` whose `empleadoId` points at a `Usuario` that is later deactivated/deleted
- WHEN the `Nomina` is read
- THEN `nombreEmpleado`/`cargo` still display (no FK, no SetNull cascade can blank them)

#### Scenario: valorNetoPagar is frozen COP
- GIVEN a `Nomina` for periodo `'2026-06'`
- WHEN the SMMLV later changes
- THEN `valorNetoPagar` is unchanged (captured COP, not indexed)

### Requirement: Enums TipoVinculacion, EstadoPagoNomina
The system MUST define `TipoVinculacion { LABORAL, PRESTACION_SERVICIOS, OTRO }` and `EstadoPagoNomina { PAGADO, PENDIENTE } @default(PENDIENTE)`. Additive; MUST NOT modify any existing enum.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoVinculacion` and `EstadoPagoNomina` exist with the listed members AND no existing enum is changed

### Requirement: empleadoId is validated same-empresa firm staff when set
When `empleadoId` is set, the system MUST validate it belongs to the same `empresa` and is firm staff (NOT a platform `ADMIN` with `empresaId = null`). The validation is app-level (`empleadoId` has NO Prisma FK). When `empleadoId` is null, only the snapshot fields are required.

#### Scenario: empleadoId of another empresa rejected
- GIVEN a user of despacho A creating a `Nomina`
- WHEN `empleadoId` references a `Usuario` of despacho B
- THEN the write is rejected (cross-tenant reference)

#### Scenario: platform ADMIN cannot be a payroll subject
- GIVEN `empleadoId` referencing a platform `ADMIN` (`empresaId = null`)
- WHEN the `Nomina` is created
- THEN it is rejected (not firm staff)

### Requirement: Tenancy and permiso gating mirror the clientes router
Every nómina endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `empleadoId`/`cuentaId` on CREATE/PATCH, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave (`contable.nomina.ver`/`.crear`/`.editar`). The `contable` módulo gate applies.

#### Scenario: Scoped by token empresaId
- GIVEN a user of despacho A
- WHEN they GET `/contable/nominas?periodo=2026-06`
- THEN only despacho A's rows are returned (hard `WHERE { empresaId }`)