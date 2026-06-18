# design-color-system

## Por qué

El usuario pide **validar el sistema de color/tema** (la relación de colores) y recomendar
mejoras para que el proyecto se vea **más profesional y psicológicamente amigable**. Tras el
re-theming reciente (fondo claro suavizado + jerarquía de profundidad en oscuro) afloraron
**inconsistencias** y la falta de un **sistema** (todo son clases Tailwind crudas, sin tokens).
Este change documenta el diagnóstico y define el sistema objetivo (vía SDD); la aplicación va
por fases.

## Diagnóstico (lo que hay hoy)

- **Sin tokens de color.** Todo es Tailwind crudo (`slate-*`, `indigo-*`). No hay `@theme` de
  color ni variables semánticas → cada pantalla repite y diverge.
- **Acento:** `indigo-600` (botones, links, focus, activos). Inequívoco y bien elegido para
  legal/B2B. + `violet`/`sky` solo decorativos en la landing.
- **Neutrales:** 100% `slate-*` (sin gray/zinc mezclados) — bien. Pero conviven **~11 tonos de
  gris** sin roles definidos (slate-50/100/200/300/400/500/600/700/800/900/950).
- **Semánticos:** éxito `emerald`, error `red`, alerta `amber`, dinero-negativo `rose`. Bien
  diferenciados, pero **dos rojos** (red error + rose egresos) y variantes dark inconsistentes.

## Hallazgos (inconsistencias reales, archivo:línea)

**Alta**
1. `EstadoBadge` de Procesos (cerrado/archivado) `bg-slate-200 text-slate-500` **sin `dark:`**
   → contraste roto en oscuro (`procesos/page.tsx`).
2. `Card` difiere **cliente vs admin**: cliente `bg-white dark:bg-slate-800`, admin
   `bg-slate-50 dark:bg-slate-700` → los dos portales se ven distintos (`ui.tsx`).
3. Borde del **topbar** `dark:border-slate-800` vs `slate-700` del resto → disonancia.

**Media**
4. Mismo badge índigo con dark distinto: `dark:bg-indigo-500/10` (procesos) vs
   `dark:bg-indigo-950/40` (clientes). Pasa también con amber.
5. `red-100` en un badge (`datos-proceso.tsx:291`) vs `red-50` en el resto.
6. Botón "ghost"/toggle con `dark:border-slate-700` (procesos) vs `slate-600` (form-ui).
7. "Descartado" usa gris (`slate-200/500`) → no comunica el estado; igual "alerta inactiva".

**Baja (contraste WCAG)**
8. Conteo gris `text-slate-400` sobre tarjeta `slate-100` ≈ **3.5:1** (AA pide 4.5:1)
   (`procesos/page.tsx`, tarjeta "No actualizado").
9. Spans que omiten `dark:text-*` explícito (heredan) — frágil (`inicio/page.tsx:154`).

## Recomendaciones — profesional + psicológicamente amigable

### 1. Tokens semánticos (la raíz del orden)
Definir en `globals.css` una capa de **CSS variables theme-aware** + mapearlas a utilidades
Tailwind v4 (`@theme inline`). Reduce ~11 grises sueltos a **5 roles**:

| Token | Claro | Oscuro | Uso |
| --- | --- | --- | --- |
| `--bg` | slate-100 | slate-950 | fondo de página |
| `--surface` | white | slate-800 | tarjetas, topbar |
| `--surface-muted` | slate-50 | slate-900 | inputs, "No actualizado" |
| `--border` | slate-200 | slate-700 | bordes/divisores |
| `--text` / `--text-muted` | slate-800 / slate-500 | slate-100 / slate-400 | texto |
| `--accent` | indigo-600 | indigo-500 | primario/activo |

→ `bg-surface`, `text-muted`, `border-default`… **una sola fuente de verdad** para ambos
portales. Migración incremental (los componentes compartidos primero: `ui.tsx`, `form-ui.tsx`,
`layout`, `topbar`, `sidebar`).

### 2. Psicología del color (por qué estas elecciones)
- **Índigo/azul = confianza, calma, competencia** → ideal para un producto legal. **Mantener**
  indigo como único acento; no competir con violet/sky fuera de la landing.
- **Slate (gris frío) = profesional**, pero en exceso puede sentirse **frío/impersonal**. La
  calidez/amabilidad se logra con: **superficies suaves** (blanco sobre gris muy claro, ya
  aplicado), **esquinas redondeadas** (rounded-xl, ya), **sombras tenues**, **aire/espaciado**
  y **bajo contraste** (nada de negro/blanco puros — ya usamos slate-800, no #000).
- **Semánticos suaves** (bg-50 + texto-700 en claro; bg translúcido + texto-300 en oscuro):
  comunican sin gritar → percepción amigable. **Mantener**.
- Opcional a explorar: un neutral **un punto más cálido** (p. ej. mezclar 3-5% de calidez en
  los grises) para sentir menos "clínico", sin perder seriedad. Riesgo bajo si se hace por
  token.

### 3. Consistencia de profundidad (ya casi, dejarlo como regla)
- **Claro:** `bg`(slate-100) → `surface`(white) → `border`(slate-200).
- **Oscuro:** `bg`(slate-950) → `surface`(slate-800) → `border`(slate-700); chrome
  (sidebar+topbar) en slate-900. (Ya aplicado tras el último ajuste; falta tokenizarlo.)

### 4. Arreglar los hallazgos puntuales (1-9 de arriba)
Pequeños, alto impacto: `EstadoBadge` con dark; igualar `Card` cliente↔admin; topbar border;
unificar variantes dark de índigo/amber a una; `red-100→red-50`; subir el gris del conteo a
`slate-500`; estados "descartado/inactivo" con un gris **legible** (no slate-200/500).

### 5. Una escala de "estado" central (en vez de repetir badges)
Un único helper `estadoTono(estado)` (ya existe `bits.tsx` en contable) reutilizado por
clientes/procesos/servicios/equipo → un solo set de tonos por significado.

## Impacto
- **Frontend (ambos portales), solo presentación.** `globals.css` (tokens) + componentes
  compartidos (`ui.tsx`, `form-ui.tsx`, `layout.tsx`, `topbar.tsx`, `sidebar.tsx`) + un helper
  de tonos de estado. Sin schema, sin lógica, sin deps.
- Migración **incremental** (tokens primero, luego barrido de clases crudas → utilidades token).

## Fuera de alcance
- Tipografía, espaciado, iconografía (otro change si se quiere).
- Rediseño de la landing (sus gradientes/blobs se mantienen).

## Decisiones del usuario (2026-06-18)
- Pidió validar la relación de colores y mejorar para verse **más profesional y amigable**.
- Pendiente confirmar: ¿migramos a **tokens** (recomendado) o solo arreglamos las
  inconsistencias puntuales? ¿exploramos el neutral **un punto más cálido** o mantenemos slate?
