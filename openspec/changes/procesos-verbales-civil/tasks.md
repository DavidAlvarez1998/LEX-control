# Tasks — procesos-verbales-civil

> Estado: **REESCRITO FIEL AL DOC + VERIFICADO** (2026-06-19). 2ª pasada: el seed genérico se
> reescribió FIEL a `doc-verbal.md` / `doc-verbal-sumario.md` (de los .docx). Ahora **verbal = 144
> campos / 16 etapas; sumario = 104 / 12**. Cubre lo que faltaba (ver `validacion-vs-doc.md`):
> CALIDAD 7 roles · datos de partes · unidad/cuantía/pretensión determinada→montos · MÓDULO MEDIDAS
> CAUTELARES (19 campos: solicitud→tipo→decisión→caución→ejecución→levantamiento) · calificación
> detallada (admisión/inadmisión→subsanación 5d→decisión/recurso · rechazo→recurso) · traslado
> (20d verbal / 10d sumario) · reconvención · excepciones de mérito (verbal) · audiencia inicial 372
> + instrucción 373 (asistencias/conciliación/decreto de pruebas/sentencia inmediata/alegatos) ·
> sentencia (tipo/resultado/costas) · recursos (apelación/aclaración/corrección/adición/reposición)
> + 2ª instancia (efecto/ponente/resultado). Sumario ⭐: demanda Verbal/Escrita · ¿mínima cuantía? ·
> correo del juzgado · reposición vs auto admisorio · SENTENCIA ANTICIPADA sin audiencia · audiencia
> ÚNICA 392 · sin 2ª instancia. Gate: **448 tests API** (12 flujos en `tests/verbales-flujos.test.ts`,
> todas las ramas caminan sin estancarse) + tsc + re-seed (`seed:catalogo`, BD verificada) + build
> cliente verde. SIN commit. Mutua-exclusividad y no-deadlock de `disponibleSi` verificados por el motor real.

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
- [x] `pnpm seed:catalogo` (upsert; 38 tipos actualizados; BD verificada: verbal 144/16, sumario 104/12)
- [x] Test de flujos reescrito al nuevo vocabulario (12 escenarios): admisión→audiencias→apelación→2ª inst; sin apelar; sentencia inmediata; inadmisión→subsana/no-subsana; rechazo→recurso; conciliación total; sumario audiencia única / sentencia anticipada / rechazo
- [ ] Smoke e2e en vivo (estilo `scripts/smoke-laboral-flujo.ts`) — opcional; el test de flujos ya cubre los caminos con el motor real
- [x] Build cliente verde (la ficha genérica + stepper por fases ya los soporta)

## 4. Cierre
- [x] Actualizar memoria
- [ ] Commit (staging selectivo por submódulo) — pendiente

## Notas
- **Motor sin cambios**: ya soporta `{todas}`/`{alguna}`, niveles de `orden`, terminales,
  plazos y el stepper por fases (genérico para judiciales). Solo es trabajo de **datos del seed**.
- **Reusa** el patrón de `laboral-doble-instancia` (el verbal es casi idéntico en estructura).
