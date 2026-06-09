# Contable — Caja Menor Specification

> New capability introduced by change `contable-module`. Adds the `CajaMenor` petty-cash fund header (Cascade root for its movements) and `CajaMenorMovimiento` — the ONE satellite-of-satellite — with a derived running balance.

## ADDED Requirements

### Requirement: CajaMenor fund header (cascade root for its movements)
The system MUST store petty-cash funds in `cajas_menores`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), `nombre` String, `montoInicial` `Decimal(14,2)`, scalar `responsableId?` (NO FK), `estado` `EstadoCajaMenor @default(ACTIVA)`, optional `observaciones` (Text), `createdAt`, `updatedAt`. It MUST have a `movimientos CajaMenorMovimiento[]` back-relation and index `@@index([empresaId])`. The header is a TENANT-SCOPED LEAF (NO inbound Cascade FK); it is the Cascade ROOT for its movements. `saldoActual` MUST be DERIVED (= `montoInicial - SUM(SALIDA) + SUM(REPOSICION)`), NEVER stored. Multiple funds MAY exist per empresa.

#### Scenario: Open a petty-cash fund
- GIVEN a user holding `contable.cajamenor.crear` in despacho A
- WHEN they POST a `CajaMenor` with `nombre` and `montoInicial`
- THEN it is created `estado = ACTIVA` with `empresaId` from the token and NO stored saldoActual

### Requirement: CajaMenorMovimiento is the one satellite-of-satellite
The system MUST store movements in `caja_menor_movimientos`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), `cajaId` FK→`CajaMenor` (Cascade — the SOLE FK / cascade root), `fechaMovimiento` (default now), `tipoMovimiento` `TipoMovCaja @default(SALIDA)`, `concepto` String, `categoria` `CategoriaCajaMenor`, `valor` `Decimal(14,2)`, scalar `procesoId?` (NO FK), `radicado?` (snapshot), `medioSalida` `MetodoPago`, scalar `responsableId?` (NO FK), optional `soporteUrl` (URL only), optional `observaciones` (Text). It MUST index `@@index([cajaId, fechaMovimiento])`, `@@index([empresaId])`. `caja` is the ONLY relation FK (Cascade); every other reference is scalar with NO Prisma FK. `saldoRestante` MUST be a running balance DERIVED in the serializer ordered by `fechaMovimiento`, NEVER stored (no race condition).

#### Scenario: Movement cascades from its caja
- GIVEN a `CajaMenor` with several `CajaMenorMovimiento` rows
- WHEN the `CajaMenor` is deleted
- THEN its movements are removed via Cascade (the SOLE FK)

#### Scenario: saldoRestante derived as a running balance
- GIVEN a `CajaMenor` with `montoInicial = 500000`, a `SALIDA` of 100000, then a `REPOSICION` of 50000
- WHEN the movements are read in `fechaMovimiento` order
- THEN the serializer computes a running `saldoRestante` (400000, then 450000) and `saldoActual = 450000`, none of which is stored

### Requirement: Enums CategoriaCajaMenor, TipoMovCaja, EstadoCajaMenor
The system MUST define `CategoriaCajaMenor { TRANSPORTE, PAPELERIA, MENSAJERIA, ALIMENTACION, OTRO }`, `TipoMovCaja { SALIDA, REPOSICION } @default(SALIDA)`, and `EstadoCajaMenor { ACTIVA, CERRADA } @default(ACTIVA)`. Additive; MUST NOT modify any existing enum.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `CategoriaCajaMenor`, `TipoMovCaja`, and `EstadoCajaMenor` exist with the listed members AND no existing enum is changed

### Requirement: Tenancy and permiso gating mirror the clientes router
Every caja-menor endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `cajaId`/`procesoId`/`responsableId` on CREATE/PATCH, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave (`contable.cajamenor.ver`/`.crear`/`.editar`). The `contable` módulo gate applies.

#### Scenario: Cross-empresa caja rejected on movement create
- GIVEN a user of despacho A creating a `CajaMenorMovimiento`
- WHEN `cajaId` references a `CajaMenor` of despacho B
- THEN the write is rejected (cross-tenant reference)