# Contable — Egresos Specification

> New capability introduced by change `contable-module`. Adds the append-only `Egreso` ledger of money PAID OUT (GENERAL overhead or POR_PROCESO costs/costas) as a tenant-scoped leaf with NO Cascade FK, plus its enums and the no-double-counting doctrine.

## ADDED Requirements

### Requirement: Egreso append-only ledger as a tenant-scoped leaf
The system MUST store outgoing payments in `egresos`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), `tipoGasto` `TipoGastoEgreso`, scalar `clienteId?` (NO FK), scalar `procesoId?` (NO FK), `radicado?` (snapshot), scalar `cuentaId?` (NO FK), `fechaGasto` (default now), `categoriaGasto` `CategoriaEgreso`, optional `subcategoria`, `descripcionGasto` String, `valorGasto` `Decimal(14,2)`, `medioPago` `MetodoPago`, `estadoGasto` `EstadoGastoEgreso @default(PAGADO)`, scalar `responsableId?` (NO FK), optional `soporteGastoUrl` (URL only), optional `observaciones` (Text), scalar `registradoPorId?` (NO FK). Because a `GENERAL` egreso has no cliente, the table is a TENANT-SCOPED LEAF: it has NO Cascade FK at all (all references are scalars), isolated solely by the hard `WHERE { empresaId }`. It MUST index `@@index([empresaId, fechaGasto])`, `@@index([empresaId, categoriaGasto])`, `@@index([empresaId, radicado])`, `@@index([empresaId, procesoId])`.

#### Scenario: Record a general overhead expense
- GIVEN a user holding `contable.egreso.crear` in despacho A
- WHEN they POST an `Egreso` with `tipoGasto = GENERAL` and no `clienteId`/`procesoId`
- THEN it is created with `empresaId` from the token and `estadoGasto = PAGADO` by default

#### Scenario: Leaf has no cascade FK
- GIVEN the pushed schema
- WHEN the `egresos` table is inspected
- THEN it has NO Cascade foreign key (every reference — clienteId/procesoId/cuentaId/responsableId/registradoPorId — is a plain scalar with NO Prisma FK); rows are scoped only by `empresaId`

### Requirement: Enums TipoGastoEgreso, CategoriaEgreso, EstadoGastoEgreso
The system MUST define `TipoGastoEgreso { GENERAL, POR_PROCESO }`, `CategoriaEgreso { NOMINA, SERVICIOS, PAPELERIA, CAJA_MENOR, COSTAS, ARRIENDO, IMPUESTOS, HONORARIOS_TERCEROS, OTRO }`, and `EstadoGastoEgreso { PAGADO, PENDIENTE } @default(PAGADO)`. Additive; MUST NOT modify any existing enum.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoGastoEgreso`, `CategoriaEgreso`, and `EstadoGastoEgreso` exist with the listed members AND no existing enum is changed

### Requirement: Egreso holds only costs not covered by the typed expense tables (no double-count)
The `Egreso` ledger MUST hold ONLY `GENERAL` overhead + `POR_PROCESO` costs that are NOT already represented in `Nomina`, `CajaMenor`/`CajaMenorMovimiento`, or `ServicioFijo`. The system MUST NOT emit a settling-Egreso row when a Nomina/CajaMenor/ServicioFijo is paid. The monthly report MUST sum the 4 source tables SEPARATELY (one documented doctrine) to avoid double-counting.

#### Scenario: Paying a Nomina does not create an Egreso
- GIVEN a `Nomina` row marked `estadoPago = PAGADO`
- WHEN the payment is recorded
- THEN NO corresponding `Egreso` row is emitted (the Nomina table is summed independently in the report)

#### Scenario: Per-proceso cost recorded as Egreso
- GIVEN a litigation cost (e.g. a peritaje) not covered by a typed table
- WHEN it is recorded
- THEN it is an `Egreso` with `tipoGasto = POR_PROCESO`, `categoriaGasto` set, and a `procesoId` scalar

### Requirement: Tenancy and FK validation mirror the clientes router
Every egreso endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `clienteId`/`procesoId`/`cuentaId`/`responsableId`/`registradoPorId` on CREATE/PATCH, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave (`contable.egreso.ver`/`.crear`/`.editar`). The `contable` módulo gate applies and `esAdminEmpresa` does NOT bypass it.

#### Scenario: Cross-empresa proceso rejected on egreso create
- GIVEN a user of despacho A creating a POR_PROCESO `Egreso`
- WHEN `procesoId` references a `Proceso` of despacho B
- THEN the write is rejected (cross-tenant reference)