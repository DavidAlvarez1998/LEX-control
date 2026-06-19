# ui-tooltip

## Por qué

Hasta ahora, para explicar un control al pasar el mouse se usaba el atributo nativo `title`
(inconsistente entre navegadores, lento en aparecer, sin estilo, no accesible por teclado de forma
uniforme). El usuario pidió un **componente Tooltip "pro" reutilizable** y **estandarizarlo** para
que de aquí en adelante toda explicación-al-hover use ese componente y no `title`.

## Qué cambia

Capability nueva **`ui-tooltip`**: un primitivo presentacional compartido `Tooltip` en
`src/components/ui.tsx` de **ambos portales** (`lex-control-client` y `lex-control-admin`), idéntico
en los dos. Reemplaza el uso de `title` para explicaciones de UI.

- **API del componente:** `<Tooltip content={...} side?="top|bottom|left|right" className?>{children}</Tooltip>`.
- **Comportamiento:** muestra `content` al **hover** y al **enfocar con teclado** (`focus-within`),
  accesible (`role="tooltip"`), CSS-only (sin estado JS), no bloquea clics (`pointer-events-none`),
  theme-aware (claro/oscuro), aparición suave (~150ms).
- **Primera adopción:** los botones **"Míos" / "Todos"** de la vista Clientes del portal cliente
  (explican qué significa cada vista) — ya migrados de `title` al componente.

> Convención: a partir de ahora, preferir `<Tooltip>` sobre `title` para cualquier explicación
> contextual en hover/focus. `title` queda solo para casos triviales o no-React.

## Impacto

- `lex-control-client/src/components/ui.tsx`: + `Tooltip`.
- `lex-control-admin/src/components/ui.tsx`: + `Tooltip` (idéntico).
- `lex-control-client/.../clientes/page.tsx`: botones Míos/Todos usan `Tooltip`.
- Sin dependencias nuevas, sin cambios de API/backend. Tailwind v4 (named group `group/tt`).

## Rollback

Aditivo y de bajo riesgo: quitar el export `Tooltip` y volver los call-sites a `title`. No afecta
datos ni contratos.
