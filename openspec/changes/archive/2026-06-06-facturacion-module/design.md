# Design: Facturación module

## Architecture decisions

### 1. `Factura` anchored to `Cliente` (Cascade), money as snapshots
Follows the contable idiom exactly: `Cliente` is the cascade root (deleting a cliente removes its
invoices), `empresaId` is desnormalized **without FK**, all `...Id` references (`contratoId`,
`configuracionCobroId`, `procesoId`) are **scalar, no-FK, app-validated** against the same empresa.
Money is `Decimal(14,2)`. Table names snake_case via `@@map`; ids are `cuid()`.

`subtotal`, `valorIva`, `total` are **computed from the items on write and stored as a snapshot** on
the `Factura`. The items are the source of truth while the invoice is a draft; once emitted, the
invoice (header + items) is immutable. This mirrors how `Cartera.valorTotalAcordado` snapshots the plan.

### 2. Payment = `Ingreso` linked by `facturaId` (single money source)
We do **not** add a separate payment table. A payment is an `Ingreso` (the existing accounting
money-in entity) carrying a new scalar `facturaId`. Rationale:
- One source of money → no reconciliation drift between "factura paid" and `Cartera`.
- The same `Ingreso` keeps feeding `Cartera` (contract-level) and now also a `Factura` (invoice-level);
  they are two views over the same payments.

Derived per invoice (never stored):
```
pagado = Σ Ingreso.valorRecibido WHERE facturaId = factura.id   (estadoPago ∈ {PAGADO, PARCIAL})
saldo  = total − pagado
estadoPago(derived):
  ANULADA            if factura.estado = ANULADA
  PAGADA             else if pagado ≥ total
  PARCIAL            else if pagado > 0
  VENCIDA            else if factura.estado = EMITIDA and fechaVencimiento < today
  PENDIENTE          else if factura.estado = EMITIDA
  BORRADOR           else (factura.estado = BORRADOR)
```
`Factura.estado` (stored) is only the **issue lifecycle** the user controls: `BORRADOR → EMITIDA →
(ANULADA)`. Payment/overdue status is always derived, like `Cartera`.

