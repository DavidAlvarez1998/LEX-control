# Contable — Cartera Specification

> New capability introduced by change `contable-module`. Adds the THIN `Cartera` head per cobro plan that RESOLVES the comercial `saldoPendiente` placeholder: it snapshots `valorTotalAcordado` from the READ-only `ConfiguracionCobro`, derives `valorPagado`/`saldoPendiente` from the `Ingreso` ledger, and maintains only the indexable `estadoCartera` label.

## ADDED Requirements

### Requirement: Cartera is a thin head per cobro plan, anchored on Cliente
The system MUST store cartera heads in `cartera`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK), `clienteId` FK→`Cliente` (Cascade — the SOLE FK / cascade root), scalar `procesoId?` (NO FK), scalar `contratoId? @unique` (NO FK, ONE Cartera per contract), scalar `configuracionCobroId? @unique` (NO FK, the plan it tracks), optional `valorTotalAcordado` `Decimal(14,2)` (SNAPSHOT from `ConfiguracionCobro` at cartera-open), `tipoCobro` `ModalidadCobro` (REUSE the comercial enum, denormalized for display), optional `fechaProximoPago` (mirrors `ConfiguracionCobro.fechaPrimerPago`), `estadoCartera` `EstadoCartera @default(AL_DIA)`, scalar `responsableId?` (NO FK), optional `observaciones` (Text), `createdAt`, `updatedAt`. It MUST declare `@@unique([contratoId])`, `@@unique([configuracionCobroId])` and index `@@index([empresaId, estadoCartera])`, `@@index([clienteId])`, `@@index([empresaId, fechaProximoPago])`. `cliente` is the ONLY relation FK (Cascade); every other reference is scalar with NO Prisma FK. The grain is ONE head per contrato/plan (per-contrato head, NOT per (cliente, proceso)); `procesoId` is an attribute.

#### Scenario: Open a cartera for a signed contract
- GIVEN a `ContratoComercial` with its `ConfiguracionCobro` of despacho A
- WHEN a user holding `contable.cartera.ver` (ADMINISTRADOR) opens a `Cartera` for it
- THEN exactly one row is created with `contratoId`/`configuracionCobroId` set and `empresaId` from the token

#### Scenario: One cartera per contract
- GIVEN a `Cartera` already exists for a `contratoId`
- WHEN a second `Cartera` is created for the same `contratoId`
- THEN it is rejected by the `@@unique([contratoId])`

### Requirement: valorTotalAcordado is a snapshot from ConfiguracionCobro (read-only)
The system MUST snapshot `valorTotalAcordado` from the READ-only comercial `ConfiguracionCobro` at cartera-open and MUST NEVER write into comercial. The snapshot MUST be computed by `modalidadCobro`: `FIJO` → `valorFijo`; `CUOTALITIS`/`CUOTA_MIXTA` → `numeroCuotas * valorCuota` (+ `valorFijo` upfront if mixed); `PRIMA_EXITO` → contingent, NULLABLE until success (with `porcentajeExito` captured for reference); fallback `ContratoComercial.valorAcordado`. A later edit to `ConfiguracionCobro` MUST NOT silently move the snapshot; an explicit re-sync action re-reads the plan.

#### Scenario: Snapshot does not drift on plan edit
- GIVEN a `Cartera` with `valorTotalAcordado` snapshotted from a FIJO plan
- WHEN the source `ConfiguracionCobro.valorFijo` is later edited
- THEN the `Cartera.valorTotalAcordado` is unchanged until an explicit re-sync is invoked

#### Scenario: PRIMA_EXITO total is indeterminate
- GIVEN a `Cartera` whose plan `modalidadCobro = PRIMA_EXITO`
- WHEN the cartera is read before success
- THEN `valorTotalAcordado` is null and `saldoPendiente` reports `null`/'indeterminado', excluded from al_dia/vencido aggregation

### Requirement: valorPagado and saldoPendiente are derived; estadoCartera is the one maintained label
The system MUST DERIVE (never store) `valorPagado = SUM(Ingreso.valorRecibido WHERE configuracionCobroId matches OR (clienteId + procesoId match) AND estadoPago IN {PAGADO, PARCIAL})` and `saldoPendiente = valorTotalAcordado - valorPagado`. `estadoCartera` MAY be the ONE maintained column (a derived LABEL, not money), recomputed inside the SAME request on every `Ingreso` write: `PAGADO` if `saldoPendiente <= 0`; `PARCIAL` if `0 < valorPagado < total`; `VENCIDO` if `saldoPendiente > 0 AND fechaProximoPago < now`; `AL_DIA` otherwise. General/non-contract `Ingreso` (`configuracionCobroId = null`) MUST be EXCLUDED from cartera math (but INCLUDED in `totalIngresosMes`).

#### Scenario: Ingreso write recomputes the cartera label
- GIVEN a `Cartera` with `valorTotalAcordado = 1000000` and `estadoCartera = AL_DIA`
- WHEN an `Ingreso` of 1000000 (PAGADO) is recorded against its `configuracionCobroId`
- THEN in the same request `valorPagado = 1000000` (derived), `saldoPendiente = 0` (derived), and `estadoCartera` is recomputed to `PAGADO`

#### Scenario: General income excluded from cartera
- GIVEN an `Ingreso` with `configuracionCobroId = null`
- WHEN cartera `valorPagado` is computed
- THEN this income is NOT counted toward any cartera's `valorPagado` (it is general income, counted only in `totalIngresosMes`)

### Requirement: Enum EstadoCartera; contable is authoritative for saldoPendiente (read-only loop)
The system MUST define `EstadoCartera { AL_DIA, VENCIDO, PARCIAL, PAGADO } @default(AL_DIA)` (additive; `Cartera.tipoCobro` REUSES `ModalidadCobro`, NOT redefined). Contable MUST become AUTHORITATIVE for `saldoPendiente` by JOINING the READ-only comercial spine (`ConfiguracionCobro.contratoId → ContratoComercial.clienteId`; `Ingreso.clienteId` + optional `configuracionCobroId`). The comercial serializer's `saldoPendiente` placeholder MAY be backfilled via a shared contable helper or `GET /contable/cartera`. Every join MUST hard-filter `WHERE { empresaId }`.

#### Scenario: Enum available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `EstadoCartera` exists with the listed members AND `ModalidadCobro` is reused unchanged

#### Scenario: Contable resolves the comercial placeholder without writing comercial
- GIVEN a comercial `ContratoComercial` whose serializer `saldoPendiente` was a placeholder
- WHEN the contable cartera helper computes the saldo
- THEN it reads `ConfiguracionCobro`/`ContratoComercial` (never writes them) and returns the authoritative `saldoPendiente`

### Requirement: Tenancy and permiso gating (cartera gestión is ADMINISTRADOR-only)
Every cartera endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `clienteId`/`procesoId`/`contratoId`/`configuracionCobroId`/`responsableId` on CREATE/PATCH, and be gated by `requireAuth` + the CONCRETE `requirePermiso("contable.cartera.ver")` clave. Cartera gestión MUST be `[ADMINISTRADOR]` only (`soloAdmin`). The `contable` módulo gate applies.

#### Scenario: Cross-empresa configuracionCobro rejected
- GIVEN a user of despacho A opening a `Cartera`
- WHEN `configuracionCobroId` references a `ConfiguracionCobro` of despacho B
- THEN the write is rejected (cross-tenant reference)