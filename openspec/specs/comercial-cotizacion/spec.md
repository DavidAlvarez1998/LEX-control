# Comercial — Cotización (Offer) Specification

> New capability introduced by change `comercial-funnel`. Adds `Cotizacion`, the re-quotable proposal over the existing `Cliente`, carrying the OFFER cobro vocabulary (`FormaPago`). It drives the `propuesta-sin-respuesta` alert.

## ADDED Requirements

### Requirement: Cotizacion as a re-quotable proposal
The system MUST store quotes in `cotizaciones`: `id` (cuid), `empresaId` (denormalized, plain indexed column, NO FK — errno-150 avoided like `UsuarioRolEmpresa`), `clienteId` FK→`Cliente` (Cascade), `tipoServicio` (free text, no `Servicio` FK), optional `tipoProcesoId` FK→`TipoProceso` (SetNull, may be global), `valorCotizado` `Decimal(14,2)`, `formaPago` `FormaPago`, optional `porcentajeExito` `Decimal(5,2)`, optional `numeroCuotas` (Int), optional `fechaEnvio` (NULL = draft), optional `fechaRespuesta`, `estadoPropuesta` `EstadoPropuesta` (default `PENDIENTE`), optional `observaciones` (Text), optional `creadoPorId` FK→`Usuario` (SetNull), `createdAt`, `updatedAt`. Multiple cotizaciones per `cliente` MUST be allowed (re-quotes). It MUST index `@@index([clienteId])`, `@@index([empresaId, estadoPropuesta])`, `@@index([empresaId, fechaEnvio])`. Only `Cliente` cascades in (denormalized `empresaId` has NO FK; an Empresa delete reaches rows via the Cliente cascade); `tipoProcesoId` and `creadoPorId` MUST be `SetNull`.

#### Scenario: Create a draft quote
- GIVEN a user holding `comercial.cotizacion.crear` in despacho A
- WHEN they POST a cotizacion for a `Cliente` of A with `valorCotizado = 5000000.00`, `formaPago = CONTADO`, no `fechaEnvio`
- THEN it is created with `estadoPropuesta = PENDIENTE` and is treated as a draft (`fechaEnvio = null`)

#### Scenario: Re-quote allowed
- GIVEN a `Cliente` that already has a cotizacion
- WHEN a second cotizacion is created for the same `cliente`
- THEN both rows persist (no uniqueness constraint blocks the re-quote)

### Requirement: Enums FormaPago and EstadoPropuesta
The system MUST define `FormaPago { CONTADO, CUOTAS, CUOTALITIS, CUOTA_MIXTA, PRIMA_EXITO }` (the OFFER vocabulary) and `EstadoPropuesta { PENDIENTE, ENVIADA, ACEPTADA, RECHAZADA }`, additive and not modifying existing enums.

#### Scenario: Enums available and additive
- GIVEN a pushed database
- WHEN the schema is inspected
- THEN `FormaPago` and `EstadoPropuesta` exist with the listed members AND no existing enum is changed

### Requirement: Forma-de-pago conditional validation
The application MUST require `porcentajeExito` when `formaPago` is `CUOTALITIS`, `CUOTA_MIXTA`, or `PRIMA_EXITO`, and MUST require `numeroCuotas` when `formaPago` is `CUOTAS` or `CUOTA_MIXTA`. Money MUST use `Decimal(14,2)` COP and percentages `Decimal(5,2)`.

#### Scenario: CUOTALITIS without porcentaje rejected
- GIVEN a cotizacion with `formaPago = CUOTALITIS` and no `porcentajeExito`
- WHEN it is submitted
- THEN it is rejected

#### Scenario: CUOTAS without numeroCuotas rejected
- GIVEN a cotizacion with `formaPago = CUOTAS` and no `numeroCuotas`
- WHEN it is submitted
- THEN it is rejected

### Requirement: Tenancy and FK validation mirror the clientes router
Every cotizacion endpoint MUST take `empresaId` from the token, hard-filter by `WHERE { empresaId }`, run `assertSameEmpresa` on `clienteId`/`tipoProcesoId`/`creadoPorId` (allowing a global `TipoProceso` with `empresaId = null`), and be gated by `requireAuth` + a CONCRETE `requirePermiso` clave per action (`comercial.cotizacion.ver`/`.crear`/`.editar`). `requirePermiso` does NOT support wildcards (exact-clave lookup → 500 on a literal `*`); `comercial.cotizacion.*` is shorthand for that set.

#### Scenario: Cross-empresa tipoProceso rejected
- GIVEN a user of despacho A
- WHEN they set `tipoProcesoId` to a despacho-scoped `TipoProceso` of despacho B
- THEN the write is rejected; a global `TipoProceso` (`empresaId = null`) would be accepted