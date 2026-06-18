# laboral-flujo-doc

## Por qué

La vista "Procesos Laborales" (Ley 2452/2025) **no refleja el documento fuente**
`openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx` — la biblia del
caso. El usuario (abogado, rol JURIDICO) lo verificó: *"veo que nada de lo que está en el doc
está en este form"*. Problemas concretos:

1. **El modelo inventa campos que el doc no pide.** Pide `pretensiones` (multiselect de 14
   ítems) y `hechos` (texto largo) como obligatorios al crear. El doc **nunca** los pide: la
   demanda es un **PDF que se adjunta** (`DEMANDA- PDF // PRUEBAS- PDF // ANEXOS - PDF`,
   doc líneas 11-13, 68-70, 151-153, 189-191). El criterio "adjuntar, no tipear" sale
   **directo de este doc**, no de ninguna otra vista de la app.

2. **El orden del form no es el del doc.** Tras elegir *demandante + única instancia*, el
   doc espera: subir **demanda, pruebas, anexos**, **fecha de radicación**, **# radicado**,
   **juzgado/corporación** (doc 9-17). Hoy esos documentos quedan dispersos y el **# radicado
   + juzgado** salen en el bloque genérico "Datos judiciales" **al fondo** del formulario,
   no en el orden del doc.

3. **El flujo solo ramifica por instancia (única/doble), no por rol.** El doc desarrolla
   **4 flujos completos y distintos** (doc líneas 3-247): demandante/única (7-63),
   demandante/doble (64-143), demandado/única (145-182), demandado/doble (183-247). El
   modelo actual los colapsa en uno y solo se bifurca por `tipoInstancia`.

4. **No hay etapa de "decisión del auto".** El doc: tras la admisión va un *auto* (PDF) cuya
   **decisión es ADMISIÓN / INADMISIÓN / RECHAZO**, y **cada una abre un flujo distinto**
   (doc 21-32, 78-89): inadmisión → subsanar 5 días hábiles; rechazo → recurso. Hoy existe
   `decisionAdmision` pero el flujo no la respeta del todo y el "auto pdf" no está explicado.

## Qué cambia

Se **recrea** el `TipoProceso` "Proceso Laboral" siguiendo el doc paso a paso, en orden, como
una máquina de etapas con ramas. El detalle stage-by-stage de los 4 flujos está en
`design.md`. En resumen:

### 1. Demanda = adjuntar PDF (no tipear) — doc-fiel
Se eliminan `pretensiones` y `hechos` como campos del formulario. La demanda se modela como
documentos: `demanda.pdf` (req), `pruebas.pdf` (opc), `anexos.pdf` (opc). El intake al crear
queda corto: **rol**, **tipo de instancia**, **¿requiere poder?**, los **documentos de la
demanda**, **fecha de radicación** (solo demandante), **# radicado** y **juzgado** — en ese
orden (= etapa *Presentación* del doc).

### 2. Motor: condiciones compuestas (cambio acotado y retro-compatible)
`Condicion` pasa de solo `{campo, igualA}` a admitir también `{todas: Condicion[]}` (AND) y
`{alguna: Condicion[]}` (OR). Necesario para flujos que dependen de **dos** campos a la vez:
p. ej. la etapa **Admisión existe salvo en demandado+única** →
`disponibleSi: {alguna: [{rol: "Demandante"}, {tipoInstancia: "Doble instancia"}]}`. Se
actualiza `evaluarCondicion` en API (`esquema.ts`) y cliente (`lib/procesos.ts` +
`procesos/[id]` inline). Las condiciones existentes (DdP/tutela) siguen funcionando sin
cambios.

### 3. Etapas en el orden y con las ramas del doc (4 flujos)
Una sola lista de `etapas` parametrizada por `rol` y `tipoInstancia` vía `disponibleSi`
(compuesto) y campos `mostrarSi`. Cubre: Presentación → Admisión (decisión del auto:
ADMISIÓN/INADMISIÓN→subsanación 5 días háb./RECHAZO→recurso) → ¿retiro art. 67? → Traslado y
notificación (10 días háb. para contestar) → Contestación (solo doble: contestación/reforma/
reconvención→decisión del juez) → Preparación de audiencia → Citación → **Audiencia única**
(única) **o Audiencia art. 77 + art. 80** (doble) → Sentencia → Recurso (**reposición** en
única / **apelación** en doble, 3 días) → Terminación / Archivo. Plazos "créele al doc" (ver
[[plazos-dias-habiles-creele-al-doc]]): contestación 10 días hábiles, subsanación 5 días
hábiles, recurso 3 días.

### 4. Form de creación en el orden del doc (solo laboral)
Para `grupo === "LABORAL"` el formulario de creación se ordena como la etapa *Presentación*
del doc: rol → instancia → ¿requiere poder? → **documentos de la demanda** → **fecha de
radicación** (demandante) → **# radicado + juzgado** (el bloque "Datos judiciales" se reubica
aquí y se recorta a radicado+juzgado; cuantía no se pide al crear porque la instancia se elige
directo). El resto del ciclo ocurre en la ficha, etapa por etapa.

## Impacto

- **Specs:** `tramite-catalog` (condiciones compuestas + esquema/etapas del laboral),
  `tramite-management` (gating/branching de las etapas laborales).
- **Motor (API):** `esquema.ts` (`Condicion` + `evaluarCondicion`); el resto del motor
  (auto-avance, gating, plazos) **no cambia** — solo aprende a evaluar AND/OR.
- **Seed:** se reescribe la entrada "Proceso Laboral" de `prisma/seed-tipos.json` y se
  re-seedea (`pnpm push` no; solo `seed-catalogo` que hace upsert + `esquemaVersion++`).
- **Cliente:** `lib/procesos.ts` (tipo `Condicion` + `evaluarCondicion`),
  `procesos/[id]/page.tsx` (uso inline), `procesos/nuevo/page.tsx` (orden del form laboral),
  `formulario-dinamico.tsx` si hace falta.
- **Reemplaza** el modelo del change archivado `procesos-laborales` (que era v1, solo
  ramificaba por instancia). Ver [[sdd-procesos-laborales]].
- **Compatibilidad:** procesos laborales ya creados con el esquema viejo quedan con datos de
  campos que dejan de existir (`pretensiones`/`hechos`) — quedan ignorados (no rompen). No hay
  migración de datos (entorno demo).

## Decisiones a confirmar con el usuario (antes de implementar)
1. **Demanda = adjuntar PDF**, eliminando `pretensiones`/`hechos` (doc-fiel). ¿OK?
2. **Tocar el motor** para condiciones compuestas (AND/OR). Es la vía limpia para los 4
   flujos; la v1 fue "sin tocar el motor", esta sí lo extiende (mínimo y retro-compatible).
3. **# radicado / juzgado** se reubican al orden del doc reusando las columnas reales
   `Proceso.radicado`/`despachoJuzgado` (no se duplican en `datos`), preservando la búsqueda
   global por radicado.
