# Tasks — procesos-laborales

> Diseño primero: las tareas de implementación se ejecutan tras la aprobación del design.

## 0. Diseño (este change)
- [x] 0.1 Leer y entender el doc fuente (`PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`)
- [x] 0.2 Mapear motor (esquema.ts solo igualdad), seed (DdP como referencia de ramas), taxonomía
- [x] 0.3 proposal.md + design.md (árbol de etapas) + specs delta + state.yaml
- [x] 0.4 Aprobación del usuario del árbol de etapas y el esquema de campos

## 1. Schema (lex-control-api/prisma/schema.prisma)
- [x] 1.1 Agregar `LABORAL` al enum `GrupoProceso`
- [x] 1.2 `pnpm generate`; aplicar con `pnpm push` (la BD no usa migrate — ver [[db-not-managed-by-migrate]])

## 2. Catálogo (lex-control-api/prisma/seed-tipos.json)
- [x] 2.1 Nuevo `TipoProceso` "Proceso Laboral" (`grupo: LABORAL`, `jurisdiccion: ORDINARIA_LABORAL`, `esJudicial: true`, área `laboral`)
- [x] 2.2 `esquemaFormulario`: selects `rol` + `tipoInstancia` requeridos; bloques demanda / admisión / retiro / traslado / contestación(doble) / preparación / audiencia / sentencia con `mostrarSi`/`requeridoSi`/`soloFicha` (ver design §4)
- [x] 2.3 `etapas`: árbol de design §2 (orden + `disponibleSi` por `tipoInstancia`) con `reglas`/`requeridosSi`/`opcionalesSi`/`plazoDesdeCampo` (ver design §3)
- [x] 2.4 Plazos: contestación 10 HÁBILES (traslado), subsanación 5 HÁBILES (inadmisión); recurso 3 CALENDARIO (sentencia + rechazo)
- [x] 2.5 Eliminar (o marcar obsoleto) el stub "Proceso ordinario laboral de primera instancia"
- [x] 2.6 Re-seed del catálogo; verificar que el tipo carga y valida (esquema bien formado)

## 3. Frontend cliente (lex-control-client)
- [x] 3.1 `lib/procesos.ts`: `type GrupoProceso` += `"LABORAL"`; `SECCION_RUTA["LABORAL"] = "/procesos-laborales"`
- [x] 3.2 `lib/nav.tsx`: ítem "Procesos Laborales" (`roles: ["JURIDICO"]`) **debajo** de "Acciones Constitucionales"
- [x] 3.3 `(dashboard)/procesos-laborales/page.tsx`: lista filtrando `grupo === "LABORAL"` (reusa patrón de lista de procesos: Vence + semáforo + búsqueda)
- [x] 3.4 `(dashboard)/procesos-laborales/nuevo/page.tsx`: tipo bloqueado a "Proceso Laboral" (estilo `/peticiones/nueva?tipo=ID`); form muestra `rol` + `tipoInstancia` primero
- [x] 3.5 `(dashboard)/procesos-laborales/[id]/page.tsx`: ficha (reusa el componente de ficha de proceso: countdown, stepper, docs requeridos)
- [x] 3.6 `(dashboard)/procesos/nuevo`: filtrar `esJudicial && grupo === "JUDICIAL"` para excluir LABORAL del wizard genérico

## 4. Verificar
- [x] 4.1 `pnpm build` API + cliente verdes; tsc limpio
- [x] 4.2 Smoke en vivo por variante: crear Demandante·Única y Demandado·Doble → avanzar etapas → comprobar ramas (subsanación/rechazo, contestación/reconvención, audiencia única vs art77+art80) y `fechaLimite` (10/5 días hábiles)
- [x] 4.3 Verificar que LABORAL no aparece en `/procesos/nuevo` y sí en `/procesos-laborales/nuevo`

## 5. Archivar
- [ ] 5.1 Fusionar deltas en `openspec/specs/tramite-catalog/spec.md` y `tramite-management/spec.md` (ADDED se anexan); mover el change a `archive/`
- [ ] 5.2 Commit con staging selectivo (rama feat/cuenta-clientes; respetar WIP paralelo del usuario)
