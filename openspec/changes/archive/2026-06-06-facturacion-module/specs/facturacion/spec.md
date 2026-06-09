# Facturación Specification

> New capability introduced by change `facturacion-module`. A despacho (empresa) issues line-item
> invoices to its own clients from the client portal. Invoices reuse the accounting `Ingreso` as the
> single source of payments; balances and payment status are derived. Tenant-scoped: empresa is always
> resolved from the token, never from the client.

## ADDED Requirements

### Requirement: Tenant Scope and Authorization
All `/facturacion` endpoints MUST be restricted to an authenticated user holding the relevant permiso
(`facturacion.factura.ver` for reads, `facturacion.factura.gestionar` for writes), and MUST act only on
the requester's own `Empresa` (resolved from the token). Any `clienteId`, `contratoId`, or `cuentaId`
supplied MUST belong to that empresa or the request is rejected.

#### Scenario: User without the permiso is rejected
- GIVEN an authenticated USUARIO without `facturacion.factura.gestionar`
- WHEN they POST `/facturacion/facturas`
- THEN the response status is 403

#### Scenario: Cross-empresa reference is rejected
- GIVEN an empresa admin of company A and a cliente of company B
- WHEN they POST an invoice with that `clienteId`
- THEN the response status is 404 (existence not revealed) and no invoice is created

#### Scenario: List returns only own empresa invoices
- GIVEN invoices exist for companies A and B
- WHEN an admin of company A GETs `/facturacion/facturas`
- THEN only company A's invoices are returned

### Requirement: Create Draft Invoice with Line Items
`POST /facturacion/facturas` MUST create a `Factura` in `BORRADOR` state with at least one line item,
computing `subtotal = Σ(item.cantidad × item.valorUnitario)`, `valorIva = round(subtotal × porcentajeIva/100)`,
and `total = subtotal + valorIva`. A draft MUST NOT be assigned a `numero`.

#### Scenario: Valid draft totals
- GIVEN an empresa admin and a valid `clienteId`
- WHEN they POST items `[{descripcion, cantidad: 1, valorUnitario: 1000000}]` with `porcentajeIva: 19`
- THEN the invoice is created with `estado = BORRADOR`, `numero = null`
- AND `subtotal = 1000000`, `valorIva = 190000`, `total = 1190000`

#### Scenario: Reject empty or invalid items
- GIVEN an empresa admin
- WHEN they POST with no items, or an item with `valorUnitario ≤ 0` or `cantidad < 1`
- THEN the response status is 400 and no invoice is created

#### Scenario: Prefill from a contract is optional
- GIVEN an empresa admin and a signed contract with a `ConfiguracionCobro`
- WHEN they create an invoice passing `contratoId`/`configuracionCobroId`
- THEN those values are stored as snapshots on the invoice
- AND a fully manual invoice (no contrato) is equally valid

### Requirement: Edit / Delete Only While Draft
`PATCH` and `DELETE` `/facturacion/facturas/:id` MUST succeed only while the invoice is `BORRADOR`,
recomputing totals on edit. An emitted or annulled invoice MUST be immutable (except payments and
annulment).

#### Scenario: Edit a draft recomputes totals
- GIVEN a BORRADOR invoice
- WHEN the admin PATCHes its items
- THEN `subtotal`, `valorIva`, and `total` are recomputed from the new items

#### Scenario: Cannot edit an emitted invoice
- GIVEN an EMITIDA invoice
- WHEN the admin PATCHes or DELETEs it
- THEN the response status is 409 and nothing changes

### Requirement: Emit Assigns a Unique Consecutive Number
`POST /facturacion/facturas/:id/emitir` MUST transition a `BORRADOR` invoice to `EMITIDA`, set
`fechaEmision`, and assign a `numero` of the form `FAC-<year>-<NNNN>` that is unique and consecutive per
`(empresa, year)`. It MUST reject an invoice with no items or one already emitted.

#### Scenario: Consecutive per empresa and year
- GIVEN company A has no invoices emitted this year
- WHEN the admin emits a draft
- THEN it receives `numero = FAC-<year>-0001`
- AND emitting the next draft yields `FAC-<year>-0002`

#### Scenario: Cannot emit an empty or already-emitted invoice
- GIVEN a BORRADOR with zero items, OR an already-EMITIDA invoice
- WHEN the admin emits it
- THEN the response status is 409

### Requirement: Register Payment Reusing Ingreso
`POST /facturacion/facturas/:id/pagos` MUST record a payment by creating an `Ingreso` linked to the
invoice via `facturaId`, only on an `EMITIDA` invoice, and MUST reject a payment that would make the
total paid exceed the invoice `total`.

#### Scenario: Payment links an Ingreso and updates derived status
- GIVEN an EMITIDA invoice with `total = 1190000` and no payments
- WHEN the admin posts a payment of `1190000`
- THEN an `Ingreso` is created with `facturaId` equal to the invoice and `valorRecibido = 1190000`
- AND the invoice's derived `pagado = 1190000`, `saldo = 0`, and derived status is `PAGADA`

#### Scenario: Partial payment
- GIVEN an EMITIDA invoice with `total = 1190000`
- WHEN the admin posts a payment of `500000`
- THEN the derived status is `PARCIAL` with `saldo = 690000`

#### Scenario: Overpayment is rejected
- GIVEN an EMITIDA invoice with `saldo = 690000`
- WHEN the admin posts a payment of `800000`
- THEN the response status is 400 and no `Ingreso` is created

#### Scenario: Cannot pay a draft or annulled invoice
- GIVEN a BORRADOR or ANULADA invoice
- WHEN the admin posts a payment
- THEN the response status is 409

### Requirement: Derived Payment Status
Every invoice returned by the API MUST include derived `pagado`, `saldo`, and `estadoPago`
(`BORRADOR | PENDIENTE | PARCIAL | PAGADA | VENCIDA | ANULADA`) computed from the linked ingresos and the
due date — never stored. `VENCIDA` applies only to an `EMITIDA` invoice past `fechaVencimiento` with
`saldo > 0`.

#### Scenario: Overdue derivation
- GIVEN an EMITIDA invoice with `fechaVencimiento` in the past and `saldo > 0`
- WHEN it is listed or read
- THEN its derived `estadoPago` is `VENCIDA`

#### Scenario: Paid never shows overdue
- GIVEN an EMITIDA invoice fully paid (`saldo = 0`) past its due date
- WHEN it is listed
- THEN its derived `estadoPago` is `PAGADA` (not `VENCIDA`)

### Requirement: Annul an Invoice
`POST /facturacion/facturas/:id/anular` MUST set an `EMITIDA` invoice to `ANULADA` with a `motivo`,
after which its derived status is `ANULADA` regardless of payments.

#### Scenario: Annul an emitted invoice
- GIVEN an EMITIDA invoice
- WHEN the admin posts `/anular` with a `motivo`
- THEN `estado = ANULADA`, `motivoAnulacion` is stored, and the derived status is `ANULADA`
