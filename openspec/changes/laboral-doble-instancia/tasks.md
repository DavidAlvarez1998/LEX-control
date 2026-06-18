# Tasks — laboral-doble-instancia

> Estado: **APLICADO + VERIFICADO** (2026-06-18). 422 tests API verdes (9 nuevos de flujos
> laborales) + re-seed (38 tipos) + build cliente verde. SIN commit. Falta smoke manual en vivo.

## 0. Diseño y validación (este change)
- [x] Extraer el doc fuente y trazar el flujo demandante·doble de-duplicado
- [x] 3 correcciones confirmadas (recurso tras subsanar · auto admisorio tras subsanar · orden prep→citación)
- [x] 2ª instancia real confirmada (sin consulta art. 69 ni casación)
- [x] Mapas de los 4 casos (`flujos-4-casos.md`)
- [x] Organización por fases (`fases.md`)
- [x] Confirmar D1–D4 (consistencia entre casos) con el usuario
- [x] Confirmar nombres/cantidad de fases (6) con el usuario

## 1. Seed — `prisma/seed-tipos.json` (tipo[20] "Proceso Laboral")
- [x] Campos nuevos: `fechaAdmisionTrasSubsanacion`, `concedeApelacion`, `fechaRemision2inst`,
      `radicado2inst`, `fechaSustentacion`, `fechaAudiencia2inst`, `fechaSentencia2inst`,
      `decisionSegundaInstancia`
- [x] Reusar campos de recurso para el rechazo tras subsanar (`mostrarSi` con `{alguna:[...]}`)
- [x] `decisionAuto`/subsanación/recurso-de-rechazo gateados a `rol = Demandante` (D1/D2)
- [x] Renumerar `orden` (subsanacion 2, recurso_rechazo 3, …; 2ª instancia 13–16; terminada 17)
- [x] Variantes `preparacionAudiencia_doble`/`citacionAudiencia_doble` (orden invertido, gated doble)
- [x] Apelación en 2 pasos (`hayRecurso` → `concedeApelacion`)
- [x] Etapas 2ª instancia: `remision2inst`, `sustentacion2inst`, `audiencia2inst`, `sentencia2inst`
      (gated `concedeApelacion = SI`) + documentos nuevos
- [x] (opcional fases) etiqueta `fase` 1–6 por etapa
- [x] `pnpm seed:catalogo` (upsert + `esquemaVersion++`)

## 2. Cliente — `components/datos-proceso.tsx`
- [x] `TITULO_SECCION_LABORAL` += variantes _doble + 4 secciones de 2ª instancia
- [x] `tituloEtapa`/`tituloCampo` instance-aware para prep/citación (orden de secciones por instancia)
- [ ] (opcional fases) render del stepper agrupado por `fase`

## 3. Verificación
- [x] `seed-tipos.test.ts` verde
- [x] Simulación de los 4 caminos (cada rol × instancia camina y termina; ramas de archivo/recurso/2ª inst.)
- [x] `pnpm build` cliente verde
- [ ] Smoke manual del flujo demandante·doble end-to-end (incl. 2ª instancia)
- [ ] Actualizar memoria engram + commit
