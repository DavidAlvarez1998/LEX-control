# Comercial — Contrato & Cobro Specification

> New capability introduced by change `comercial-funnel`. Adds `ContratoComercial` (contrato + poder doc tracks plus a denormalized cobro headline) and the authoritative 1:1 `ConfiguracionCobro` plan. This is storage of an AGREED plan, NOT a billing engine; the `ModalidadCobro` enum is shared with the future contable módulo.

## ADDED Requirements

### Requirement: ContratoComercial with two parallel doc tracks and a cobro headline
The system MUST store contracts in `contratos_comerciales`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like `UsuarioRolEmpresa`), `clienteId` FK→`Cliente` (Cascade), optional `cotizacionId` FK→`Cotizacion` (SetNull, provenance), `tipoContrato` `TipoContrato`, `fechaGeneracion` (default now), optional `fechaEnvio`, optional `fechaFirma`, `estadoContrato` `EstadoDocFirma` (default `PENDIENTE`), `estadoPoder` `EstadoDocFirma` (default `PENDIENTE`), `tipoCobroAcordado` `ModalidadCobro`, optional `valorAcordado` `Decimal(14,2)`, optional `porcentajeAcordado` `Decimal(5,2)`, optional `documentoContratoUrl`, optional `documentoPoderUrl`, optional `observaciones` (Text), optional `registradoPorId` FK→`Usuario` (SetNull), `createdAt`, `updatedAt`. It MUST index `@@index([clienteId])`, `@@index([empresaId, estadoContrato, fechaEnvio])`, `@@index([empresaId, estadoPoder])`. Only `Cliente` cascades in (denormalized `empresaId` has NO FK; an Empresa delete reaches rows via the Cliente cascade); `cotizacionId` and `registradoPorId` MUST be `SetNull`. The model MUST be named `ContratoComercial` (suffix) so a future contable `Contrato` cannot collide. Document URLs are path/string only; upload infrastructure is out of scope.

#### Scenario: Generate a contract with poder track
- GIVEN a user holding `comercial.contrato.crear` in despacho A
- WHEN they POST a `ContratoComercial` for a `Cliente` of A
- THEN it is created with `estadoContrato = PENDIENTE`, `estadoPoder = PENDIENTE`, and `empresaId` from the token

#### Scenario: Deleting the source cotizacion nulls provenance
- GIVEN a `ContratoComercial` whose `cotizacionId` points at a `Cotizacion`
- WHEN that `Cotizacion` is deleted
- THEN the contract survives with `cotizacionId = null`

### Requirement: Enums TipoContrato, EstadoDocFirma, ModalidadCobro
The system MUST define `TipoContrato { PRESTACION_SERVICIOS, MANDATO, OTRO }`, `EstadoDocFirma { PENDIENTE, ENVIADO, FIRMADO }` (used by both `estadoContrato` and `estadoPoder`), and `ModalidadCobro { CUOTALITIS, CUOTA_MIXTA, PRIMA_EXITO, FIJO, OTRO }` (the AGREED/binding vocabulary). `ModalidadCobro` MUST be a closed enum (a stable join key the future contable módulo reads), additive and not modifying existing enums.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `TipoContrato`, `EstadoDocFirma`, and `ModalidadCobro` exist with the listed members AND no existing enum is changed

### Requirement: ConfiguracionCobro is the authoritative 1:1 cobro plan
The system MUST store the structured agreed plan in `configuraciones_cobro`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like `UsuarioRolEmpresa`), `contratoId` `@unique` FK→`ContratoComercial` (Cascade — the config dies with the contract), `clienteId` (denormalized, NO FK — `contratoId` is the single cascade root), `modalidadCobro` `ModalidadCobro`, optional `valorFijo` `Decimal(14,2)`, optional `porcentajeExito` `Decimal(5,2)`, optional `numeroCuotas` (Int), optional `valorCuota` `Decimal(14,2)`, optional `fechaPrimerPago` (DUE date only), optional `condicionesEspeciales` (Text), `createdAt`, `updatedAt`. It MUST be 1:1 with `ContratoComercial` (`contratoId @unique`) and index `@@index([empresaId, fechaPrimerPago])`, `@@index([clienteId])`. It MUST be gated by `comercial.cobro.configurar` (writes) / `comercial.cobro.ver` (reads). `ConfiguracionCobro` MUST be authoritative for the PLAN; the `ContratoComercial.{tipoCobroAcordado, valorAcordado, porcentajeAcordado}` fields are a denormalized self-describing summary and `ConfiguracionCobro` MUST win on any conflict.

#### Scenario: One config per contract
- GIVEN a `ContratoComercial` that already has a `ConfiguracionCobro`
- WHEN a second config is created for the same `contratoId`
- THEN it is rejected by the `@unique` on `contratoId`

#### Scenario: Config dies with the contract
- GIVEN a `ContratoComercial` with a `ConfiguracionCobro`
- WHEN the contract is deleted
- THEN the `configuraciones_cobro` row is removed via Cascade

#### Scenario: Config wins on conflict with the headline
- GIVEN a contract whose headline `valorAcordado` differs from its `ConfiguracionCobro.valorFijo`
- WHEN the agreed plan is read by a consumer
- THEN `ConfiguracionCobro` is the authoritative source and the headline is treated as a stale summary

### Requirement: Comercial stores the cobro PLAN, not a billing engine (boundary)
The comercial módulo MUST store only the agreed cobro PLAN. There MUST be NO `Pago`/`Cuota`/`Recibo`/`Cartera`/`saldo` rows in `configuraciones_cobro` or any comercial table. `saldoPendiente`, `mora`, and cuotas-pagadas MUST be DERIVED or owned by the future contable módulo. `fechaPrimerPago` is the only forward-looking field comercial owns (a DUE date), used purely as the `cuota-inicial` alert heuristic until contable supplies payment truth.

#### Scenario: No payment rows in comercial
- GIVEN the pushed comercial schema
- WHEN the comercial tables are inspected
- THEN there is no `Pago`/`Cuota`/`Recibo`/`Cartera` table and `configuraciones_cobro` stores only plan inputs plus the `fechaPrimerPago` due date

### Requirement: Tenancy and FK validation mirror the clientes router
Every contrato/cobro endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `clienteId`/`cotizacionId`/`contratoId`/`registradoPorId`, and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave per action (`comercial.contrato.ver`/`.crear`/`.editar` for the contrato+poder state machine incl. FIRMADO; `comercial.cobro.ver`/`.configurar` for the cobro plan). `requirePermiso` does NOT support wildcards (exact-clave lookup → 500 on a literal `*`); the `.*` forms are shorthand for those sets.

#### Scenario: Cross-empresa cotizacion rejected on contract create
- GIVEN a user of despacho A creating a `ContratoComercial`
- WHEN `cotizacionId` references a `Cotizacion` of despacho B
- THEN the write is rejected (cross-tenant reference)