# contratos-contable-facturacion

## Por qué

Definir (SDD, sin implementar aún) **cómo se relacionan correctamente** en el portal del
despacho tres piezas: **Contratos del equipo (RR.HH.)**, **Contable** y **Facturación**, y
cómo encaja el **equipo (Usuarios)**. Hoy las tres existen y se tocan en partes, pero el
modelo no está documentado ni completo.

## Estado actual (verificado en schema + código)

**Hay DOS "contratos" distintos** — clave para no confundirlos:
- **`Contrato`** = contrato **RR.HH.** del personal del despacho. Tiene `usuarioId` (vincula a
  un miembro del equipo), `honorarios`, `formaPago` (Mensual / Por caso / Comisión), `diaPago`,
  `tipoColaborador`, etc. → es la **fuente de verdad del COSTO de cada persona**.
- **`ContratoComercial`** = contrato de **servicio al cliente** (embudo comercial), con
  `ConfiguracionCobro` (plan de cobro). → origen de los **INGRESOS**.

**Flujos que ya existen:**
- **Ingresos:** `ContratoComercial` → `ConfiguracionCobro` → **`Factura`** (facturación) →
  al pagarse genera un **`Ingreso`** (contable, enlazado por `facturaId`).
- **Costos del equipo:** `Contrato` (RR.HH.) → **`Nomina`** (contable) — hoy se **prellena por
  copia** desde el contrato (`GET /contable/nominas/empleables`), guarda `empleadoId` (Usuario.id)
  y un snapshot; **no** guarda `contratoId`.
- **Comisiones:** `ComisionDespacho` (un COMERCIAL cierra un `ContratoComercial`).
- **Consolidación:** `contable.reporte` **ya** calcula el P&L del periodo:
  `utilidadNeta = totalIngresos − (egresos + nómina + serviciosFijos + caja)`.

## El modelo correcto (cómo se relacionan los 3)

**Contable es el hub / libro mayor.** Facturación alimenta los **ingresos**; los Contratos del
equipo alimentan los **costos** (vía Nómina); Contable **consolida**.

```
  Cliente ─ ContratoComercial ─ Factura ──(pago)──▶ Ingreso ┐
                                                            │
  Equipo (Usuario) ─ Contrato(RR.HH.) ──▶ Nómina ─(egreso)──┤──▶ CONTABLE
                                                            │     (P&L · caja · cartera)
  (Comercial) ContratoComercial cerrado ─▶ ComisiónDespacho ┘
```

- El **Contrato del equipo** = fuente de verdad del costo de la persona.
- La **Nómina** lo **materializa por periodo** (egreso).
- La **Facturación** materializa el ingreso del cliente.
- El **reporte de Contable** los resta → utilidad. Ese es el punto donde "se encuentran" los 3.

## Huecos para que quede "bien hecho"

1. **Nómina ↔ Contrato sin enlace fuerte:** nómina copia valores pero no guarda `contratoId`.
   → agregar `Nomina.contratoId` (trazabilidad: de qué contrato salió cada pago).
2. **Sin recurrencia de nómina:** se crea manual por periodo. → **generar** la nómina del periodo
   desde los Contratos **activos** con `formaPago = Mensual` (idempotente, clamp de `diaPago`),
   reusando el patrón ya probado de `ServicioFijoRecurrente`. (Memoria: "Recurrencia = Fase 2".)
3. **`formaPago` no dirige el costo:** debería ramificar — **Mensual** → nómina fija; **Por caso**
   → egreso ligado a un proceso; **Comisión** → integra con `ComisionDespacho`.
4. **Sin rentabilidad por cliente/proceso:** no se imputa el costo del equipo a procesos, así que
   no hay P&L por cliente/proceso (ingresos de facturación − costo del equipo imputado).

## Plan por fases (propuesto)

- **Fase 1 — Enlace + trazabilidad (bajo riesgo):** `Nomina.contratoId`; el prellenado y el
  reporte ya existen. Deja la base trazable.
- **Fase 2 — Recurrencia de nómina:** `POST /contable/nominas/generar?periodo=YYYY-MM` que crea las
  instancias del periodo desde contratos activos Mensuales (idempotente). Espejo de servicios fijos.
- **Fase 3 — `formaPago` dirige el flujo:** Por caso → egreso por proceso; Comisión → enlaza
  `ComisionDespacho`.
- **Fase 4 — Rentabilidad por cliente/proceso:** imputar el costo del equipo a procesos para P&L
  por cliente/proceso (cierra el círculo facturación↔costos).

## Decisiones a confirmar (antes de redactar specs)

1. ¿La nómina se **autogenera** desde contratos activos (Fase 2) o sigue **manual con prellenado**?
2. ¿Quieren **rentabilidad por cliente/proceso** (imputar costo del equipo)? Define si entran Fases 3-4.
3. ¿Los contratos **por comisión / por caso** entran ahora o después?
4. ¿`Nomina` debe **bloquear edición** de los valores que vienen del contrato (snapshot fiel) o
   permitir ajuste manual por periodo (bonos/descuentos)? (Hoy es copy-values editable.)

## Impacto (cuando se implemente)

- **API**: posible `Nomina.contratoId` (migración aditiva), endpoint de generación recurrente,
  ramas por `formaPago`, agregaciones de rentabilidad. **Schema**: solo columnas aditivas.
- **Client**: Contratos (equipo) ya existe; Contable/Nómina y Facturación ya existen — se trata
  de **enlazarlos**, no de crear módulos nuevos.

## Fuera de alcance

- Liquidación laboral real (prestaciones, seguridad social, retención) — la nómina aquí es
  registro de pagos, no liquidador (ya advertido en `sdd-nomina-desde-contrato`).
- Integración tributaria/DIAN.