### 3. Consecutive numbering assigned on EMIT, in a transaction
A draft has `numero = NULL`. Emitting assigns `FAC-<year>-<NNNN>` where `NNNN` is the next sequence
for `(empresaId, year)`. Computed inside the same `$transaction` as the state change to avoid races:
read the current max for the empresa+year (`numero LIKE 'FAC-<year>-%'`), increment, write. Unique
constraint `@@unique([empresaId, numero])` is the hard backstop (MySQL allows multiple NULLs, so drafts
don't collide). Year comes from the server clock at emit time.

### 4. New module `facturacion/`, mounted at `/facturacion`
A dedicated module (repo idiom: one concern = one module) rather than folding into `contable`. It
reuses `requireAuth`, `empresaIdRequerido`, hard `WHERE empresaId`, and `assertSameEmpresa`-style
guards for `clienteId`/`contratoId`/`cuentaId`. New permiso keys:
- `facturacion.factura.ver` — list/read
- `facturacion.factura.gestionar` — create/edit/emit/pay/anular

Granted to `RolEmpresa.ADMINISTRADOR` (matches the nav, where Facturación is `adminOnly`). Registered
in the same permiso catalog the other modules use.

### 5. "Facturar desde contrato" is a prefill, not a coupling
Creating from a contract just **prefills** the draft: cliente from the contract, and one line item with
`ConfiguracionCobro.valorCuota` (or `valorFijo`) as `valorUnitario`. The user can edit before saving.
No structural link is required beyond the optional `contratoId`/`configuracionCobroId` snapshots, so a
fully manual invoice is equally valid.

## Endpoints (`/facturacion`)
| Method | Path | Permiso | Notes |
|--------|------|---------|-------|
| GET | `/facturas?estado=&clienteId=` | `.ver` | List with derived `pagado/saldo/estadoPago` |
| GET | `/facturas/:id` | `.ver` | Header + items + linked ingresos |
| POST | `/facturas` | `.gestionar` | Create **draft** from `{ clienteId, items[], porcentajeIva?, fechaVencimiento?, contratoId?, configuracionCobroId?, procesoId? }` |
| PATCH | `/facturas/:id` | `.gestionar` | Edit a **draft only** (items, dates, IVA). 409 if not BORRADOR |
| DELETE | `/facturas/:id` | `.gestionar` | Delete a **draft only**. 409 if EMITIDA/ANULADA |
| POST | `/facturas/:id/emitir` | `.gestionar` | Assign consecutive, set EMITIDA (immutable thereafter). 409 if no items / already emitted |
| POST | `/facturas/:id/anular` | `.gestionar` | `{ motivo }` → ANULADA. Allowed from EMITIDA |
| POST | `/facturas/:id/pagos` | `.gestionar` | Create a linked `Ingreso` `{ valorRecibido, metodoPago, fechaIngreso?, cuentaId?, tipoCobro?, numeroComprobante? }`; sets `facturaId`. Only on EMITIDA |

Validation: amounts > 0; `cantidad ≥ 1`; `clienteId`/`contratoId`/`cuentaId` must belong to the empresa
(else 404, existence not revealed); a payment cannot exceed `saldo` (configurable — reject overpayment
with 400) — **decision: reject overpayment** to keep `pagado ≤ total`.

## Data model (additions)
```prisma
enum EstadoFactura { BORRADOR EMITIDA ANULADA }

model Factura {
  id                   String        @id @default(cuid())
  empresaId            String        // desnorm, no FK (Cliente is the root)
  clienteId            String
  contratoId           String?       // scalar, no FK
  configuracionCobroId String?       // scalar, no FK
  procesoId            String?       // scalar, no FK
  radicado             String?       // snapshot
  numero               String?       // NULL while BORRADOR; 'FAC-YYYY-NNNN' on emit
  fechaEmision         DateTime?     // set on emit
  fechaVencimiento     DateTime?
  estado               EstadoFactura @default(BORRADOR)
  subtotal             Decimal       @db.Decimal(14, 2) @default(0)
  porcentajeIva        Decimal       @db.Decimal(5, 2)  @default(19)
  valorIva             Decimal       @db.Decimal(14, 2) @default(0)
  total                Decimal       @db.Decimal(14, 2) @default(0)
  observaciones        String?       @db.Text
  motivoAnulacion      String?       @db.Text
  registradoPorId      String?       // scalar, no FK
  createdAt            DateTime      @default(now())
  updatedAt            DateTime      @updatedAt

  cliente Cliente       @relation(fields: [clienteId], references: [id], onDelete: Cascade)
  items   FacturaItem[]

  @@unique([empresaId, numero])
  @@index([empresaId, estado])
  @@index([clienteId])
  @@index([empresaId, fechaEmision])
  @@map("facturas")
}

model FacturaItem {
  id            String  @id @default(cuid())
  empresaId     String  // desnorm
  facturaId     String
  descripcion   String
  cantidad      Int     @default(1)
  valorUnitario Decimal @db.Decimal(14, 2)
  total         Decimal @db.Decimal(14, 2) // cantidad * valorUnitario (snapshot)
  orden         Int     @default(0)

  factura Factura @relation(fields: [facturaId], references: [id], onDelete: Cascade)

  @@index([facturaId])
  @@map("factura_items")
}

// On Ingreso, add:
//   facturaId String?  // scalar, no FK; app-validated same empresa+cliente
//   @@index([facturaId])
```

## Risks / mitigations
- **Race on consecutive number** → assign inside `$transaction` + `@@unique([empresaId, numero])` backstop.
- **Overpayment / negative saldo** → reject a payment that exceeds `saldo` (400).
- **Editing an emitted invoice** → guarded: PATCH/DELETE only on BORRADOR (409 otherwise).
- **Double money counting** → none: a payment is an `Ingreso`; `facturaId` is just an extra link, it does
  not change how `Cartera` already sums ingresos.
