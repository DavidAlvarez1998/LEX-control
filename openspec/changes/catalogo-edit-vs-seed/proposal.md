# catalogo-edit-vs-seed

## Por qué

Pregunta recurrente del equipo: **¿editar un `TipoProceso` en el admin (catálogo de
procesos) daña los flujos curados** que vivimos construyendo (verbal, verbal sumario,
laboral, DdP, tutela)? Y al revés: ¿qué pasa con esas ediciones cuando se vuelve a
sembrar? Este change **documenta el comportamiento real** (verificado en código) y fija
la **regla de fuente de verdad**, para que nadie pierda trabajo ni corrompa un flujo.

No hay cambio de código: el comportamiento ya está implementado. Esto lo codifica en spec.

## Comportamiento actual (verificado en código)

- **`PATCH /catalog/tipos/:id` → `catalog.service.updateTipo`** sobrescribe en BD
  `esquemaFormulario` y `etapas` con **lo que envíe el form** (el `updateTipoProcesoSchema`
  los exige, `min(1)`), e incrementa `esquemaVersion`.
- **El form del admin (`catalogo-procesos/page.tsx`) protege lo avanzado**: al abrir la
  edición guarda un **snapshot crudo** del tipo (`origCampos`/`origEtapas`) y al guardar
  hace **merge sobre el original**, sobrescribiendo solo lo editable (nombre, descripción,
  jurisdicción, áreas, `esJudicial`, labels, orden, `camposRequeridos` básicos, `plazoDias`)
  y **conservando** lo que no edita:
  - campos: `ayuda`, `mostrarSi`, `requeridoSi`, `soloFicha`…
  - etapas: `documentosRequeridos`, `requeridosSi`, `opcionalesSi`, plazos derivados,
    ramas, `terminal`/`disponibleSi`/`accion`…
  - Si detecta reglas avanzadas (`esCampoAvanzado`/`esEtapaAvanzada`) muestra un **aviso
    ámbar**: *"Este tipo usa reglas avanzadas … Se conservarán al guardar; para cambiarlas,
    edita el catálogo semilla."*
- **`pnpm seed:catalogo`** (upsert desde `prisma/seed-tipos.json`) sobrescribe
  `esquemaFormulario` y `etapas` en BD desde el JSON.

## Implicaciones (la regla)

1. **`seed-tipos.json` es la fuente de verdad de los tipos curados.** Cambios de fondo a
   esos flujos se hacen en el JSON y se aplican con `seed:catalogo`. Eso es lo que sobrevive.
2. **Una edición normal en el admin NO corrompe el flujo** (el merge conserva lo avanzado).
3. **Pero las ediciones del admin a tipos curados viven solo en la BD** → el próximo
   `seed:catalogo` las **revierte** a lo del JSON. El admin es para crear tipos **nuevos**
   del despacho o tocar metadata básica, no para editar los flujos curados.
4. **Borrar** una fila de campo/etapa en el admin sí la quita (el merge no preserva lo
   eliminado) — hasta el próximo reseed, que la restaura.

## Impacto

- **Solo documentación.** Añade requisitos al capability `tramite-catalog`. Sin código,
  sin schema, sin deps.

## Fuera de alcance

- Sincronizar ediciones del admin de vuelta al `seed-tipos.json` (no se hace; sería otro change).
