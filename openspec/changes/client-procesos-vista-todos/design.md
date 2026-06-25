# Diseño — client-procesos-vista-todos

## Estado actual (referencia)

- `lex-control-client/src/app/(dashboard)/procesos/page.tsx`
  - Toggle en líneas ~267–283: `Jurisdicción` (`/procesos`) vs `Sección` (`/procesos?vista=seccion`).
    Ambas leen `tipos` (catálogo) y arman conteos (`conteoTiposPorJur`, `conteoTiposPorGrupo`).
  - Árbol de 3 niveles; el nivel 3 ya lista procesos reales con `listProcesos`, los ordena con
    `grupoUrgencia()` + sort por `fechaLimite`, y pinta `venceUI()` + `EstadoBadge`.
- `lex-control-client/src/app/(dashboard)/mis-procesos/page.tsx`
  - Lista plana; `listProcesos({ responsableId })` + `ordenar()` por `fechaLimite`. `venceUI()`
    duplicada aquí.
- `lex-control-client/src/components/vencimientos-banner.tsx` — banner de urgentes (`getVencimientos`).
- `lex-control-api`: `GET /procesos` (`listProcesos`) con filtros `area/estado/q/responsableId/
  clienteId/page/conNovedades`; `GET /procesos/vencimientos` agrupa abiertos en
  `{ vencido, por_vencer, al_dia }`. `crearSemaforo()` (procesos.dto.ts) define vencido/por_vencer/al_día
  (hoy+3 días hábiles).

## Decisiones

### D1 — El toggle pasa a 3 vistas controladas por `?vista`
`vista ∈ { jurisdiccion (default), todos, mios }`. Se elimina `seccion`. El componente decide:
- `jurisdiccion` → render del árbol de catálogo actual (sin cambios).
- `todos` / `mios` → render de **una sola** lista plana nueva (`<ListaProcesosPlana>`), con
  `responsableId = usuario.id` solo en `mios`.

Orden del toggle: **Jurisdicción · Todos · Míos** (decisión del usuario). Default = Jurisdicción
(primera, comportamiento actual; no rompe enlaces existentes a `/procesos`).

### D2 — Vista de lista plana = la del inicio, pero completa
Una sola tabla (reusa columnas del nivel 3: Proceso · Cliente · Etapa · **Vence** · Responsable ·
Estado). Orden global:

1. **Vencidos** (semáforo `vencido`)
2. **Por vencer** (semáforo `por_vencer`)
3. **Al día con fecha** (`al_dia` + `fechaLimite`), por `fechaLimite` asc
4. **Sin fecha** (abiertos sin `fechaLimite`)
5. **Cerrados / archivados** (grises), al final

Es la generalización de `grupoUrgencia()` que ya existe en el nivel 3 (que solo distingue
0=con fecha / 1=sin fecha / 2=cerrado). Aquí se separa además vencido vs por_vencer vs al_día usando
el `semaforo` que la API ya devuelve en cada `ProcesoListItem`.

### D3 — Orden estable a través de la paginación → ordenar en la API
`listProcesos` pagina. Si ordenamos solo en cliente, el orden "vencidos primero" sería **por página**,
no global (un vencido en la página 3 quedaría después de un al-día de la página 1). Para que el orden
sea correcto se añade ordenamiento **server-side**:

- Nuevo parámetro opcional `orden=vencimiento` en `GET /procesos`.
- Cuando está presente, el repositorio ordena por: grupo de urgencia (vencido < por_vencer < con-fecha
  < sin-fecha < cerrado) y luego `fechaLimite asc`. Como el grupo "vencido/por_vencer" se deriva de
  `fechaLimite` vs (hoy / hoy+3 hábiles), en SQL se puede expresar como:
  - cerrados/archivados al final (orden por `estado`),
  - luego `fechaLimite ASC` con nulos al final (`NULLS LAST` / `ORDER BY fechaLimite IS NULL, fechaLimite ASC`).
  Eso ya deja vencidos→por_vencer→al_día→sin_fecha→cerrados en orden correcto **sin** recomputar el
  semáforo en SQL (el semáforo sigue calculándose en el DTO para el badge). El corte vencido/por_vencer
  es visual (color), el **orden** lo da `fechaLimite asc`.

Sin el parámetro, el endpoint se comporta igual que hoy (aditivo, retrocompatible).

**Alternativa descartada (B):** traer todo sin paginar y ordenar en cliente — simple pero no escala si
un despacho tiene cientos de procesos. Se prefiere paginar con orden correcto del servidor.

### D4 — `/mis-procesos` redirige
`mis-procesos/page.tsx` → `redirect("/procesos?vista=mios")` (server) o `router.replace` (client),
eliminando la duplicación de `venceUI`/`ordenar`. El deep-link sigue vivo.

### D5 — Reuso de UI, sin librerías nuevas
- Mover `venceUI()` a un helper compartido (p.ej. `src/lib/vencimiento.ts`) y consumirlo en la lista
  plana (hoy está duplicado en `procesos/page.tsx` y `mis-procesos/page.tsx`).
- Reusar `EstadoBadge` y el `VencimientosBanner` (el banner sigue arriba en todas las vistas).
- Mantener filtros existentes (área/estado/búsqueda) sobre la lista plana.

## Riesgos

- **Conteo/volumen:** la vista `Todos` lista todos los procesos del tenant. Mitiga la paginación +
  orden server-side (D3). Mostrar el total y respetar `page`.
- **Empty states:** sin procesos → `EmptyState` (ya disponible en `ui.tsx`).
- **View transition:** la lista hereda el cross-fade de `(dashboard)/template.tsx`; sin trabajo extra.
