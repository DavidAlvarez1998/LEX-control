# P1 a fondo — Novedades del juzgado en la LISTA de procesos

Profundización lista-para-implementar del gap #1: hoy las actuaciones nuevas **solo** se ven entrando
a cada ficha. Objetivo: que la **lista** (`/procesos`) muestre qué procesos tienen novedades sin abrirlos.
Sigue siendo **diseño** (no se implementa aquí).

## 1. Qué es "novedad" (ya existe la base)
Una actuación es "nueva/no leída" si `ActuacionProceso.createdAt > Proceso.actuacionesVistasAt`
(el sello `actuacionesVistasAt` y el flag por-ítem ya existen — ver [[rama-judicial-actuaciones]] #3).
El problema es **contarlas por proceso en la lista** sin N+1.

## 2. Estrategia de datos — contador denormalizado (recomendada)
- **Campo nuevo:** `Proceso.actuacionesNuevas Int @default(0)` (`pnpm push`, aditivo).
- **Se recalcula en 2 lugares (los únicos que cambian el estado de "nuevas"):**
  1. **`sincronizarProceso`** (on-demand y cron): tras insertar, `actuacionesNuevas =
     count(ActuacionProceso where procesoId, createdAt > actuacionesVistasAt)`. Ya tenemos todo ahí.
  2. **`marcarActuacionesVistas`**: pone `actuacionesVistasAt = now` **y** `actuacionesNuevas = 0`
     (en la misma operación).
- **La lista lo lee directo** → O(1) por fila, cero joins ni subconsultas. Es la opción simple y barata.

### Alternativa (descartada para v1)
Subconsulta/`groupBy` en `listProcesos` sin campo nuevo: correcto pero más caro y se complica con
paginación/ordenamiento. Se descarta; el contador denormalizado es trivial de mantener (2 puntos).

### Coherencia
- El contador puede "desfasarse" solo si alguien escribe actuaciones por fuera de `sincronizarProceso`
  (no ocurre). Aun así, cada sync lo recalcula desde la verdad (count real) → **se auto-corrige**.

## 3. Backend
- **Modelo:** `Proceso.actuacionesNuevas Int @default(0)`.
- **`sincronizarProceso`:** al final, además de `idProcesoRama`/datos, setear `actuacionesNuevas` con el
  count real vs `actuacionesVistasAt`. (Ya carga las actuaciones existentes; el count es directo.)
- **`marcarActuacionesVistas`:** `data: { actuacionesVistasAt: new Date(), actuacionesNuevas: 0 }`.
- **Lista:** `ProcesosRepository.countAndList` incluye `actuacionesNuevas` en el `select`; el DTO
  `toProcesoListItem` lo expone. (Endpoint `GET /procesos` sin params nuevos.)
- **Filtro "con novedades":** query param `?conNovedades=1` → `where.actuacionesNuevas = { gt: 0 }`.
- **Contador global:** `GET /procesos/vencimientos`-style, o derivarlo en la respuesta de lista
  (`totalConNovedades`), o un `count(where actuacionesNuevas>0)` barato.

## 4. Cliente / tipos
- `ProcesoListItem` (`procesos-api.ts`) += `actuacionesNuevas: number`.
- `listProcesos(filtros)` += `conNovedades?: boolean` → agrega `?conNovedades=1`.

## 5. UI (lista `/procesos`)
- **Columna / píldora** junto al título o como columna propia:
```
 Proceso                                 Cliente   Etapa         Vence      Juzgado
 Ejecutivo mín. — Finova vs Gesama        Finova    Mandamiento   12-jul 🟡  🟢 2 nuevas
   Rad. 66001400300220260070400                                              ───────────
 Ejecutivo mín. — A vs B                  …         Audiencia     —          ·
```
- **Filtro** "Con novedades" (toggle junto a Míos/Todos): aplica `conNovedades`.
- **Contador global** en el header como pill clicable: "🟢 3 con novedades del juzgado" → activa el filtro.
- La píldora navega a la ficha (como toda la fila) y al abrir + "Marcar como vistas" baja a 0.

## 6. Casos borde
- Proceso **no judicial / sin radicado** → `actuacionesNuevas = 0`, sin píldora.
- **Reservado / no publicado** → 0 (no rompe).
- Proceso recién creado, nunca sincronizado → 0.
- Tras "Marcar como vistas" en la ficha → al volver a la lista (o refrescar) la píldora está en 0.
- **Paginación/orden:** el filtro y un orden opcional "por novedades" funcionan con el campo indexable
  (opcional `@@index([empresaId, actuacionesNuevas])` si se quiere ordenar/filtrar mucho).

## 7. Esfuerzo
- **Backend:** 1 campo + recálculo en 2 funciones + 1 param de filtro + exponer en DTO. **Bajo-medio.**
- **Frontend:** columna/píldora + toggle + pill global. **Bajo.**
- Sin tocar la Rama (usa lo ya sincronizado). Se puede entregar junto con la Fase 1.

## 8. Relación con otras propuestas
- Alimenta el **cockpit "Para hoy"** (P2) y la **campanita in-app** (P17): ambas reusan
  `actuacionesNuevas`/`conNovedades`.
- Complementa la **frescura** (P5): la lista dice "cuántas nuevas", la ficha "de cuándo".

## 9. Preguntas abiertas
1. ¿Píldora **por fila** + filtro, o también una **vista dedicada** "Novedades" (≈ P2)? (Recomendado:
   empezar por píldora+filtro; la vista dedicada es P2.)
2. ¿Ordenar la lista por novedades por defecto cuando el filtro está activo? (Recomendado: sí.)
3. ¿El contador global suma solo "Míos" o todos los visibles? (Recomendado: respeta el toggle Míos/Todos.)
