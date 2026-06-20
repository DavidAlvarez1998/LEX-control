# Tasks — client-modulos-conectados

> Estado: **ANÁLISIS + DISEÑO (no implementado)**. Mapa del estado real + "to-be" de las conexiones
> que faltan. Casi todo es surfacear enlaces que YA existen en datos (procesoId/contratoId/
> configuracionCobroId/facturaId). Orden por valor/esfuerzo (ver design.md §D7).

## Fase 1 — Proceso 360 "Financiero" (mayor valor)
- [ ] 1.1 API: `GET /facturacion/facturas?procesoId=` (filtro nuevo; ya existe el patrón page/filtros)
- [ ] 1.2 API (opcional): `GET /contable/cartera?procesoId=` o derivar de la cartera del contrato
- [ ] 1.3 Front `procesos/[id]`: pestaña "Financiero" → ingresos (`/contable/ingresos?procesoId=`), cartera, facturas, contrato/términos de origen (vía SolicitudAsignacionProceso.cobroSnapshot)
- [ ] 1.4 Estado vacío claro cuando el proceso no tiene movimientos
- [ ] 1.5 Solo lectura para JURIDICO; respetar requirePermiso existente

## Fase 2 — Facturas en la ficha del Cliente (cierra el hub)
- [ ] 2.1 API: `GET /facturacion/facturas?clienteId=` (confirmar/añadir filtro)
- [ ] 2.2 Front `clientes/[id]`: sección "Facturas" + mini-resumen de ingresos

## Fase 3 — Origen visible en Facturación
- [ ] 3.1 DTO/endpoint de detalle de factura incluye contrato comercial + plan de cobro (lectura)
- [ ] 3.2 Front facturación: mostrar contrato + plan en el detalle (sin tocar emisión/pago)

## Fase 4 — Desambiguar "Contratos" (UX)
- [ ] 4.1 Rótulos: "Contrato del cliente" (comercial, ficha cliente) vs "Contratos del personal" (RRHH, /contratos)
- [ ] 4.2 Revisar nav/títulos para que no se confundan

## Fase 5 — Comisiones trazables
- [ ] 5.1 Mostrar el contrato comercial (`contratoId`) en la vista de ComisionDespacho

## Cierre
- [ ] Gate por fase: tsc + tests API + build cliente; smoke de cada vista
- [ ] Fusionar spec a `openspec/specs/client-modulos-conectados/` y archivar
- [ ] (Futuro, change aparte) convertir escalares procesoId/contratoId/facturaId/configCobroId en FK reales con integridad
