# Contable — Ingresos Specification

> New capability introduced by change `contable-module`. Adds the append-only `Ingreso` ledger of actual money RECEIVED, anchored on `Cliente` (sole Cascade root), and the enums it uses. This ledger is the input that RESOLVES comercial's derived `saldoPendiente`.

## ADDED Requirements

### Requirement: Ingreso append-only ledger of money received
The system MUST store received payments in `ingresos`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like the comercial satellites), `clienteId` FK→`Cliente` (Cascade — the SOLE FK / cascade root), scalar `procesoId?` (NO FK), `radicado?` (snapshot of `Proceso.radicado` at insert, report-by-radicado convenience), scalar `contratoId?` (NO FK, links the payment to the comercial contract), scalar `configuracionCobroId?` (NO FK, the plan row it applies against), scalar `cuentaId?` (NO FK, the bolsa that received it), `fechaIngreso` (default now), `conceptoPago` String, `tipoCobro` `TipoCobroIngreso`, `valorRecibido` `Decimal(14,2)`, `metodoPago` `MetodoPago`, `estadoPago` `EstadoPagoIngreso @default(PAGADO)`, optional `numeroComprobante`, optional `soportePagoUrl` (URL only), optional `observaciones` (Text), scalar `registradoPorId?` (NO FK). It MUST index `@@index([empresaId, fechaIngreso])`, `@@index([clienteId])`, `@@index([empresaId, procesoId])`, `@@index([empresaId, radicado])`, `@@index([configuracionCobroId])`, `@@index([empresaId, estadoPago])`. `cliente` is the ONLY relation FK (Cascade); every other reference is a SCALAR with NO Prisma FK. Multiple `Ingreso` rows MAY exist per `cliente` (append-only; never updated to mutate history of money received).

#### Scenario: Record a received payment
- GIVEN a user holding `contable.ingreso.crear` in despacho A
- WHEN they POST an `Ingreso` for a `Cliente` of A with `valorRecibido` and `metodoPago`
- THEN it is created with `empresaId` from the token, `estadoPago = PAGADO` by default, and `fechaIngreso = now`

#### Scenario: Cliente cascade reaches the ledger
- GIVEN a `Cliente` of A with several `Ingreso` rows
- WHEN that `Cliente` is deleted (or its `Empresa` is deleted, reaching it via the Cliente cascade)
- THEN its `ingresos` rows are removed via Cascade (the SOLE FK)

#### Scenario: radicado is snapshotted, not derived live
- GIVEN an `Ingreso` created against a `Proceso` whose `radicado` is later changed
- WHEN the `Ingreso` is read
- THEN it shows the `radicado` captured at insert (a frozen snapshot), not the live value

### Requirement: Enums TipoCobroIngreso, MetodoPago, EstadoPagoIngreso
The system MUST define `TipoCobroIngreso { ANTICIPO, CUOTA_INICIAL, HONORARIOS, PRIMA_EXITO, COSTAS, ABONO, OTRO }`, `MetodoPago { EFECTIVO, TRANSFERENCIA, CONSIGNACION, TARJETA, OTRO }` (shared by `Ingreso.metodoPago`, `Egreso.medioPago`, `CajaMenorMovimiento.medioSalida`), and `EstadoPagoIngreso { PAGADO, PENDIENTE, PARCIAL } @default(PAGADO)`. These are additive and MUST NOT modify any existing enum; `ModalidadCobro` from comercial MUST be REUSED, not redefined.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoCobroIngreso`, `MetodoPago`, and `EstadoPagoIngreso` exist with the listed members AND no existing enum (including `ModalidadCobro`) is changed

### Requirement: Tenancy and FK validation mirror the clientes router
Every ingreso endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `clienteId`/`procesoId`/`contratoId`/`configuracionCobroId`/`cuentaId`/`registradoPorId` on CREATE/PATCH, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave (`contable.ingreso.ver`/`.crear`/`.editar`). `requirePermiso` does NOT support wildcards (exact-clave lookup); the `.*` forms are shorthand. The `contable` módulo gate (403 "Módulo no contratado") applies and `esAdminEmpresa` does NOT bypass it.

#### Scenario: Cross-empresa cuenta rejected on ingreso create
- GIVEN a user of despacho A creating an `Ingreso`
- WHEN `cuentaId` references a `CuentaBancaria` of despacho B
- THEN the write is rejected (cross-tenant reference) by `assertSameEmpresa`

#### Scenario: Módulo not contracted blocks the endpoint
- GIVEN a despacho whose plan does NOT contract the `contable` módulo
- WHEN any user (even an `esAdminEmpresa` CLIENTE) calls `/contable/ingresos`
- THEN the request is rejected 403 "Módulo no contratado"