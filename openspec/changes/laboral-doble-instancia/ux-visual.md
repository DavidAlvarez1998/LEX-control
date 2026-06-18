# UX / visual — laboral-doble-instancia

> **Alcance confirmado:** este change **modifica el formulario ya existente** del "Proceso
> Laboral" y **sus fases** — no crea uno nuevo.

## 0. Base: reutiliza `transiciones-suaves` (no duplicar)

La tecnología visual ya está definida en el change [[transiciones-suaves]] y se **reutiliza**
tal cual:

- **Transición de ruta** (lista → ficha): View Transitions API vía `experimental.viewTransition`
  + `(dashboard)/template.tsx` (cross-fade nativo) + fallback CSS `@supports`. El morph del
  **título** lista→ficha se hace con el helper `vtName("proceso", id)` (ya previsto allí).
- **Aparición de campos condicionales:** keyframe `lex-campo-in` + clase `.lex-campo-reveal`
  (fade + leve `translateY`, ~200ms, solo al montar), aplicada por `formulario-dinamico.tsx`
  cuando el campo tiene `mostrarSi`. Esto **ya cubre** los campos que aparecen al elegir una
  opción.
- **Tokens** `--lex-transition-dur: 200ms` y easing `cubic-bezier(0.22, 1, 0.36, 1)`.
- **Accesibilidad:** `@media (prefers-reduced-motion: reduce)` anula el movimiento.

> Dependencia: este change **asume `transiciones-suaves` aplicado** (o lo arrastra). Sin él,
> los campos igual funcionan; solo aparecen sin animar.

## 1. Específico del laboral · "esta opción abre otro camino"

Cuando una opción despliega una **rama** (p. ej. `decisionAuto = INADMISIÓN` revela el bloque
de subsanación), los campos revelados deben **dejar claro que pertenecen a un camino abierto
por esa elección**, no confundirse con los campos base. Recomendación:

### Bloque de rama (`.lex-rama`)
Los campos de una rama se envuelven en un contenedor con:
- **Acento lateral izquierdo** (borde de 2–3px, color de marca tenue) → señal visual de
  "camino condicional / dependiente".
- **Sangría** (indent) proporcional a la profundidad (rama → sub-rama → sub-sub-rama), para que
  se lea la jerarquía (p. ej. INADMISIÓN → subsanación → decisión tras subsanar).
- **Etiqueta contextual** (chip/línea pequeña arriba del bloque): *"Porque elegiste
  «INADMISIÓN»"* — hace explícito **por qué** aparecen esos campos y de qué decisión cuelgan.
- **Entrada animada** con `.lex-campo-reveal` (la del change de transiciones): el bloque entra
  con fade + `translateY` ~200ms, solo al montar.

### Comportamiento
- Al **cambiar la opción**, la rama anterior se desmonta (React por `key`) y la nueva entra
  animada. No se animan los campos base ya visibles (no parpadean).
- Las ramas mutuamente excluyentes (p. ej. subsanación vs. recurso de rechazo) **nunca** se
  muestran a la vez: solo la que corresponde a la decisión tomada.
- El acento + etiqueta es **presentación**: no cambia `disponibleSi`/`mostrarSi` ni el motor.

```
Decisión del auto:  [ INADMISIÓN ▾ ]
┌▎ Porque elegiste «INADMISIÓN»                 ← chip contextual
│  Escrito de subsanación   [ subir PDF ]        ← .lex-rama (acento + indent + reveal)
│  Fecha en que se subsanó  [ __/__/__ ]
│  Decisión tras subsanar:  [ RECHAZAR ▾ ]
│  ┌▎ Porque elegiste «RECHAZAR»                 ← sub-rama (más indent)
│  │  → Recurso contra el rechazo …
│  └
└
```

## 2. Específico del laboral · orden de los campos dentro de una etapa

Cuando una etapa pide varios datos, deben presentarse en un **orden consistente y predecible**
(el del trámite real), para que el usuario siempre sepa qué viene. Convención:

> **Orden canónico por etapa:**
> `(1) la pregunta/decisión que define la rama` → `(2) FECHA` → `(3) DOCUMENTO(S) PDF` →
> `(4) sub-decisión / observaciones`

Ejemplos (se respeta **fecha antes que documento**, como pediste):
- **Calificación:** Decisión del auto → **Fecha del auto** → **`auto-calificacion.pdf`**.
- **Subsanación:** **Fecha en que se subsanó** → **`escrito-subsanacion.pdf`** → Decisión tras
  subsanar → (si admite) Fecha del auto de admisión → `auto-admision-tras-subsanacion.pdf`.
- **Traslado:** **Fecha de la notificación** → **`notificacion.pdf`**.
- **Contestación:** ¿contestaron? → **Fecha** → **`contestacion.pdf`** (o `auto-silencio.pdf`).
- **Sentencia:** **Fecha de la sentencia** → **`sentencia.pdf`** → Decisión.
- **2ª instancia (cada etapa):** **Fecha** → **documento PDF** (→ decisión donde aplique).

Donde un documento dependa de una opción, el doc va **inmediatamente debajo** del campo que lo
gobierna (anclaje inline ya existente en `datos-proceso.tsx` vía `anclasPorCampo`), conservando
el orden fecha→documento dentro de la rama.

## 3. Las fases en lo visual (stepper agrupado — mejora opcional)

Si se activa la capa de fases (`fase` en las etapas, ver `fases.md`), el stepper agrupa las
etapas por fase (cabecera de fase + etapas dentro) y muestra solo las fases aplicables al caso.
El cambio de fase activa puede usar el mismo cross-fade/`.lex-campo-reveal` para que la
transición entre fases sea coherente con el resto. Opcional; no bloquea las correcciones del
flujo.

## 4. Tareas UX (se suman a `tasks.md`)

- [ ] Confirmar/aplicar `transiciones-suaves` (dependencia visual).
- [ ] `globals.css` (client): clase `.lex-rama` (acento lateral + indent por nivel) reusando
      tokens `--lex-transition-dur`/easing; respetar `prefers-reduced-motion`.
- [ ] `datos-proceso.tsx` / `formulario-dinamico.tsx`: envolver los campos con `mostrarSi` (que
      cuelgan de un select) en `.lex-rama` + chip *"Porque elegiste «X»"* + `.lex-campo-reveal`.
- [ ] Ordenar los campos del esquema laboral según la convención (1)→(4) por etapa
      (fecha antes que documento) — orden del `esquemaFormulario` en el seed.
- [ ] (opcional fases) stepper agrupado por `fase`.
