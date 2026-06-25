# Tasks — client-procesos-vista-todos

## 1. API: orden por vencimiento (aditivo)
- [x] 1.1 `GET /procesos` acepta `orden=vencimiento` (opcional) — `procesos.service.ts` ramifica.
- [x] 1.2 Repositorio: `countAndListByVencimiento` ordena cerrados/archivados al final, luego
      `fechaLimite` asc con nulos al final. Reusa el MISMO `where` (sin duplicar) ordenando claves
      mínimas en memoria + trae la página por ids → orden estable a través de la paginación. Sin el
      parámetro → `countAndList` (orden actual) intacto.
- [x] 1.3 `pnpm --dir lex-control-api build` verde + 505 tests (+1 nuevo orden=vencimiento) verdes.

## 2. Client: helper de vencimiento compartido
- [x] 2.1 `lex-control-client/src/lib/vencimiento.ts` con `venceUI(item)`.
- [x] 2.2 Reemplazadas las copias duplicadas (`procesos/page.tsx`; `mis-procesos` ahora redirige).

## 3. Client: toggle de 3 vistas en `/procesos`
- [x] 3.1 Toggle `Jurisdicción · Todos · Míos` (`ToggleVistas`); eliminado `Sección`
      (`?vista=seccion`, `conteoTiposPorGrupo`, GRUPOS/GRUPO_LABEL) y el botón "Mis procesos".
- [x] 3.2 `vista=jurisdiccion` (default) → árbol de catálogo (`CatalogoProcesos`, sin cambios de UX).
- [x] 3.3 `ListaProcesosPlana`: `listProcesos({ orden:"vencimiento", ... , page })`; tabla compartida
      `TablaProcesos` (Proceso·Cliente·Etapa·Vence·Responsable·Estado); `venceUI`+`EstadoBadge`;
      paginación Anterior/Siguiente.
- [x] 3.4 `vista=todos` → `ListaProcesosPlana` sin `responsableId`.
- [x] 3.5 `vista=mios` → `ListaProcesosPlana` con `responsableId = usuario.id`.
- [x] 3.6 `VencimientosBanner` arriba + filtros (búsqueda/área/estado/con novedades/actualizar Rama);
      `EmptyState` sin resultados.

## 4. Client: redirigir `/mis-procesos`
- [x] 4.1 `mis-procesos/page.tsx` → `redirect("/procesos?vista=mios")`.

## 5. Verificación
- [x] 5.1 `pnpm --dir lex-control-client build` verde (lint: solo deuda preexistente setState-en-effect).
- [ ] 5.2 Smoke manual: `Todos` vencidos primero; `Míos` filtra al usuario; `Jurisdicción` igual;
      `/mis-procesos` redirige; clic abre la ficha; paginación conserva el orden. (PENDIENTE en runtime)

## 6. Cierre
- [ ] 6.1 Commit (client + api + superrepo). (PENDIENTE — sin commit hasta que lo pidas)
- [ ] 6.2 Archivar el change (fusionar deltas a `specs/client-portal` y `specs/proceso-vencimientos`).
