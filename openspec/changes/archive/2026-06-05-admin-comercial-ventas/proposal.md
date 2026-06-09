# Proposal — admin-comercial-ventas

## Why

LEX Control needs to sell **itself** (its Planes/subscriptions) to law firms. Today the only
commercial module is the CLIENT-side funnel (`comercial-funnel`): a despacho selling legal services
to *its* clientes. This change adds the **platform's own sales pipeline**: the LEX Control team
capturing leads (prospect companies), working them through a funnel, closing a plan sale, and paying
the salesperson a commission.

This is a distinct concern from `comercial-funnel` (different audience, different anchor entity) and
lives entirely in the **admin** app + platform-level data (no `empresaId` tenancy — this is LEX
Control's own data, scoped by the assigned salesperson).

## What changes

- **New platform role `COMERCIAL`** (added to the `Rol` enum next to `ADMIN`/`USUARIO`). A COMERCIAL
  is platform staff (`empresaId = null`) who sells plans. `Usuario` gains `porcentajeComision`
  (per-person commission rate, only meaningful for COMERCIAL).
- **`Prospecto`** — a prospect company (lead): contact data, **canal de entrada** (how it arrived),
  plan of interest, assigned comercial, and a funnel **estado** (NUEVO → CONTACTADO → COTIZADO →
  NEGOCIACION → GANADO / PERDIDO). On **GANADO** it snapshots the sale (plan sold, negotiated price,
  close date) and links the created `Empresa`.
- **`Comision`** — one per won prospecto: base (negotiated price), applied % (snapshot of the
  comercial's rate) or a manual fixed amount, final monto, and a payment lifecycle
  (PENDIENTE → PAGADA / ANULADA) the ADMIN settles by hand (no payments backend yet).
- **Win → conversion**: closing a prospecto as GANADO creates the **Empresa + Suscripcion** (plan
  sold) and generates the **Comision** in one transaction — no double data capture.
- **Access**: COMERCIAL sees/works only **their assigned** prospectos and **their** comisiones;
  ADMIN sees everything, assigns/reassigns prospectos, configures each comercial's rate, and marks
  comisiones paid.
- **Endpoints** mounted at `/prospectos` and `/comisiones` (guarded by `requireRole`).
- **Admin UI**: new nav `Prospectos` (funnel board/list + create + advance + win/lose) and
  `Comisiones` (list + mark paid), plus `rol = COMERCIAL` and `porcentajeComision` in the Usuarios
  screen.

## Decisions (confirmed with product)

- Commission rate is **per comercial** (variable per person), applied to the **negotiated** sale
  price; a **fixed amount** can override it per sale. Generated **on win**, PENDIENTE → PAGADA by
  hand (facturación/pagos is deferred, so no payment-triggered accrual).
- Sale price is **negotiable** per prospecto (defaults to the plan's `precioMensual`); commission is
  computed on the negotiated price.
- Prospectos are **assigned to one comercial** (ADMIN distributes); not a shared pool.
- Build **complete** (prospectos + role + comisiones + canal) in one change.

## Impact

- **Schema** (additive, `prisma db push`): `Rol += COMERCIAL`; `Usuario.porcentajeComision`; new
  `Prospecto`, `Comision`; new enums `CanalEntrada`, `EstadoProspecto`, `EstadoComision`. References
  to `Plan`/`Usuario`/`Empresa` are scalar **no-FK, app-validated** (repo idiom; platform data, not
  tenant-cascaded). The one real FK is `Prospecto.empresaId → Empresa` (`SetNull`) for the converted
  firm.
- **API** (`lex-control-api`): new `modules/ventas/` (prospectos + comisiones routers), mounted in
  `app.ts`. Reuses `requireRole`. The win-transaction creates Empresa + Suscripcion.
- **Admin** (`lex-control-admin`): new pages + nav; Usuarios screen extended.
- **No change** to the client portal or to `comercial-funnel`.

## Rollback

`prisma db push` is additive. Rollback = drop `prospectos`, `comisiones` + the 3 new enums, remove
`COMERCIAL` from `Rol` and `porcentajeComision` from `usuarios` (no rows depend on them if unused).
