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
> MODIFIED by change `contable-nomina-desde-contrato` — this validation is now ACTIVELY enforced on both `POST` and `PATCH /contable/nominas` (rejecting `400`), because the client sends `empleadoId` when a nómina is prefilled from a contrato.

When `empleadoId` is set, the system MUST (on `POST` and `PATCH`) validate it belongs to the same `empresa` (token) and is firm staff (NOT a platform `ADMIN` with `empresaId = null`) before writing; otherwise it MUST reject with `400`. The validation is app-level (`empleadoId` has NO Prisma FK). When `empleadoId` is null, only the snapshot fields are required.

#### Scenario: empleadoId of another empresa rejected
- GIVEN a user of despacho A creating a `Nomina`
- WHEN `empleadoId` references a `Usuario` of despacho B
- THEN the write is rejected `400` (cross-tenant reference) and no `nomina.create` runs

#### Scenario: Valid same-empresa empleadoId accepted
- GIVEN a user of despacho A creating a `Nomina` with `empleadoId` of a despacho-A user
- WHEN the POST is processed
- THEN the row is created with `empresaId` from the token and the given `empleadoId`

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

### Requirement: empleables endpoint exposes minimal staff-with-contract for nómina prefill
> ADDED by change `contable-nomina-desde-contrato`.

The system MUST provide `GET /contable/nominas/empleables` returning the minimal projection of the firm's HR `Contrato` rows needed to prefill a `Nomina`: each item MUST contain ONLY `{ contratoId, usuarioId (nullable), nombre, cargo, honorarios, tipoContrato, fechaInicio, estado }`. It MUST hard-filter by the token `empresaId` (`WHERE { empresaId }`), MUST be gated by `requireAuth` + `requirePermiso('contable.nomina.crear')`, and the `contable` módulo gate applies. It MUST NOT expose the full `Contrato` (no `clausulas`, `penalidades`, `documentos`, `numeroDocumento`, etc.). It MUST NOT require granting `contrato.ver` to the CONTABLE role. It MUST return ALL contracts regardless of `estado` (and include `estado` in the projection) so the UI can default to vigentes (`ACTIVO`) yet still surface terminated/suspended contracts when a liquidación must be paid; the filtering by estado is a UI concern, not an API restriction.

#### Scenario: Contable lists employables without seeing full contracts
- GIVEN a user holding `contable.nomina.crear` in despacho A (no `contrato.ver`)
- WHEN they GET `/contable/nominas/empleables`
- THEN they receive despacho A's staff with only `{contratoId, usuarioId, nombre, cargo, honorarios, tipoContrato, fechaInicio, estado}`
- AND no clause / document / legal field of any contrato is included (the Prisma `select` never names them)

#### Scenario: Scoped by token empresaId
- GIVEN despacho A has contratos and despacho B has contratos
- WHEN a user of despacho A calls the endpoint
- THEN only despacho A's contratos are returned (hard `WHERE { empresaId }`)

#### Scenario: Login-less staff are employable
- GIVEN a despacho-A contrato whose `usuarioId` is null (messenger with no login)
- WHEN the endpoint is called
- THEN that person appears with `usuarioId = null` and a non-empty `nombre`

#### Scenario: Terminated contract still payable for liquidación
- GIVEN a despacho-A contrato with `estado = FINALIZADO`
- WHEN the endpoint is called
- THEN it is included in the response with `estado = FINALIZADO`
- AND the UI hides it by default but reveals it under "incluir finalizados (liquidación)"

### Requirement: Creating a nómina MAY prefill from a Contrato, copying values (not referencing)
> ADDED by change `contable-nomina-desde-contrato`.

When a `Nomina` is created from a selected contrato, the client MUST prefill ONLY these fields by **copying** the contrato's values at create time: `empleadoId` ← `Contrato.usuarioId`, `nombreEmpleado` ← `Contrato.nombreCompleto`, `cargo` ← `Contrato.cargo`, `fechaIngreso` ← `Contrato.fechaInicio`, `salarioHonorarios` ← `Contrato.honorarios`, and `tipoVinculacion` mapped from the free-text `Contrato.tipoContrato`. The system MUST NOT prefill `bonificaciones`, `descuentos` or `cuentaId` from the contrato (type/concept mismatch). All prefilled values MUST remain editable before submit. The created `Nomina` MUST hold no live reference to the contrato (the existing snapshot/no-FK requirements are unchanged); a later change to the contrato or deactivation of the person MUST NOT alter an already-created `Nomina`.

#### Scenario: Prefill the five clean fields
- GIVEN a contrato `{nombreCompleto:"Ana Ruiz", cargo:"Abogada", tipoContrato:"Laboral", fechaInicio:2025-02-01, honorarios:4.500.000, usuarioId:"u1"}`
- WHEN the contable picks it in the nómina form
- THEN the form shows `empleadoId=u1`, `nombreEmpleado="Ana Ruiz"`, `cargo="Abogada"`, `tipoVinculacion=LABORAL`, `fechaIngreso=2025-02-01`, `salarioHonorarios=4.500.000`
- AND `bonificaciones`, `descuentos`, `cuentaId` stay empty for manual entry

#### Scenario: tipoContrato maps to the closed enum with OTRO fallback
- GIVEN a contrato with `tipoContrato = "Prestación de servicios"`
- WHEN it prefills the nómina
- THEN `tipoVinculacion = PRESTACION_SERVICIOS`
- AND a contrato with `tipoContrato = "Freelance"` (or any unrecognized value) maps to `OTRO`

#### Scenario: Free-text name still works without a contrato (fallback)
- GIVEN a person with no registered contrato
- WHEN the contable types `nombreEmpleado` directly (no selection)
- THEN the nómina is created normally with `empleadoId = null` (existing behavior preserved)

#### Scenario: Snapshot is independent of the source contrato
- GIVEN a `Nomina` created by prefill from a contrato
- WHEN the contrato's `honorarios` is later changed or the person is deactivated
- THEN the existing `Nomina.salarioHonorarios` / `nombreEmpleado` are unchanged (values were copied, not referenced)