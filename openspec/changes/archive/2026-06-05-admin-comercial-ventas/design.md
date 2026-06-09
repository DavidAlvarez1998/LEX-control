# Design — admin-comercial-ventas

## Data model (additive)

```prisma
enum Rol { ADMIN  USUARIO  COMERCIAL } // + COMERCIAL

enum CanalEntrada { WEB  WHATSAPP  DIRECTO  REFERIDO  LLAMADA  REDES_SOCIALES  OTRO }
enum EstadoProspecto { NUEVO  CONTACTADO  COTIZADO  NEGOCIACION  GANADO  PERDIDO }
enum EstadoComision { PENDIENTE  PAGADA  ANULADA }

// Usuario += porcentajeComision Decimal(5,2)?  (solo aplica a COMERCIAL)

model Prospecto {
  id             String   @id @default(cuid())
  nombreEmpresa  String
  nombreContacto String
  email          String?
  telefono       String?
  cargo          String?
  canalEntrada   CanalEntrada    @default(DIRECTO)
  estado         EstadoProspecto @default(NUEVO)
  planInteresId  String?  // scalar no-FK -> Plan (app-validated)
  comercialId    String?  // scalar no-FK -> Usuario COMERCIAL (assigned)
  // Snapshot del cierre (cuando GANADO):
  planVendidoId  String?  // scalar no-FK -> Plan
  precioVenta    Decimal? @db.Decimal(10, 2) // negociado; default = Plan.precioMensual
  fechaCierre    DateTime?
  empresaId      String?  @unique // FK real -> Empresa creada al ganar (SetNull)
  empresa        Empresa? @relation(fields: [empresaId], references: [id], onDelete: SetNull)
  motivoPerdida  String?  @db.Text
  notas          String?  @db.Text
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  @@index([comercialId, estado])
  @@index([estado])
  @@index([canalEntrada])
  @@map("prospectos")
}

model Comision {
  id          String   @id @default(cuid())
  prospectoId String   @unique // scalar no-FK (1:1 con la venta ganada)
  comercialId String   // scalar no-FK -> Usuario
  baseCalculo Decimal  @db.Decimal(10, 2) // = precioVenta
  porcentaje  Decimal? @db.Decimal(5, 2)  // % aplicado (snapshot); null si monto fijo
  monto       Decimal  @db.Decimal(10, 2) // comisión final
  estado      EstadoComision @default(PENDIENTE)
  fechaPago   DateTime?
  notas       String?  @db.Text
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  @@index([comercialId, estado])
  @@map("comisiones")
}
```

`Empresa` gains the back-relation `prospecto Prospecto?`. Nothing else on existing models changes
besides the `Rol` enum value and `Usuario.porcentajeComision`.

### Why scalar no-FK for plan/comercial refs
Same idiom as `contable`/`comercial`: avoids multiple-relation clutter and errno-150, and these are
app-validated on write. This is **platform** data (not tenant-scoped), so there is no empresa-cascade
to honor. The only real FK is `empresaId` (1:1 to the converted firm) so deleting an Empresa nulls
the link rather than orphaning a dangling id.

## Win transaction (POST /prospectos/:id/ganar)

Body: `{ planId?, precioVenta?, montoComisionFijo? }` (planId defaults to `planInteresId`;
precioVenta defaults to the plan's `precioMensual`).

In a single `prisma.$transaction`:
1. Validate prospecto is not already GANADO; validate plan exists; require a `comercialId` assigned.
2. Create `Empresa { nombre: nombreEmpresa, email, telefono }`.
3. Create `Suscripcion { empresaId, planId, estado: ACTIVA }`.
4. Update prospecto → `estado: GANADO`, `planVendidoId`, `precioVenta`, `fechaCierre: now`, `empresaId`.
5. Compute commission: `comercial = Usuario(comercialId)`; if `montoComisionFijo` given →
   `monto = montoComisionFijo, porcentaje = null`; else `porcentaje = comercial.porcentajeComision ?? 0`,
   `monto = precioVenta * porcentaje / 100`. Create `Comision { prospectoId, comercialId, baseCalculo:
   precioVenta, porcentaje, monto, estado: PENDIENTE }`.

Idempotency: `Prospecto.empresaId @unique` + `Comision.prospectoId @unique` prevent double-win
(second attempt 409). Losing: `POST /prospectos/:id/perder { motivoPerdida }` → estado PERDIDO.

## Access model (requireRole, no requirePermiso)
Platform roles use `requireRole` (not the empresa permiso system).
- `GET/POST /prospectos`, `PATCH /prospectos/:id`, advance/win/lose: `requireRole(ADMIN, COMERCIAL)`.
  When `req.user.rol === COMERCIAL`, the handler hard-scopes `where: { comercialId: req.user.sub }`
  on reads and rejects writes to prospectos not assigned to them (404). ADMIN sees/edits all and is
  the only role that may set/!change `comercialId` (assign) and configure `porcentajeComision`.
- `GET /comisiones`: `requireRole(ADMIN, COMERCIAL)` — COMERCIAL scoped to own.
- `PATCH /comisiones/:id` (mark PAGADA/ANULADA): `requireRole(ADMIN)` only.

## Endpoints
```
GET   /prospectos            list (ADMIN: all + ?comercialId/?estado/?canal; COMERCIAL: own)
POST  /prospectos            create (ADMIN may set comercialId; COMERCIAL → self)
GET   /prospectos/:id        detail
PATCH /prospectos/:id        edit fields / advance estado / (ADMIN) reassign comercial
POST  /prospectos/:id/ganar  win → Empresa+Suscripcion+Comision (tx)
POST  /prospectos/:id/perder lose { motivoPerdida }
GET   /comisiones            list (own | all) + ?estado/?comercialId
PATCH /comisiones/:id        ADMIN: estado PAGADA(+fechaPago)/ANULADA
GET   /ventas/reporte        (optional) totals: ventas, monto vendido, comisiones por estado, by canal
```

## Admin UI
- Nav: `Prospectos`, `Comisiones` (ADMIN sees both; COMERCIAL sees both, scoped). A platform-role
  guard mirrors the client's `AdminEmpresaGuard` but on `rol`.
- Prospectos: funnel list grouped/filterable by estado; create modal (canal, plan interés, contacto);
  detail with advance + **Ganar** (pick plan, negotiated price, optional fixed commission) + **Perder**.
- Comisiones: table (comercial, prospecto/empresa, base, %, monto, estado) + ADMIN "Marcar pagada".
- Usuarios: add `COMERCIAL` to the rol select and a `porcentajeComision` field shown for COMERCIAL.
