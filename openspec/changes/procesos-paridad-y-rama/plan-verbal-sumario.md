# Plan — Proceso verbal sumario (civil)

> SDD por caso · paraguas: [proposal.md](proposal.md) · doc fuente:
> `roadmap-docs/JURISDICCIÓN ORDINARIO CIVIL- PROCESO VERBAL SUMARIO.docx`
> análisis previo: `openspec/changes/procesos-verbales-civil/{doc-verbal-sumario,validacion-vs-doc}.md`

## Estado actual (verificado en seed-tipos.json)

- **104 campos, 12 etapas.** Única instancia (CGP 390–392): sin apelación ni 2ª instancia.
  Audiencia única (art. 392), traslado 10 días hábiles, subsanación 5 días.
- Tiene ya: reposición contra auto admisorio, sentencia anticipada que gatea/omite la
  audiencia, módulo de medidas cautelares inline, `demandaModo` (verbal/escrita) que
  condiciona el PDF.

## Problemas del doc (a reconciliar)

1. **Reconvención visible**: el art. 392 CGP **prohíbe** reconvención en sumario, pero el
   esquema heredó campos de reconvención del verbal. → ocultarlos (`mostrarSi:false` o
   filtrar por tipo) para que no aparezcan.
2. **Excepciones de mérito**: en sumario se resuelven **en la audiencia única**, no en un
   traslado previo. Confirmar que no haya etapa/campos de "excepciones previas" sueltos.
3. Nomenclatura del radicado: el esquema usa `radicadoJudicial`/`juzgado`/`correoJuzgado`
   (no la llave `radicado` ni `fechaRadicacion`). Relevante para la Rama (abajo).

## Brechas vs. mínima cuantía

- **Consumo de la Rama** (principal): el botón no aparece (faltan llaves; ver abajo).
- Acta de la audiencia única: anclar `acta-audiencia.pdf` a la etapa `audienciaUnica`.
- Plantillas: **N/A** (no genera; adjunta). No es brecha.

## Enganche con la Rama Judicial

Llaves: `juzgado` ✅ · `radicado` ❌ (usa `radicadoJudicial` y/o columna `proceso.radicado`)
· `fechaRadicacion` ❌. Mismo patrón que verbal → **Opción B**: generalizar el botón sobre
la columna canónica + autollenar `juzgado` (resolviendo el `radicadoJudicial` vs. columna).

## Tareas

1. ✅ **Botón Rama** — resuelto vía Opción B (encabezado `RadicadoDato`); ya funciona en sumario.
2. ✅ **Quitar reconvención** (art. 392 la prohíbe) — **HECHO** (2026-06-23): eliminados los 7
   campos `hayReconvencion`/`recon*` del esquema (104→97 campos), renombrada la etapa
   `contestacion` "Contestación y reconvención" → "Contestación" y removido el
   `opcionalesSi` de `reconvencion.pdf`. Aplicado a la DB (esquemaVersion++); 12/12 tests de
   flujos verbales verdes; verbal **no** se tocó (conserva su reconvención).
3. ✅ **Acta de audiencia** — ya estaba anclada: la etapa `audienciaUnica` tiene
   `acta-audiencia-unica.pdf`. Sin cambios.
4. ⏳ **Normalizar `radicadoJudicial`** (campo del esquema) vs. la columna canónica
   `proceso.radicado` — **diferido**: la Opción B hizo el botón independiente de esa llave,
   así que es limpieza no bloqueante (baja prioridad; riesgo de datos).
5. ✅ **Verificado**: única instancia, audiencia única gateada por `sentenciaAnticipada`,
   conciliación total → terminal, rechazo → archivo (tests).
