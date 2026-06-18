# transiciones-suaves

## Por qué

El usuario pide "transiciones suaves" en los portales y, sobre todo, **qué es lo más
profesional**. Hoy la navegación **entre páginas del dashboard es un corte seco**: no hay
transición de ruta. Las microtransiciones de hover/focus ya existen (Tailwind `transition-*`)
y la **landing** ya tiene animaciones ricas (`lex-fade-up`, `lex-reveal`, blobs, sheen en
`globals.css`, con guard `prefers-reduced-motion`). El hueco es la **transición al cambiar de
vista** dentro de la app de trabajo.

En una herramienta B2B legal, "profesional" no es "lo que más se mueve": es **sutil, rápido y
consistente** (≈200ms, solo `opacity`/`transform` → 60fps en GPU, mismo easing en toda la app,
respeta `prefers-reduced-motion`). Es lo que hacen Linear/Stripe/Vercel/Clio.

## Decisión: arrancar por View Transitions (no framer-motion)

Se evaluaron 3 caminos:

| Opción | Qué da | Costo | Deps |
| --- | --- | --- | --- |
| **A. `template.tsx` + CSS fade** | Cross-fade de ruta hecho a mano | bajo | 0 |
| **B. View Transitions API (nativo)** | Cross-fade nativo + elemento compartido (lista→ficha) | bajo-medio (experimental en Next 16) | 0 |
| **C. framer-motion** | Animaciones declarativas complejas | medio + ~35kb bundle | +1 |

**Se elige B**, porque su **comportamiento por defecto YA es el cross-fade** que daría A → no
hay migración A→B; A no se desperdicia, vive como **fallback CSS** para navegadores sin
soporte. **C se descarta** por ahora: sobre-ingeniería y peso de bundle para navegación de un
dashboard. Stack verificado: **Next 16.2.7 + React 19.2.4** en ambos portales (soporta
`experimental.viewTransition` + el componente `ViewTransition` de React 19.2).

Lo profesional = **B con red de seguridad A**, sin C.

## Qué cambia

### 1. Activar View Transitions (config, ambos portales)
`next.config.ts`: `experimental: { viewTransition: true }` en `lex-control-client` y
`lex-control-admin`.

### 2. Cross-fade de ruta por defecto (ambos portales)
`src/app/(dashboard)/template.tsx` (nuevo en cada portal). `template.tsx` **se re-monta en
cada navegación** (a diferencia de `layout.tsx`), así dispara la transición. Envuelve
`children` con el mecanismo de View Transitions; el default del navegador hace el cross-fade.
Solo aplica al **dashboard** (no a login/activar/landing, que ya tienen lo suyo).

### 3. Fallback + tokens en CSS (`globals.css`, ambos portales)
- Variables de transición consistentes: `--lex-transition-dur: 200ms` y el easing ya usado
  `cubic-bezier(0.22, 1, 0.36, 1)`.
- Reglas `::view-transition-old/new` con esa duración (cross-fade corto, profesional).
- `@supports not (...)`: fallback CSS keyframe (la "opción A") para navegadores sin View
  Transitions → la app igual entra con un fade suave.
- Extender el bloque `@media (prefers-reduced-motion: reduce)` ya existente para anular
  también las view-transitions.

### 4. Predeterminado para vistas futuras (convención)
El cross-fade de ruta queda **heredado por construcción**: `template.tsx` envuelve TODO el
grupo `(dashboard)`, así que **cualquier página nueva bajo `(dashboard)/` obtiene la
transición sin tocar nada**. Para que el elemento-compartido también sea trivial de aplicar:
- **Helper `vtName(scope, id)`** en `src/lib/` de cada portal → devuelve el objeto de estilo
  `{ viewTransitionName: ... }` (sanitizado) para reusar en listas→detalle futuras en una
  línea: `style={vtName("proceso", t.id)}` en la fila y el mismo en el contenedor de la ficha.
