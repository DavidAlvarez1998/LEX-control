# client-modulos-conectados

## Por qué

En el portal cliente, el **dato vive bien relacionado en la BD** (todo cuelga de `Cliente` y casi
todo de `Proceso`/`ContratoComercial`), pero la **UI lo muestra en silos**: cada módulo
(Clientes/CRM, Procesos, Facturación, Contable, Contratos) enseña solo lo suyo. El usuario pidió
**identificar con SDD qué debería estar unido** (facturación, comercial, comisiones, contratos…).

Este change es **análisis + diseño** (no implementación todavía): mapea el estado real y define el
"to-be" de las conexiones cruzadas que faltan, para luego implementarlas por fases.

## Estado actual (mapeado en el código)

- **Ficha de Cliente = hub ya integrado** ⭐⭐⭐⭐ — muestra procesos, seguimientos, cotizaciones,
  contrato comercial + cobro, cartera y comisiones. **Hueco:** no muestra **facturas** ni un
  resumen de ingresos del cliente.
- **Procesos = silo jurídico** ⭐⭐ — la ficha del caso **no ve el dinero**: ni ingresos, ni cartera,
  ni facturas, ni el contrato comercial de origen (aunque `Ingreso/Cartera/Factura` ya tienen
  `procesoId`/`contratoId`). El abogado no ve cómo va el cobro de su caso.
- **Facturación = silo parcial** ⭐⭐ — emite facturas y registra pagos (pago → `Ingreso` vía
  `facturaId`, ya cableado), pero **no muestra el contrato comercial ni el plan de cobro**
  (`ConfiguracionCobro`) de origen, aunque `Factura.contratoId`/`configuracionCobroId` existen.
- **Contable** ⭐⭐⭐ — dos mundos en pestañas; **Cartera** sí deriva de `ConfiguracionCobro`+`Ingreso`.
  No surfacea contrato comercial/cotización.
- **Contratos (RRHH) = aislado** ⭐ — solo conecta con Nómina (Contable lee `Contrato.honorarios`).

### Colisión de nombres "Contrato"
Hay **dos conceptos** que la UI no distingue bien:
- **`ContratoComercial`** (acuerdo + cobro con el cliente) → aparece como "Contrato y cierre" dentro
  de la ficha del Cliente.
- **`Contrato`** (laboral, del personal/RRHH) → pantalla `/contratos` (solo admin de empresa).
Ambos se leen como "Contratos" → confunde.

## Qué se propone unir (to-be)

1. **Proceso 360 — pestaña "Financiero"**: en la ficha del proceso, mostrar sus **ingresos,
   cartera, facturas y el contrato comercial de origen** (ya ligados por `procesoId`/`contratoId`;
   solo falta surfacearlos). Es el hueco de mayor valor: el abogado ve el cobro de su caso.
2. **Cliente — añadir Facturas + resumen de ingresos**: cerrar el hueco del hub (hoy ve cartera y
   comisiones pero no las facturas).
3. **Facturación — mostrar origen**: en cada factura, el **contrato comercial** y el **plan de
   cobro** que la originan; y dejar claro el relato factura → pago → ingreso → cartera.
4. **Desambiguar "Contratos"**: nombres claros en la UI — "Contratos del cliente" (comercial) vs
   "Contratos del personal" (RRHH) — para que nadie los confunda.
5. **Comisiones trazables**: mostrar de qué **contrato comercial** (y opcionalmente qué ingreso)
   nace cada `ComisionDespacho`.

> Clave: casi todo esto es **surfacear enlaces que YA existen en datos** (FKs/escalares
> `procesoId`/`contratoId`/`configuracionCobroId`/`facturaId`). Poco o nada de schema nuevo.

## Impacto

- Mayormente **frontend** (nuevas secciones/pestañas que consumen endpoints existentes o leves GET
  nuevos filtrados por `procesoId`). Posibles GET de conveniencia en API (`?procesoId=`).
- **Sin cambios de schema** salvo, si se decide, hacer FK reales algunos escalares (fuera de alcance
  inicial). Riesgo bajo: es additivo y de presentación.

## Rollback

Aditivo: quitar las secciones/pestañas nuevas. No toca datos ni contratos HTTP existentes.
