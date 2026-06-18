# design-color-system

Sistema de color compartido por los dos portales (cliente + admin), basado en tokens
semánticos theme-aware, con reglas de consistencia y contraste. Objetivo: profesional
(índigo/slate, superficies limpias) y amigable (suave, bajo contraste, sin negro/blanco puros).

## ADDED Requirements

### Requirement: Tokens de color semánticos theme-aware
La paleta MUST estar definida como **CSS variables** en `globals.css` (valores para claro y
para `html.dark`) y expuesta como utilidades Tailwind v4 vía `@theme inline`. Los componentes
SHOULD usar esas utilidades en vez de tonos `slate-*`/`indigo-*` crudos.

#### Scenario: Roles definidos una sola vez
- **GIVEN** `globals.css`
- **THEN** existen tokens para: `--bg`, `--surface`, `--surface-muted`, `--border`,
  `--text`, `--text-muted`, `--accent` (+ su `-hover`)
- **AND** cada uno tiene valor para claro y para `html.dark`
- **AND** quedan disponibles como `bg-surface`, `text-muted`, `border-default`, etc.

#### Scenario: Componentes compartidos usan tokens
- **GIVEN** `ui.tsx` (Card/Button), `form-ui.tsx`, `layout.tsx`, `topbar.tsx`, `sidebar.tsx`
- **WHEN** se renderizan en cualquiera de los dos portales
- **THEN** sus superficies/bordes/textos salen de los tokens → cliente y admin se ven idénticos

### Requirement: Jerarquía de profundidad consistente
Las capas de superficie MUST seguir un único escalonado en ambos temas.

#### Scenario: Profundidad clara
- **GIVEN** modo claro
- **THEN** fondo de página = `bg` (slate-100), tarjetas/topbar = `surface` (white), bordes =
  `border` (slate-200)

#### Scenario: Profundidad oscura
- **GIVEN** modo oscuro
- **THEN** fondo = `bg` (slate-950), tarjetas = `surface` (slate-800), chrome (sidebar+topbar)
  = slate-900, bordes = `border` (slate-700) → sidebar y contenido NO son del mismo tono

### Requirement: Un solo acento
El color de acento MUST ser único (índigo). violet/sky SHALL quedar restringidos a decoración
de la landing, nunca a UI funcional.

#### Scenario: Acción primaria / estado activo
- **GIVEN** un botón primario, link o ítem activo
- **THEN** usa `--accent` (indigo-600 claro / indigo-500 oscuro), no otro matiz

### Requirement: Colores semánticos consistentes y suaves
Cada significado MUST tener UN set de tonos (claro + oscuro) reutilizado vía un helper central
(no repetido ad-hoc por pantalla). MUST usar variantes suaves (bg-50/texto-700 en claro; bg
translúcido/texto-300 en oscuro).

#### Scenario: Estado con tono único
- **GIVEN** estados de cliente/proceso/servicio (PROSPECTO, ACTIVO, VENCIDO, DESCARTADO…)
- **WHEN** se pinta su badge
- **THEN** sale de `estadoTono(estado)` central: éxito=emerald, alerta=amber, peligro=red,
  neutral=slate **legible** (no slate-200/500 que se lee como deshabilitado)
- **AND** dinero-negativo usa `rose` (distinto del `red` de error/peligro)

#### Scenario: Sin estados sin dark
- **GIVEN** cualquier badge/píldora de estado
- **THEN** SIEMPRE define su variante `dark:` (no se permite `bg-slate-200 text-slate-500` sin
  `dark:`, que rompe en oscuro)

### Requirement: Contraste mínimo accesible
El texto MUST cumplir WCAG AA (≥ 4.5:1 texto normal). El texto "muted" SHOULD ser como mínimo
`--text-muted` (slate-500/400), nunca slate-400 sobre superficies claras tipo slate-100.

#### Scenario: Texto secundario legible
- **GIVEN** un conteo/hint sobre una superficie clara (white o slate-100)
- **THEN** usa `text-muted` (≥ slate-500), no `text-slate-400`

### Requirement: Calidez sin perder seriedad
La sensación amigable MUST lograrse por suavidad (superficies claras, esquinas redondeadas,
sombras tenues, espaciado, bajo contraste), NO por saturar el acento. El texto principal SHALL
ser `--text` (slate-800), nunca negro puro; las superficies, nunca negro/blanco a contraste
máximo.
