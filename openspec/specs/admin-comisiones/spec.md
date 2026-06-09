# Admin — Comisiones Specification

> New capability introduced by change `admin-comercial-ventas`. One commission per won prospecto for
> the assigned COMERCIAL. Platform-level data scoped by salesperson; only ADMIN settles payment.

## ADDED Requirements

### Requirement: Comision generated on win
The system MUST store commissions in `comisiones`: `id` (cuid), `prospectoId` (unique, scalar no-FK,
1:1 with the won prospecto), `comercialId` (scalar no-FK → `Usuario`), `baseCalculo` `Decimal(10,2)`
(the negotiated sale price), optional `porcentaje` `Decimal(5,2)` (the applied rate snapshot; null
when a fixed amount was used), `monto` `Decimal(10,2)` (final commission), `estado` `EstadoComision`
(default `PENDIENTE`), optional `fechaPago`/`notas`, `createdAt`, `updatedAt`. A Comision MUST be
created by the win transaction, never directly. Enum `EstadoComision { PENDIENTE, PAGADA, ANULADA }`.

#### Scenario: Percentage commission from the salesperson's rate
- GIVEN a comercial with `porcentajeComision = 10`
- WHEN a prospecto is won with `precioVenta = 100000` and no fixed amount
- THEN a Comision is created with `baseCalculo = 100000`, `porcentaje = 10`, `monto = 10000`,
  `estado = PENDIENTE`

#### Scenario: Fixed-amount override
- GIVEN a win with `montoComisionFijo = 25000`
- WHEN the commission is generated
- THEN `monto = 25000` and `porcentaje = null`

#### Scenario: One commission per prospecto
- GIVEN a prospecto that already produced a commission
- WHEN the win action is retried
- THEN no second Comision is created (`prospectoId` is unique → 409)

### Requirement: Salesperson-scoped read, ADMIN-only settlement
`GET /comisiones` MUST return only the caller's own commissions when `rol = COMERCIAL` (hard
`where: { comercialId }`), and all (with optional `?estado`/`?comercialId` filters) for ADMIN.
`PATCH /comisiones/:id` (to `PAGADA` with `fechaPago`, or `ANULADA`) MUST require `rol = ADMIN`.

#### Scenario: COMERCIAL sees only their commissions
- GIVEN commissions for comerciales A and B
- WHEN A lists `/comisiones`
- THEN only A's commissions are returned

#### Scenario: COMERCIAL cannot mark paid
- WHEN a COMERCIAL PATCHes a commission to `PAGADA`
- THEN the API responds 403

#### Scenario: ADMIN marks a commission paid
- WHEN an ADMIN PATCHes a PENDIENTE commission to `PAGADA`
- THEN `estado = PAGADA` and `fechaPago` is set
