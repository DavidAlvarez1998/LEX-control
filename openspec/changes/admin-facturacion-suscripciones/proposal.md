# admin-facturacion-suscripciones

## Por qué

El portal **admin** tiene una pantalla "Facturación" que hoy es **placeholder** (datos en cero,
sin backend). Esa pantalla debe ser la **facturación de PLATAFORMA**: LEX Control cobrándole a cada
**despacho** su **suscripción al Plan** (el ingreso recurrente del negocio). Es distinta de la
facturación del portal cliente (despacho → sus propios clientes), que sí existe.

Hoy **no hay modelo** de factura/pago a nivel plataforma. Lo que existe: `Plan.precioMensual`,
`Suscripcion` (1 por `Empresa`, con `estado`/`inicioEn`/`finEn`) y el flujo de venta
(Prospecto ganado → Empresa + Suscripcion + Comision). Falta cerrar el ciclo: **cobrar el recurrente**.

> Alcance de este change: **diseño/plan (SDD)**. No se implementa todavía — queda listo para
> retomar e implementar en una próxima sesión. Encaja con la Fase 0 comercial (pasarela de pago).

## Qué se construye (cuando se implemente)

1. **Modelo nuevo** `FacturaSuscripcion` (plataforma→despacho): `empresaId`, `suscripcionId`,
   `planId` (snapshot), `periodo` (`YYYY-MM`), `valor`, `estado`
   (PENDIENTE/PAGADA/VENCIDA/ANULADA), `fechaEmision`, `fechaVencimiento`, `fechaPago`,
   `metodoPago`, `numero` consecutivo. **Único por `(suscripcionId, periodo)`** (idempotente).
2. **Generación por periodo** — acción "Generar facturación de {mes}": recorre suscripciones
   `ACTIVA` y crea la factura faltante de ese periodo (no duplica). Mismo patrón probado que
   `ServicioFijoRecurrente` del contable.
3. **Cobro** — registrar pago manual (→ PAGADA) y/o **pasarela** (Wompi/PayU) para autocobro.
   Impago prolongado → suspender la suscripción → `Empresa.activo=false` ya **corta el acceso**.
4. **Vista admin "Facturación"** — tablero de cobros: KPIs (facturado del mes, pendiente, vencido,
   MRR, morosos), botón "Generar periodo", tabla de facturas (despacho/plan/periodo/valor/vence/
   estado con semáforo) + filtros, acciones por factura (ver, marcar pagada/link de pago, anular),
   y vista por despacho (suscripción + historial + cartera).

### Qué se factura y cuándo (resumen)
- **Qué:** `Plan.precioMensual` de la suscripción activa (mensual; anual = ×12 con posible
  descuento). Excesos de cupo (`PlanCuota` vs uso real) = mejora futura.
- **Cuándo:** recurrente por periodo `YYYY-MM` (mes calendario), emisión al inicio, vencimiento
  `+N días`; solo suscripciones `ACTIVA`; prorrateo del primer periodo (opcional).

## Impacto

- **Schema:** modelo `FacturaSuscripcion` (+ enum estado) — aplicar con `db push`.
- **API:** módulo nuevo (router→service→repository→dto) con generar-periodo, listar, registrar pago,
  anular, resumen/KPIs. ADMIN-only.
- **Admin front:** reemplazar el placeholder `/facturacion` por la vista real.
- **Reusa:** patrones de `ServicioFijoRecurrente` (generación), `Factura` (consecutivo+inmutable),
  `Cartera` (saldo derivado), `Empresa.activo` (corte por impago).

## Rollback

Aditivo: modelo + módulo + vista nuevos. Rollback = revertir schema (`db push`) y ocultar la vista.
No afecta la facturación del portal cliente (es otro modelo).
