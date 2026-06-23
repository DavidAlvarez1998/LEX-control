# Plan — Proceso Laboral (Ley 2452/2025)

> SDD por caso · paraguas: [proposal.md](proposal.md) · doc fuente:
> `roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`
> análisis previo: `openspec/changes/laboral-flujo-doc/{validacion,design,tasks}.md` +
> `openspec/changes/laboral-doble-instancia/`

## Estado actual (verificado en seed-tipos.json)

- **54 campos, 23 etapas.** 4 flujos = rol (Demandante/Demandado) × instancia (Única/Doble).
  4 terminales (`archivado`, `archivado_rechazo`, `terminada`, `terminada_conciliacion`).
- Ficha **seccionada** (`seccionesLaboral` en `datos-proceso.tsx`): los campos se agrupan en
  secciones por etapa y cada sección renderiza su propio `FormularioDinamico`. Documentos
  anclados inline por campo. Sin plantillas generadas (adjunta) — **correcto**.

## Problemas del doc (a reconciliar / limpiar)

1. **Sub-flujo de reconvención muerto**: campos como `fechaAutoReconvencion`,
   `fechaSubsanacionReconvencion`, `decisionTrasSubsanacionReconvencion` existen en el
   esquema pero **ninguna etapa los usa** (el flujo solo captura `decisionReconvencion` +
   fecha + doc). → **limpiar** (eliminar los muertos) o modelar sus etapas. Recomendado:
   limpiar (decisión ya tomada en `laboral-flujo-doc/validacion.md`).
2. **2ª instancia sin fuente documental**: `radicado2inst`, `fechaSustentacion`,
   `fechaAudiencia2inst`, `fechaSentencia2inst`, `decisionSegundaInstancia` se agregaron en
   `laboral-doble-instancia` sin estar en el .docx del 15 de junio. → confirmar con el
   usuario si son extensión deseada (probablemente sí) y dejarlo registrado.
3. **Orden de etapas por instancia**: preparación/citación de audiencia se invierten entre
   única y doble; `seccionesLaboral` ya lo maneja con `tituloEtapa(...doble)`. Solo verificar.

## Brechas vs. mínima cuantía

- **Consumo de la Rama** (principal): el botón no aparece (faltan llaves; ver abajo).
- Plantillas: **N/A** (adjunta). No es brecha.
- Motor / terminales / documentos anclados: en paridad.

## Enganche con la Rama Judicial

Llaves: `fechaRadicacion` ✅ (campo soloFicha, solo si rol=Demandante) · `radicado` ❌ ·
`juzgado` ❌. El radicado vive en `proceso.radicado` y el despacho en
`proceso.despachoJuzgado` (capturados en el bloque "Radicación" de la **creación**, no en
el esquema dinámico de la ficha). Por eso el gate de mínima cuantía no dispara y, además,
**la ficha seccionada no tiene un campo `radicado` editable** donde colgar el botón.

**Opción B adaptada:** el botón "Actualizar" va donde el laboral edita el radicado — el
header `RadicadoDato` de la ficha y/o el bloque "Radicación" de la creación — autollenando
`proceso.despachoJuzgado` + el campo `fechaRadicacion`. (No tiene sentido inyectarlo dentro
de `seccionesLaboral`, porque ahí el radicado no es un campo.)

## Tareas — estado (2026-06-23)

Auditoría: **sin campos duplicados, sin referencias rotas** (54 campos).

1. ✅ **Rama (Opción B)** — la ficha ya tenía el botón por el encabezado `RadicadoDato`
   (laboral no tiene campo `radicado` en el esquema → el gate `!tiene("radicado")` lo
   muestra). Se agregó además el botón al **form de creación** (bloque "Radicación"):
   rellena juzgado y agrega la contraparte como sujeto procesal, igual que los verbales.
2. ❌➡️✅ **"Reconvención muerta": era falso.** El sub-flujo de reconvención **sí está
   modelado y vivo**: cadena `mostrarSi` completa (`hayReconvencion` solo en doble instancia
   → `decisionReconvencion` → subsanación → notificación → contestación → silencio) y sus
   **documentos anclados** en la etapa `contestacion` vía `opcionalesSi` (reconvencion.pdf,
   auto-reconvencion.pdf, subsanacion-reconvencion.pdf, …). No se elimina nada.
3. ➖ **2ª instancia**: presente (remision→sustentacion→audiencia→sentencia); es extensión
   sobre el .docx del 15-jun (aceptada). Registrado; sin cambios.
4. ✅ **Autollenado**: el botón del encabezado (sincronizarActuaciones) llena
   `despachoJuzgado` (columna) y `fechaRadicacion` (campo, si rol=Demandante); el de creación
   llena juzgado + contraparte.
5. ✅ **Verificado**: `createProceso` de laboral crea OK; flujos laborales con tests verdes.

**Conclusión:** el laboral **no requiere limpieza de seed** (la "reconvención muerta" no
existía). Solo se sumó el botón de la Rama en creación. Pendiente smoke en vivo.
