# Tasks: Facturación module

## Phase 1 — Schema (`lex-control-api`)  ✅ APPLIED
- [x] 1.1 `schema.prisma`: add `enum EstadoFactura { BORRADOR EMITIDA ANULADA }`
- [x] 1.2 `schema.prisma`: add `model Factura` (anchored to `Cliente` Cascade; `@@unique([empresaId, numero])`; indexes) per design
- [x] 1.3 `schema.prisma`: add `model FacturaItem` (Cascade from `Factura`)
- [x] 1.4 `schema.prisma`: add `Ingreso.facturaId String?` scalar (no FK) + `@@index([facturaId])`; add `facturas Factura[]` back-relation on `Cliente`
- [x] 1.5 `pnpm push` + `pnpm generate`

## Phase 2 — API (`modules/facturacion/`)  ✅ APPLIED
- [x] 2.1 `facturacion.schemas.ts`: zod schemas (create draft, patch, emitir, anular, pago)
- [x] 2.2 `facturacion.router.ts`: GET list (+ derived `pagado/saldo/estadoPago`), GET detail (items + ingresos)
- [x] 2.3 POST create draft (compute subtotal/IVA/total from items), PATCH/DELETE draft-only (409 guard)
- [x] 2.4 POST `/emitir` — consecutive `FAC-YYYY-NNNN` per empresa+year inside `$transaction` (+ unique backstop)
- [x] 2.5 POST `/pagos` — create linked `Ingreso` (set `facturaId`), reject overpayment (400), EMITIDA-only (409)
- [x] 2.6 POST `/anular` — EMITIDA → ANULADA with `motivo`
- [x] 2.7 Tenant scope helpers: hard `WHERE empresaId`, assert cliente/contrato/cuenta same-empresa
- [x] 2.8 Mount `/facturacion` in `app.ts`
- [x] 2.9 Permisos: register `facturacion.factura.ver` / `.gestionar`, grant to `ADMINISTRADOR` + `CONTABLE` (seeded → 44 permisos)

## Phase 3 — Tests (`tests/facturacion.test.ts`)  ✅ 20 tests, suite 194 green
- [x] 3.1 Create draft → totals (subtotal/IVA/total) correct; reject empty/invalid items (400)
- [x] 3.2 Emit → consecutive per empresa+year; reject empty/already-emitted (409)
- [x] 3.3 Edit/delete draft-only (409 on EMITIDA)
- [x] 3.4 Payment creates linked Ingreso; PARCIAL/PAGADA derived; overpayment 400; pay draft/anulada 409
- [x] 3.5 Derived status: VENCIDA past due with saldo>0; paid never VENCIDA
- [x] 3.6 Tenant scope: missing permiso 403; module gate 403; (cross-empresa cliente 404 covered by create 404)
- [x] 3.7 Anular → ANULADA + motivo

## Phase 4 — Client UI (`/facturacion`)  ✅ APPLIED (4.4 deferred)
- [x] 4.1 Replace placeholder: list real invoices (numero/cliente/fecha/total/saldo + derived estado badge), under `AdminEmpresaGuard`
- [x] 4.2 "Nueva factura" modal: pick cliente, add/remove items, IVA %, vencimiento → create draft; live subtotal/IVA/total preview (`formatMoney`/`MoneyInput`)
- [x] 4.3 Invoice detail modal: items + totals + linked payments; actions Emitir / Registrar pago / Anular (`ConfirmDialog` for emit/anular)
- [ ] 4.4 "Facturar desde contrato" prefill — DEFERRED (manual create shipped; prefill is a follow-up)
- [x] 4.5 "Descargar" omitted for now (PDF deferred) — replaced by "Ver" detail action

## Phase 5 — Verify
- [x] 5.1 `pnpm test` green (API) — 194 passing
- [x] 5.2 `tsc --noEmit` clean (API + client); client `pnpm build` succeeds (`/facturacion` route built)
- [x] 5.3 Live smoke (2026-06-06, automated against running :4000): draft → emit (FAC-2026-0001) → partial pay (PARCIAL, saldo 690.000) → overpay rejected (400) → full pay (PAGADA, saldo 0); 14/14 checks green

## Out of scope (future changes)
- [ ] PDF / print view + working "Descargar"
- [ ] Installment calendar (cuotas timeline) linking each Ingreso to a specific cuota
- [ ] DIAN electronic invoice (CUFE) integration
