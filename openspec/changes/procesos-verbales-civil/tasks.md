# Tasks — procesos-verbales-civil

> Estado: **PLAN SDD** (diseño escrito; **nada aplicado**). La API está en reestructuración →
> no tocar el seed todavía. Implementar cuando esté lista y tras confirmar las decisiones del
> `proposal.md` (rol, cuantía, plazos hábiles, 2ª instancia completa).

## 0. Confirmaciones previas (con el usuario)
- [ ] ¿Modelar `rol` (Demandante/Demandado) en el verbal? (calificación solo del demandante)
- [ ] ¿Capturar `cuantiaTipo` (Mayor/Menor) o basta el monto?
- [ ] Plazos en días **hábiles** (CGP 118): traslado 20 (verbal)/10 (sumario), subsanación 5, recurso 3
- [ ] ¿2ª instancia del verbal completa (remisión→sustentación→audiencia→sentencia 2ª) o resultado único?

## 1. Seed — `Proceso declarativo verbal` (reescribir entrada)
- [ ] `esquemaFormulario`: campos intake + `soloFicha` (ver `design.md` §A)
- [ ] `etapas`: presentacion→calificacion→[subsanacion|recurso_rechazo|archivado_rechazo]→retiro→[archivado|traslado]→contestacion→audienciaInicial→[audienciaInstruccion|terminada_conciliacion]→recurso→[2ª instancia]→terminada
- [ ] `disponibleSi` compuestos (rol×decisiones); `mostrarSi` en campos de ficha
- [ ] documentos anclados (demanda/pruebas/anexos/poder/auto/subsanacion/notificacion/contestacion/sentencia/2inst)
- [ ] plazos con `plazoDesdeCampo` + `plazoTipoDias=habiles` (20/5/3)
- [ ] etiqueta `fase` 1–6 por etapa
- [ ] `esJudicial=true`, jurisdicción `ORDINARIA_CIVIL`

## 2. Seed — `Proceso verbal sumario` (reescribir entrada)
- [ ] `esquemaFormulario` (ver `design.md` §B; sin reconvención/2ª instancia)
- [ ] `etapas`: presentacion→calificacion→[subsanacion|archivado_rechazo]→retiro→[archivado|traslado]→contestacion→[audienciaUnica|terminada_conciliacion]→recurso(reposición)→terminada
- [ ] documentos anclados + plazos (10/5/3 hábiles) + `fase` por etapa
- [ ] `esJudicial=true`, jurisdicción `ORDINARIA_CIVIL`

## 3. Re-seed y verificación
- [ ] `pnpm seed:catalogo` (upsert + `esquemaVersion++`)
- [ ] Test de flujos (estilo `tests/laboral-flujos.test.ts`): cada camino camina y termina sin estancarse
- [ ] Smoke e2e (estilo `scripts/smoke-laboral-flujo.ts`): verbal (demandante→2ª inst.) y sumario (única→reposición); gating (demandado no califica; sumario sin 2ª instancia)
- [ ] Build cliente verde (la ficha genérica + stepper por fases ya los soporta)

## 4. Cierre
- [ ] Actualizar memoria + commit (staging selectivo por submódulo)

## Notas
- **Motor sin cambios**: ya soporta `{todas}`/`{alguna}`, niveles de `orden`, terminales,
  plazos y el stepper por fases (genérico para judiciales). Solo es trabajo de **datos del seed**.
- **Reusa** el patrón de `laboral-doble-instancia` (el verbal es casi idéntico en estructura).
