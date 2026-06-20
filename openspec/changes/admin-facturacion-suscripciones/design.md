# Design — admin-facturacion-suscripciones

Diseño de la facturación de PLATAFORMA (LEX Control → despachos por su suscripción). Plan SDD;
implementación en una próxima sesión. Decisiones con rationale.

## D1 — Modelo separado del de despacho (no reusar `Factura`)

`Factura`/`Ingreso` existentes son **tenant-scoped** (un despacho factura a sus clientes,
`empresaId` = el despacho dueño). La facturación de plataforma es **cross-tenant** (la plataforma
factura a la `Empresa`). Mezclarlas en `Factura` rompería el scoping multi-tenant. Decisión: modelo
nuevo **`FacturaSuscripcion`** a nivel plataforma (lo gestionan ADMIN, no los despachos).

```
FacturaSuscripcion
  id, numero (FSU-YYYY-NNNN, consecutivo plataforma)
  empresaId        → Empresa (el despacho que paga)
  suscripcionId    → Suscripcion
  planId           // snapshot del plan facturado
  periodo          // 'YYYY-MM'  (UNIQUE con suscripcionId)
  valor            Decimal
  estado           PENDIENTE | PAGADA | VENCIDA | ANULADA
  fechaEmision, fechaVencimiento, fechaPago?, metodoPago?
  @@unique([suscripcionId, periodo])   // idempotencia de la generación
```
`VENCIDA` puede ser **derivada** (PENDIENTE + fechaVencimiento < hoy) en vez de columna, igual que
el `estadoPago` derivado de la facturación del despacho — evita un job que mueva estados.

## D2 — Generación idempotente por periodo (patrón ServicioFijoRecurrente)

Acción `POST /admin/facturacion/generar { periodo }`:
- Lee suscripciones `ACTIVA`.
- Para cada una, **upsert lógico** por `(suscripcionId, periodo)`: si ya existe, no duplica.
- `valor` = `Plan.precioMensual` (snapshot). `fechaVencimiento` = emisión + N días.
- Devuelve cuántas creó / cuántas ya existían.
Es exactamente el patrón ya probado en `contable` (`/generar` de servicios fijos recurrentes).

## D3 — Cobro y corte por impago

- **Registro de pago:** `POST /admin/facturacion/:id/pago` → `estado=PAGADA`, `fechaPago`,
  `metodoPago`. Idempotencia por `numeroComprobante` (mismo criterio que `registrarPago` del
  despacho, ya implementado en api-production-grade Track 4).
- **Pasarela (futuro):** Wompi/PayU para autocobro/recaudo (Fase 0 comercial). El webhook marcaría
  PAGADA.
- **Dunning / corte:** una factura `VENCIDA` mucho tiempo → suspender `Suscripcion.estado` y/o poner
  `Empresa.activo=false`, que **ya bloquea el login** de todos los usuarios del despacho
  (capability `empresa-activo-login-block`). No hace falta lógica nueva de corte.

## D4 — Periodicidad y anclaje

- Default **mensual por mes calendario** (`periodo='YYYY-MM'`): simple de conciliar y de mostrar.
- **Anual:** plan/suscripción podría marcar frecuencia anual → `valor = precioMensual*12` (con
  descuento configurable). Mantener `periodo` como el mes de emisión.
- **Prorrateo** del primer periodo (suscripción a mitad de mes): opcional; si complica, cobrar
  periodo completo en v1 y refinar después.

## D5 — Vista admin (reemplaza el placeholder `/facturacion`)

- **KPIs:** Facturado del mes · Pendiente de cobro · Vencido · **MRR** (Σ precioMensual de activas)
  · # despachos al día / morosos.
- **Acción:** "Generar facturación de {mes}".
- **Tabla:** Nº · Despacho · Plan · Periodo · Valor · Vence · Estado (semáforo al-día/por-vencer/
  vencido/pagada). Filtros: periodo, estado, despacho; búsqueda.
- **Por despacho:** suscripción actual + historial de facturas + **cartera** (saldo).
- Paginación con el helper compartido (`parsePage`) — listados pueden crecer.

## D6 — Permisos

ADMIN-only (y quizá rol COMERCIAL de plataforma en lectura, como en otras vistas admin). Reusa el
patrón de auth/roles del admin; no toca el RBAC del despacho.

## Decisiones abiertas (resolver al implementar)

1. ¿Frecuencia anual en v1 o solo mensual? (Leaning: mensual v1.)
2. ¿`estado VENCIDA` derivado o materializado? (Leaning: derivado.)
3. ¿Prorrateo del primer periodo en v1? (Leaning: no, periodo completo.)
4. ¿Excesos de cupo (`PlanCuota` vs uso) facturables? (Futuro, fuera de v1.)
5. Pasarela de pago: ¿v1 manual y pasarela después, o pasarela desde el inicio? (Depende de cuenta
   Wompi/PayU del usuario — Fase 0 comercial.)
