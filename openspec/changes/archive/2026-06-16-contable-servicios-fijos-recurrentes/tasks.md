# Tasks — contable-servicios-fijos-recurrentes

## Schema
- [x] enum `FrecuenciaServicioFijo { MENSUAL, ANUAL }`
- [x] modelo `ServicioFijoRecurrente` (hoja de Empresa, `@@unique(empresaId, tipoServicio, proveedor)`)
- [x] `ServicioFijo.recurrenteId?` escalar + `@@index([empresaId, recurrenteId])`
- [x] back-relation `Empresa.serviciosFijosRecurrentes`
- [x] `pnpm push` + `pnpm generate`

## API (módulo contable)
- [x] schemas Zod: create/update recurrente (ANUAL ⇒ mesPago via `.refine`) + generar
- [x] `GET/POST/PATCH /contable/servicios-fijos-recurrentes` (reusa `contable.serviciofijo.*`)
- [x] `POST /contable/servicios-fijos-recurrentes/generar` — MENSUAL/ANUAL, vencimiento recortado, idempotente
- [x] helper `fechaVencimientoDe(periodo, diaPago)` (UTC, clamp último día)

## Frontend (cliente)
- [x] lib: tipos `ServicioFijoRecurrente`, const `FRECUENCIA_SERVICIO`, métodos API
- [x] pestaña Servicios fijos: sección "Plantillas recurrentes" (CRUD + activar/desactivar) + "Generar periodo"

## VENCIDO derivado (gap del módulo, cerrado)
- [x] `GET /servicios-fijos` añade `vencido` derivado (fechaVencimiento<now y no PAGADO), sin mutar estadoPago
- [x] front: badge muestra "VENCIDO" (rojo) cuando `vencido`; "Marcar pagado" sigue disponible
- [x] test + smoke en vivo (PENDIENTE vencido → vencido=true, estadoPago intacto)

## Borrar/inactivar cuenta (gap contable-cuentas, cerrado)
- [x] `DELETE /contable/cuentas/:id`: 409 si está referenciada (Ingreso/Egreso/Nómina/SF/SF-recurrente) → guía a INACTIVA; 204 si libre; 404 ajena
- [x] front: botón "Eliminar" + ConfirmDialog (muestra el 409 guiando a INACTIVA); `api.del` + `borrarCuenta`
- [x] 3 tests + smoke en vivo (204 sin movimientos, 409 con SF asociado)

## soporteFacturaUrl en UI (gap contable-serviciosfijos, cerrado)
- [x] campo "Soporte de factura (URL)" en el form de instancia + enlace "Abrir soporte ↗"
- [x] smoke en vivo (persiste y se relee)

## Saldo de cuenta (fix relacionado, mismo turno)
- [x] `CuentaBancaria.saldoActual` resta también `ServicioFijo` + `Nomina` PAGADO (detalle y listado)
- [x] listado `GET /cuentas` ahora trae `saldoActual` (groupBy en lote) + columna en el front

## Verificación
- [x] 351/351 tests (4 nuevos de recurrentes + saldo actualizado)
- [x] `tsc` API + cliente limpios; `pnpm build` cliente OK
- [x] smoke en vivo 10/10 (BD real, empresa "Despacho Demo": crear bolsa → plantilla mensual → generar 2030-01 → venc 2030-01-05 → marcar pagado → saldo 1.000.000→910.000 en detalle y listado; limpieza sin residuo)
- [ ] commit / rama / merge — pendiente decisión del usuario
