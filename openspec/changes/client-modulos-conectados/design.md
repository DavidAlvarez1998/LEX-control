# Design — client-modulos-conectados

Decisiones de diseño para conectar los módulos del portal cliente. Basado en el mapa real del
código (ver `proposal.md`). Artefactos en español por consistencia con los demás changes del repo.

## D1 — La columna vertebral: Cliente y Proceso

El dominio ya tiene dos "anclas" y casi todo cuelga de ellas:
- **`Cliente`** ← Proceso, Cotizacion, ContratoComercial, Cartera, Factura, Ingreso, ComisionDespacho, SeguimientoComercial.
- **`Proceso`** ← (vía escalares) Ingreso.procesoId, Cartera.procesoId, Factura.procesoId.

Decisión: **no inventar relaciones nuevas**; surfacear en la UI las que ya existen. Las dos fichas
360 (Cliente y Proceso) son los puntos de unificación naturales.

## D2 — Proceso 360 (la mayor brecha)

Hoy `Ingreso`, `Cartera` y `Factura` llevan `procesoId` (escalar, ya poblado por Contable/
Facturación) pero la ficha del proceso no los lee. Diseño:
- Pestaña **"Financiero"** en `procesos/[id]` que carga:
  - **Ingresos del proceso** — `GET /contable/ingresos?procesoId=` (ya existe el filtro).
  - **Cartera del proceso** — la cartera cuyo `procesoId`/contrato corresponde (derivar de
    `/contable/cartera` filtrando por proceso, o GET nuevo `?procesoId=`).
  - **Facturas del proceso** — requiere `GET /facturacion/facturas?procesoId=` (filtro nuevo, leve).
  - **Contrato comercial de origen** — vía la `SolicitudAsignacionProceso` 1:1 inversa que creó el
    proceso (snapshot `cobroSnapshot` ya guardado) o el `contratoId` de los ingresos.
- Solo lectura para el rol JURIDICO; CONTABLE/admin pueden actuar donde ya tienen permiso.
- Reusa `requirePermiso` existente (no abre datos nuevos: el proceso ya es del despacho).

## D3 — Cliente: faltan Facturas

La ficha de Cliente ya es un hub; solo falta una sección **Facturas** (`GET /facturacion/facturas?clienteId=`,
filtro a confirmar/añadir) + un mini-resumen de ingresos. Misma página `clientes/[id]`.

## D4 — Facturación muestra su origen

`Factura.contratoId` y `Factura.configuracionCobroId` existen pero no se muestran. En el detalle de
factura, añadir (solo lectura) el **contrato comercial** y el **plan de cobro** de origen, para que
el relato "de dónde sale esta factura" sea visible. Sin cambiar el flujo de emisión/pago.

## D5 — Desambiguación de "Contratos" (UX, sin schema)

Dos conceptos, dos nombres en la UI:
- En la ficha del Cliente: el bloque actual "Contrato y cierre" → mantener como **Contrato del
  cliente** (comercial).
- En el sidebar `/contratos` (RRHH): etiquetar claramente como **Contratos del personal** (o "Equipo
  / RRHH"). Tablas y modelos NO cambian (`contratos_comerciales` vs `contratos`).

## D6 — Comisiones trazables

`ComisionDespacho.contratoId` es escalar (opcional). En la sección Comisiones (ficha cliente y hub
comercial), mostrar el contrato comercial asociado. Vincular a `Ingreso` queda como mejora futura
(hoy `baseCalculo` es manual del admin).

## D7 — Orden por valor/esfuerzo (para implementar luego)

1. **Proceso 360 "Financiero"** — mayor valor (el abogado ve el dinero), esfuerzo medio (1 filtro
   nuevo en facturas; el resto ya existe).
2. **Facturas en ficha Cliente** — cierra el hub, esfuerzo bajo.
3. **Origen en Facturación** (contrato + plan) — esfuerzo bajo.
4. **Desambiguar Contratos** — esfuerzo bajo (etiquetas).
5. **Comisión → contrato visible** — esfuerzo bajo.

## Fuera de alcance (futuro)

- Convertir los escalares `procesoId`/`contratoId`/`facturaId`/`configuracionCobroId` en **FK reales**
  con integridad referencial (hoy se validan en app). Migración de datos + riesgo → change aparte.
- Vincular `ComisionDespacho` a `Ingreso`/`Factura` con cálculo automático.
