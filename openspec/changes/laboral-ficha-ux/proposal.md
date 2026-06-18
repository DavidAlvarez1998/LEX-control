# laboral-ficha-ux

## Por qué

En la ficha de un Proceso Laboral **ya creado**, el formulario de datos (`DatosProceso` en
edición) renderiza TODOS los campos en una grilla plana de 2 columnas
(`grid-cols-1 sm:grid-cols-2`). Como el laboral tiene ~30 campos de muchas etapas, la grilla
**empareja campos no relacionados** (p. ej. "Decisión del auto" a la izquierda y una fecha de
otra cosa a la derecha), y no hay separación por etapa. El usuario (abogado): *"a la izquierda
tengo la opción de si el auto fue admitido o no y a la derecha la fecha, lo cual hace que sea
raro y toca buscar dónde iría cada cosa"*.

## Qué cambia

**Solo UX/presentación. NO cambia la lógica** (gating de etapas, validación al guardar,
auto-avance, condiciones, plazos, anclaje de documentos — todo intacto).

Para `grupo === "LABORAL"`, la ficha en edición se reorganiza en **secciones por etapa**, en
el orden del flujo, cada una con su **encabezado** y sus campos en **una sola columna**
(lectura vertical, sin el emparejamiento raro izquierda/derecha). Cada documento sigue inline
bajo su campo (anclaje ya existente). Secciones (según las etapas disponibles con los datos
actuales):

1. **Presentación de la demanda** — rol, instancia, ¿requiere poder?, fecha de radicación.
2. **Calificación de la demanda (auto)** — decisión del auto, fecha del auto, observaciones.
3. **Subsanación** — decisión tras subsanación, fecha (solo si inadmisión).
4. **Recurso contra el rechazo** — recurso, decisión (solo si rechazo).
5. **¿Retiro de la demanda? (art. 67)** — hayRetiro.
6. **Traslado y notificación** — fecha de notificación.
7. **Contestación (reforma / reconvención)** — contestaron, fechas, reforma, reconvención…
8. **Audiencia** — conciliable, fecha audiencia, conciliación, excepciones/saneamiento…
9. **Sentencia y recurso** — fecha sentencia, decisión, recurso, forma, decisión recurso.

Las secciones cuyas etapas no aplican (p. ej. Contestación en única instancia, o Subsanación
si el auto no fue inadmitido) **no se muestran** — se reutiliza el `disponibleSi`/`mostrarSi`
existente, sin nueva lógica.

## Cómo (frontend, acotado a laboral)

- `datos-proceso.tsx`: helper de presentación `seccionesLaboral(etapas, esquema)` que agrupa
  los campos por la etapa que los introduce (camposRequeridos + campos de sus condiciones +
  campos dependientes vía `mostrarSi`), en orden de `orden`. Es **solo agrupación visual**: no
  decide requeridos ni habilita nada.
- En la rama `grupo === "LABORAL"` de la edición, en vez de un `FormularioDinamico` plano se
  renderiza una sección por grupo: encabezado + `FormularioDinamico` (subset de campos, una
  columna) + los slots de documentos de esos campos.
- Para `grupo !== "LABORAL"` (DdP/tutela) **nada cambia**.

## Impacto

- Specs: `tramite-management` (nota de presentación; no altera requisitos funcionales).
- Código: solo `lex-control-client/src/components/datos-proceso.tsx` (+ quizá un className).
- Sin cambios en API, seed, validación ni motor. Extiende [[laboral-flujo-doc]].
