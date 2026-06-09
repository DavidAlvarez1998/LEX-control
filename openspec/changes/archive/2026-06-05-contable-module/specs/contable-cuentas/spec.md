# Contable — Cuentas / Bolsas Specification

> New capability introduced by change `contable-module`. Adds `CuentaBancaria` (a bolsa bancaria/caja) as a tenant-scoped leaf that stores only `saldoInicial` and derives `saldoActual`; it is referenced by the scalar `cuentaId` on Ingreso/Egreso/Nomina/ServicioFijo.

## ADDED Requirements

### Requirement: CuentaBancaria bolsa stores only saldoInicial; saldoActual is derived
The system MUST store bolsas in `cuentas_bancarias`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), `entidadBancaria` String, `tipoCuenta` `TipoCuentaBancaria`, optional `numeroCuenta`, `nombreBolsa` String, `saldoInicial` `Decimal(14,2) @default(0)`, `estadoCuenta` `EstadoCuentaBancaria @default(ACTIVA)`, scalar `responsableId?` (NO FK), optional `observaciones` (Text), `createdAt`, `updatedAt`. It is a TENANT-SCOPED LEAF (NO Cascade FK). It MUST index `@@index([empresaId])`, `@@index([empresaId, estadoCuenta])`. It MUST store ONLY `saldoInicial`; `saldoActual` MUST be DERIVED at read-time and NEVER stored: `saldoActual = saldoInicial + SUM(Ingreso.valorRecibido WHERE cuentaId = this AND estadoPago = PAGADO) - SUM(Egreso.valorGasto WHERE cuentaId = this AND estadoGasto = PAGADO)` (optionally minus PAGADO `Nomina`/`ServicioFijo` linked by `cuentaId`). `CONCILIACION_PENDIENTE` is a manual flag.

#### Scenario: Open a bolsa
- GIVEN a user holding `contable.cuenta.crear` (ADMINISTRADOR) in despacho A
- WHEN they POST a `CuentaBancaria` with `entidadBancaria`, `tipoCuenta`, `nombreBolsa`, `saldoInicial`
- THEN it is created `estadoCuenta = ACTIVA` with `empresaId` from the token and NO stored saldoActual

#### Scenario: saldoActual derived from the ledgers
- GIVEN a bolsa with `saldoInicial = 1000000`, a PAGADO `Ingreso` of 500000 against it, and a PAGADO `Egreso` of 200000 against it
- WHEN the bolsa is read
- THEN `saldoActual = 1300000` is computed at read-time and is not a stored column

### Requirement: Enums TipoCuentaBancaria, EstadoCuentaBancaria
The system MUST define `TipoCuentaBancaria { AHORROS, CORRIENTE, CAJA }` and `EstadoCuentaBancaria { ACTIVA, INACTIVA, CONCILIACION_PENDIENTE } @default(ACTIVA)`. Additive; MUST NOT modify any existing enum.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoCuentaBancaria` and `EstadoCuentaBancaria` exist with the listed members AND no existing enum is changed

### Requirement: Delete is blocked while the bolsa is referenced
Because `cuentaId` is a scalar with NO Prisma FK (so the DB will not block it), the app MUST block deleting a `CuentaBancaria` while any `Ingreso`/`Egreso`/`Nomina`/`ServicioFijo`/`CajaMenorMovimiento` references it via `cuentaId` (the `Servicio onDelete: Restrict` spirit). `INACTIVA`/`CONCILIACION_PENDIENTE` is the soft-disable path.

#### Scenario: Cannot delete a bolsa with movements
- GIVEN a `CuentaBancaria` referenced by at least one `Ingreso.cuentaId`
- WHEN a delete is attempted
- THEN it is rejected (app-level Restrict) and the user is directed to set `estadoCuenta = INACTIVA`

### Requirement: Tenancy and permiso gating (cuenta config is ADMINISTRADOR-only)
Every cuenta endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `responsableId` on CREATE/PATCH, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave (`contable.cuenta.ver`/`.crear`/`.editar`). Cuenta configuration permisos MUST be `[ADMINISTRADOR]` only (`soloAdmin`). The `contable` módulo gate applies.

#### Scenario: CONTABLE rep cannot create a bolsa
- GIVEN a user holding `RolEmpresa.CONTABLE` (but not `ADMINISTRADOR`)
- WHEN they POST `/contable/cuentas`
- THEN the request is rejected (cuenta config is ADMINISTRADOR-only)