- **Nota en `CLAUDE.md`** (sección Frontends): convención de transiciones para que futuras
  sesiones la sigan por defecto (heredar el cross-fade; usar `vtName` en lista→detalle;
  ~200ms, opacity/transform, respetar reduced-motion).

### 5. Aparición suave de campos condicionales (client)
Los formularios dinámicos del client despliegan/ocultan campos según `mostrarSi` (una opción
habilita otros). Hoy los campos revelados **aparecen de golpe**. Se agrega una entrada suave
(fade + leve `translateY`, ~200ms) que corre **solo al montar** el campo recién revelado:
- `globals.css`: keyframe `lex-campo-in` + clase `.lex-campo-reveal` (+ reduced-motion).
- `formulario-dinamico.tsx`: aplica `lex-campo-reveal` al wrapper **solo si `campo.mostrarSi`**
  → los campos base no parpadean al cargar; React conserva por `key` los ya visibles (no
  re-animan); cubre **creación y ficha** (ambas usan `FormularioDinamico` vía `datos-proceso`).

### 6. Un caso de elemento compartido (showcase, solo client)
La lista de procesos del client es una **tabla** (`<tr key={t.id}>`), no cards, así que un
"row → ficha completa" se ve forzado. Showcase v1: **morph del título** — el `PageHeader` de
la ficha (`procesos/[id]`) comparte `view-transition-name` (vía `vtName`) con el título de la
fila correspondiente, demostrando el efecto premium sin un morph antinatural. Degrada al
fallback / swap instantáneo donde no haya soporte o con reduced-motion.

## Impacto
- **Frontend client + admin** (espejado):
  - `next.config.ts` — agregar `experimental.viewTransition: true` (hoy config vacía).
  - `src/app/(dashboard)/template.tsx` — **nuevo** (no existe en ninguno); envuelve el
    contenido de página, que el `layout.tsx` renderiza dentro de `<main>` → cross-fade
    acotado al área de contenido (sidebar/topbar fijos).
  - `src/app/globals.css` — tokens `--lex-transition-dur` + `::view-transition-old/new(root)`
    + `@supports not(...)` fallback + extender el bloque `prefers-reduced-motion` existente.
  - `src/lib/` — helper `vtName(scope, id)` (nuevo).
- **Solo client (showcase)**: `view-transition-name` (vía `vtName`) en el título de la fila
  de la lista de procesos y en el `PageHeader` de la ficha.
- **`CLAUDE.md`**: nota de convención en la sección Frontends.
- **Schema / backend / API**: sin cambios.
- **Bundle**: sin dependencias nuevas (0 kb).

## Rollback
Reversible y de bajo riesgo:
1. Quitar `experimental.viewTransition` de los dos `next.config.ts`.
2. Borrar los `template.tsx`.
3. Revertir el bloque de `::view-transition-*` / `@supports` en `globals.css`.
Sin estado persistido, sin migración, sin deps. El fallback CSS y `prefers-reduced-motion`
garantizan que, ante cualquier aspereza del API experimental, la app siga andando suave.

## Fuera de alcance
- **framer-motion** y animaciones declarativas complejas de componentes (listas con stagger,
  drag, gestos): no se adoptan ahora (opción C, descartada por peso/complejidad).
- Animaciones de la **landing** (ya existen) y de **login/activar**: intactas.
- Transiciones de elemento compartido en TODAS las vistas: solo 1 caso demo; el resto se
  decide después según cómo se vea.

## Decisiones del usuario (2026-06-18)
- "¿Qué es lo más profesional?" → **sutil + ~200ms + opacity/transform + consistente**, no
  framer-motion.
- "¿Tendríamos A y B?" → no compiten en la misma transición; **B de base, A como fallback**.
- "Para no migrar de A a B, mejor arrancar con B" → confirmado: el default de B ya cubre A;
  se arranca por **B**.
