# comercial-rol-portal

## Por qué

El RolEmpresa **COMERCIAL** del despacho (portal cliente) ya cubre el embudo de ventas
(clientes, seguimientos, fases, cotizaciones, contratos, cobro, solicitud de asignación),
pero le faltaban cuatro capacidades que la operación real de un despacho exige. Este cambio
las cierra y, de paso, tapa un hueco de seguridad en la API de procesos.

## Qué cambia

1. **Comisiones internas (MANUAL).** Nuevo modelo `ComisionDespacho` (empresaId/clienteId/
   comercialId + base/%/monto/estado). El ADMINISTRADOR de la empresa las registra/edita; el
   COMERCIAL solo ve las suyas (acotadas por `comercialId` en el router). Permisos
   `comercial.comision.ver` (ADMINISTRADOR+COMERCIAL) / `.crear` / `.editar` (solo ADMINISTRADOR).
   Endpoints `GET/POST/PATCH /comercial/comisiones`. UI en la ficha del cliente.

2. **Resumen de cobro/cartera en la ficha (solo lectura).** `GET /comercial/clientes/:id/cartera`
   bajo `comercial.cobro.ver` (módulo comercial, NO exige contable). Reusa la derivación de
   saldos extraída a `contable/cartera.service.ts` (`valorPagado`/`conSaldo`).

3. **Agenda del comercial (reusa seguimientos).** `SeguimientoComercial` se extiende con campos de
   agenda (`comercialId` dueño, `titulo`, `completada`, `fechaCompletada`, `canceladaEn`,
   `motivoCancelacion`); `fechaProximaTarea` es el slot. `GET /comercial/agenda` (mes, dueño,
   incluirCompletadas, vencidas) + `POST /comercial/seguimientos/:id/{completar,cancelar,reabrir}`.
   UI: calendario mensual portado del admin (`agenda-comercial-view.tsx`) + página `/agenda` +
   ítem de nav (roles COMERCIAL).

4. **Procesos asegurados + lectura para COMERCIAL.** `procesos.router` pasa de solo `requireAuth`
   a `requirePermiso`: lecturas → `proceso.ver` (JURIDICO+COMERCIAL+ADMINISTRADOR), escrituras →
   `proceso.editar` (JURIDICO+ADMINISTRADOR). El COMERCIAL (sin JURIDICO) ve `GET /procesos` acotado
   a sus clientes (responsable o responsableComercial). UI: `/procesos` y `/procesos/[id]` abren a
   COMERCIAL en **solo lectura** (sin crear/etapa/radicado/datos/documentos/derivar).

## Impacto

- Schema: +1 modelo (`comisiones_despacho`), +6 columnas nullable en `seguimientos_comerciales`
  (aplicado con `db push`; backfill `comercialId=registradoPorId`).
- Seed: +5 permisos (`comercial.comision.*`, `proceso.ver/editar`). RBAC global → afecta a usuarios
  existentes al instante.
- Tests: +14 (366 total); mocks de procesos ampliados con permiso/módulo/suscripción.
- Frontends: portal cliente (nuevo lib `comercial-api.ts`, componente de agenda, secciones de
  cartera/comisiones en la ficha, procesos solo-lectura). Ambos builds verdes.
