# client-procesos-vista-todos

## Por qué

En el portal cliente, `/procesos` hoy tiene un toggle de dos vistas que son **lo mismo**: ambas
navegan el **catálogo** (árbol de tipos de proceso) y solo cambian el criterio de agrupación —
`Jurisdicción` (default) y `Sección` (por `grupo`: PETICION/CONSTITUCIONAL/LABORAL/JUDICIAL). Para
*encontrar y abrir un proceso real* el abogado tiene que bajar 2–3 niveles del árbol. La vista por
`Sección` aporta poco: es otra forma de listar el catálogo, no los procesos.

Aparte existe `/mis-procesos` — una **lista plana** de procesos (los del usuario), ordenada por
vencimiento, que **sí** es accionable, pero vive como ruta suelta sin entrada en el sidebar ni
relación visible con `/procesos`.

El **inicio** (`/inicio`) ya muestra lo más útil: los procesos **vencidos primero**, seguidos de los
**próximos a vencer** (vía `GET /procesos/vencimientos`). Eso es exactamente lo que falta en la
landing de procesos.

## Qué cambia

Reemplazar el toggle de catálogo por **tres vistas hermanas** en `/procesos`:

```
[ Jurisdicción ]  [ Todos ]  [ Míos ]
```

- **Jurisdicción** (default, sin cambios): el árbol de catálogo actual agrupado por jurisdicción.
- **Todos** (reemplaza a `Sección`): **lista plana de todos los procesos**, ordenada vencidos →
  por vencer → al día → sin fecha → cerrados/archivados (grises) al final. Es la vista del inicio,
  pero completa y navegable.
- **Míos** (integra `/mis-procesos`): la misma lista plana, filtrada al `responsable` actual.

`/mis-procesos` pasa a **redirigir** a `/procesos?vista=mios` (una sola implementación).

Se **elimina** la vista `Sección` (`?vista=seccion`) — su agrupación por `grupo` no se reusa en
ninguna otra parte.

## Alcance

- `lex-control-client`: `procesos/page.tsx` (toggle + nueva vista de lista), `mis-procesos/page.tsx`
  (redirect), reuso de `venceUI`/`EstadoBadge`/`listProcesos`.
- `lex-control-api`: ordenamiento por vencimiento en el listado de procesos (para que la paginación
  conserve el orden vencidos-primero). Cambio aditivo, sin tocar el esquema.
- **No** toca el modelo de datos, RBAC, ni el catálogo. El árbol por jurisdicción queda intacto.

## Qué NO hace

No agrega filtros nuevos (área/estado/búsqueda ya existen y se mantienen). No cambia la ficha del
proceso ni la creación. No añade `Míos` al sidebar (sigue accesible desde el toggle y desde el
deep-link `/mis-procesos`).

## Rollback

Cambio puramente de presentación + un parámetro de orden aditivo en la API. Revertir = restaurar el
toggle de dos vistas y `mis-procesos/page.tsx`; el endpoint sigue funcionando sin el parámetro
`orden` (default = comportamiento actual).
