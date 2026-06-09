# Proposal: Facturación module (issue invoices to clients)

## Why
The despacho's commercial flow already runs end-to-end *up to recording incoming money*:
`Cliente → Seguimiento → Cotización → Contrato → ConfiguracionCobro (plan) → Ingreso → Cartera`.
The missing link is the **formal invoice** (`Factura`) the despacho issues to its client. Today the
client portal `/facturacion` page is a static placeholder (`const facturas = []`) and there is **no
`Factura` model and no endpoints** at all. Without it, a despacho can note that money came in
(`Ingreso`) but cannot issue an invoice, so the commercial→billing flow is not complete.

This change adds the Facturación module: create line-item invoices (with IVA), issue them with a
consecutive number, register payments that **reuse the existing `Ingreso`** (single source of money),
and derive the payment status — consistent with the accounting module's "derived balances"
philosophy (`Cartera = total − Σ Ingresos`).

## Decisions (confirmed with product)
- **Invoice shape**: line items (`descripcion`, `cantidad`, `valorUnitario`) + **subtotal / IVA / total**
  (Colombian-style). IVA percentage is per-invoice (default 19%).
- **Payment**: a payment is an **`Ingreso`** linked to the invoice via a new scalar `Ingreso.facturaId`.
  `pagado`, `saldo` and the PAGADA/PARCIAL status are **derived** from the linked ingresos — no separate
  payment entity, no double-counting of money (the same ingreso still feeds `Cartera`).
- **Origin**: an invoice can be created **from a signed contract** (prefilled cliente + cuota value from
  `ConfiguracionCobro`) **or manually** (pick cliente, type the items).

## Scope

### In Scope
- **Schema** (additive, `prisma db push`): `Factura` (+ `FacturaItem`) anchored to `Cliente` (Cascade);
  new `Ingreso.facturaId` scalar (no FK, app-validated); enum `EstadoFactura`.
- **API** `lex-control-api/src/modules/facturacion/` mounted at `/facturacion`: CRUD on drafts,
  emit (assign consecutive), anular, register payment (creates a linked `Ingreso`). Tenant-scoped
  (`empresaIdRequerido`, hard WHERE) + `requirePermiso` with concrete keys. Tests.
- **Client UI** `lex-control-client` `/facturacion`: list (with derived status), create-draft modal
  (cliente + items + IVA + vencimiento), invoice detail (items, totals, linked payments), emit /
  register-payment / anular actions, and a "facturar desde contrato" prefill.

### Out of Scope
- **PDF / print / "Descargar"**: deferred (a print view comes later). The list keeps the column but it
  is non-functional for now and `log`-noted in the UI.
- **DIAN electronic invoicing / CUFE / tax authority integration**: out of scope (this is an internal
  invoice document, not an e-invoice).
- **Admin (platform) UI**: none. These are the despacho's invoices to *its* clients → client portal only,
  exactly like the rest of the contable/comercial flow.
- **Recurring auto-billing / installment calendar**: the "cuota timeline" is a separate future change;
  here we only prefill a single invoice from the contract.

## Affected Areas
| Area | Impact |
|------|--------|
| `lex-control-api/prisma/schema.prisma` | `Factura`, `FacturaItem`, `EstadoFactura`; `Ingreso.facturaId` |
| `lex-control-api/src/modules/facturacion/` | New router + schemas (CRUD, emit, anular, pagos) |
| `lex-control-api/src/app.ts` | Mount `/facturacion` |
| roles/permisos catalog | New keys `facturacion.factura.ver` / `facturacion.factura.gestionar` granted to `ADMINISTRADOR` |
| `lex-control-client/src/app/(dashboard)/facturacion/page.tsx` | Wire to live API (replace placeholder) |
| `lex-control-api/tests/facturacion.test.ts` | New tests |

## Rollback Plan
Additive. Revert by dropping `facturas` + `factura_items` tables, the `EstadoFactura` enum, the
`Ingreso.facturaId` column, the `facturacion` module mount, and the permiso keys. No existing row
depends on the new column if unused. `Ingreso`/`Cartera` behavior is otherwise unchanged.

## Success Criteria
- [ ] Create a draft invoice with line items; subtotal/IVA/total computed correctly.
- [ ] Emit assigns a unique consecutive `FAC-YYYY-NNNN` per empresa; emitted invoices are immutable
      except for payments/anular.
- [ ] Registering a payment creates an `Ingreso` linked via `facturaId`; the invoice's `saldo` and
      status (PAGADA/PARCIAL/PENDIENTE/VENCIDA) are derived and match `Cartera`.
- [ ] An empresa can only see/act on its own invoices (tenant scope); a non-admin-empresa is rejected.
- [ ] `/facturacion` lists real invoices and supports create / emit / pay / anular.
- [ ] Tests + `tsc --noEmit` green for API and client.
