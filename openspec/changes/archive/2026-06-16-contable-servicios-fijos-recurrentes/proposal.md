# Proposal: Servicios fijos recurrentes (plantilla + generación por periodo)

## Intent
Hoy `ServicioFijo` es un snapshot por periodo (`@@unique(empresaId, tipoServicio, proveedor, periodo)`)
con un `fechaVencimiento` tecleado a mano cada mes. No existe noción de **recurrencia**: el contable no
puede declarar "el internet vence el día 5 de cada mes" ni "el dominio se paga el 20 de noviembre de
cada año". Este change añade una **plantilla recurrente** que define la regla una vez y desde la cual se
**generan/causan** las instancias `ServicioFijo` del periodo con su `fechaVencimiento` calculada.

## Motivación (problema reportado)
El usuario detectó dos cosas en la vista Contable:
1. Servicios fijos debería permitir fijar el **día (y mes si es anual)** en que se cumple el pago, según
   frecuencia mensual o anual. → este change.
2. Pagar un servicio fijo desde una cuenta no descontaba el saldo. → arreglado aparte (la derivación de
   `CuentaBancaria.saldoActual` ahora resta también `ServicioFijo` y `Nomina` PAGADO; ya estaba previsto
   como opcional en el spec `contable-cuentas`).

## Scope
- **Schema** (additive): enum `FrecuenciaServicioFijo { MENSUAL, ANUAL }`; modelo
  `ServicioFijoRecurrente` (hoja de Empresa, `@@unique(empresaId, tipoServicio, proveedor)`); campo
  escalar `ServicioFijo.recurrenteId?` (sin FK) para trazar el origen.
- **API** (módulo `contable`, reusa permisos `contable.serviciofijo.ver/.crear/.editar`):
  - `GET/POST/PATCH /contable/servicios-fijos-recurrentes` — CRUD de plantillas (sin DELETE: soft via `activo`).
  - `POST /contable/servicios-fijos-recurrentes/generar` `{ periodo }` — causa las instancias del periodo
    desde las plantillas activas; **MENSUAL** aplica a todo periodo, **ANUAL** solo si `mes(periodo) ==
    mesPago`; `fechaVencimiento` se recorta al último día del mes (día 31 en febrero → 28/29);
    **idempotente** (respeta el `@@unique` por periodo, `skipDuplicates`).
- **Frontend** (cliente): sección "Plantillas recurrentes" en la pestaña Servicios fijos (CRUD +
  activar/desactivar) y botón "Generar periodo".

## Decisiones
- **Reusa permisos** de servicio fijo (no se crean claves nuevas) → CONTABLE ya las tiene, cero re-seed.
- **valorEstimado** en la plantilla; la instancia copia ese valor como `valorFacturado` (editable luego).
- Generación **explícita** (botón), no cron — coherente con el resto del módulo (sin jobs).

## Out of scope
- `VENCIDO` derivado en lectura (`fechaVencimiento < now`) sigue pendiente (gap conocido del módulo).
- Cron/automatización de la generación mensual.
