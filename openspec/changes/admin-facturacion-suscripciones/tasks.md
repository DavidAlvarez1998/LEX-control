# Tasks — admin-facturacion-suscripciones

> Estado: **PLAN SDD (no implementado)**. Listo para retomar e implementar en una próxima sesión.
> Reusa patrones ya probados: ServicioFijoRecurrente (generar), Factura (consecutivo+inmutable),
> registrarPago idempotente (Track 4), Cartera (saldo derivado), Empresa.activo (corte por impago).

## Fase 1 — Schema
- [ ] 1.1 Modelo `FacturaSuscripcion` (empresaId, suscripcionId, planId snapshot, periodo, valor, estado, fechaEmision/Vencimiento/Pago, metodoPago, numero) + `@@unique([suscripcionId, periodo])` + enum estado
- [ ] 1.2 `pnpm push` + `pnpm generate`

## Fase 2 — API (módulo nuevo, ADMIN-only, router→service→repository→dto)
- [ ] 2.1 `POST /admin/facturacion/generar { periodo }` — idempotente por (suscripcionId, periodo); valor = Plan.precioMensual; solo ACTIVA
- [ ] 2.2 `GET /admin/facturacion` — lista paginada (parsePage) + filtros (periodo/estado/despacho); estado VENCIDA derivado
- [ ] 2.3 `GET /admin/facturacion/resumen` — KPIs (facturado del mes, pendiente, vencido, MRR, morosos)
- [ ] 2.4 `POST /admin/facturacion/:id/pago` — registrar pago idempotente (numeroComprobante) → PAGADA
- [ ] 2.5 `POST /admin/facturacion/:id/anular`
- [ ] 2.6 Suspender despacho por mora (reusa Empresa.activo=false)
- [ ] 2.7 Tests (generar idempotente, vencida derivada, pago idempotente, aislamiento del tenant)

## Fase 3 — Vista admin (reemplaza placeholder /facturacion)
- [ ] 3.1 KPIs + botón "Generar facturación del periodo"
- [ ] 3.2 Tabla facturas (despacho/plan/periodo/valor/vence/estado semáforo) + filtros + paginación
- [ ] 3.3 Acciones por factura (ver, marcar pagada/link de pago, anular)
- [ ] 3.4 Vista por despacho (suscripción + historial + cartera)

## Fase 4 — Pago automático (futuro, depende de cuenta del usuario)
- [ ] 4.1 Integrar pasarela (Wompi/PayU) + webhook → PAGADA (Fase 0 comercial)

## Cierre
- [ ] Gate: tsc + tests + build admin; smoke (generar periodo, pagar, suspender)
- [ ] Resolver decisiones abiertas del design (anual/prorrateo/estado derivado/excesos)
- [ ] Fusionar spec a `openspec/specs/admin-facturacion-suscripciones/` y archivar
