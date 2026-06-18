# Tasks — procesos-verbales-civil

> Estado: **APLICADO + VERIFICADO** (2026-06-18). Seed reescrito (verbal 51 campos/18 etapas; sumario 25/11), grupo=JUDICIAL + esJudicial=true. 442 tests API (8 nuevos: tests/verbales-flujos.test.ts) + re-seed (40 tipos) + build cliente verde. SIN commit. Alcance: tal como dicta el CGP.

## 1. Seed — `Proceso verbal` (reescribir entrada)
- [x] `esquemaFormulario`: campos intake + `soloFicha` (ver `design.md` §A)
- [x] `etapas`: presentacion→calificacion→[subsanacion|recurso_rechazo|archivado_rechazo]→retiro→[archivado|traslado]→contestacion→audienciaInicial→[audienciaInstruccion|terminada_conciliacion]→recurso→[2ª instancia]→terminada
- [x] `disponibleSi` compuestos (rol×decisiones); `mostrarSi` en campos de ficha
- [x] documentos anclados (demanda/pruebas/anexos/poder/auto/subsanacion/notificacion/contestacion/sentencia/2inst)
- [x] plazos con `plazoDesdeCampo` + `plazoTipoDias=habiles` (20/5/3)
- [x] etiqueta `fase` 1–6 por etapa
- [x] `esJudicial=true`, jurisdicción `ORDINARIA_CIVIL`

## 2. Seed — `Proceso verbal sumario` (reescribir entrada)
- [x] `esquemaFormulario` (ver `design.md` §B; sin reconvención/2ª instancia)
- [x] `etapas`: presentacion→calificacion→[subsanacion|archivado_rechazo]→retiro→[archivado|traslado]→contestacion→[audienciaUnica|terminada_conciliacion]→terminada (sentencia EN FIRME, sin recurso)
- [x] documentos anclados + plazos (10/5/3 hábiles) + `fase` por etapa
- [x] `esJudicial=true`, jurisdicción `ORDINARIA_CIVIL`

## 3. Re-seed y verificación
- [x] `pnpm seed:catalogo` (upsert + `esquemaVersion++`)
- [x] Test de flujos (estilo `tests/laboral-flujos.test.ts`): cada camino camina y termina sin estancarse
- [ ] Smoke e2e en vivo (estilo `scripts/smoke-laboral-flujo.ts`) — opcional; el test de flujos ya cubre los caminos con el motor real
- [x] Build cliente verde (la ficha genérica + stepper por fases ya los soporta)

## 4. Cierre
- [x] Actualizar memoria
- [ ] Commit (staging selectivo por submódulo) — pendiente

## Notas
- **Motor sin cambios**: ya soporta `{todas}`/`{alguna}`, niveles de `orden`, terminales,
  plazos y el stepper por fases (genérico para judiciales). Solo es trabajo de **datos del seed**.
- **Reusa** el patrón de `laboral-doble-instancia` (el verbal es casi idéntico en estructura).
