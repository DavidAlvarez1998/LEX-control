# procesos-orden-reciente

## Por qué

En el portal cliente, las vistas planas `/procesos?vista=todos` y `?vista=mios`
(change [[client-procesos-vista-todos]]) ordenan **siempre** por vencimiento
(deadline-first): vencidos → por vencer → al día → sin fecha → cerrados. Es el
default correcto para "qué atender primero", pero el abogado no tiene forma de
ver **qué se tocó de último** (lo recién creado o editado) cuando esa es la
pregunta — p. ej. retomar el proceso que acaba de trabajar, sin importar su
vencimiento.

## Qué cambia

Agregar un selector de **orden** en la barra de filtros, tanto en la **vista
plana** (`Todos` / `Míos`) como en la **lista de un tipo** (nivel 3 del
catálogo), con dos opciones:

```
Ordenar:  [ Más urgentes ]   [ Recién modificados ]
```

- **Más urgentes** (default, sin cambio): `orden=vencimiento` — el orden
  deadline-first actual.
- **Recién modificados**: `orden=reciente` — por **última creación o edición**,
  más reciente primero.

## Hallazgo clave (por qué es un cambio chico)

El backend **ya** soporta este orden: en `procesos.repository.ts`, cuando
`orden ≠ "vencimiento"` la lista usa `orderBy: { updatedAt: "desc" }`, y
`updatedAt` es `@updatedAt` de Prisma → se actualiza tanto al **crear** como al
**editar / mover etapa** (`updateProceso`, `moverEtapa`, autoavance). Es decir
"última fecha de creación o edición" = `updatedAt desc`, ya existente y con
paginación SQL nativa (a diferencia del orden por vencimiento, que es en memoria).

El único trabajo real es de UI: la vista plana tenía `orden` **fijo** en
`"vencimiento"` y no exponía la alternativa. No se toca el API.

## Alcance

- `lex-control-client`:
  - `lib/procesos-api.ts` — tipo `orden?: "vencimiento" | "reciente"`.
  - `app/(dashboard)/procesos/page.tsx`:
    - `ListaProcesosPlana` (vista plana) — estado `orden`, control segmentado,
      reset de página al cambiar, subtítulo coherente; pasa `orden` al API
      (orden **server-side**, con paginación).
    - `CatalogoProcesos` (nivel 3) — estado `orden`, mismo control; el re-orden
      es **en memoria**: "reciente" conserva el orden del server (`updatedAt
      desc`) y solo evita el re-orden por urgencia.
- **Sin cambios** en `lex-control-api` (el branch `else` de `listProcesos` ya
  ordena por `updatedAt desc`).

## Fuera de alcance

- Filtro/orden por documento del cliente (cédula): el buscador ya cubre cliente
  por nombre; no se incluye aquí.
