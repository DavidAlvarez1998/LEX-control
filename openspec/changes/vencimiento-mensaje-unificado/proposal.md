# Mensaje de vencimiento unificado (qué vence + cuándo) en todas las vistas

## Contexto / problema

Hoy el vencimiento de un proceso se muestra de forma **inconsistente**:

- En la **ficha** se ve completo y claro:
  `⏱ Plazo para subsanar: 24 de junio de 2026 (5 días hábiles).`
  (lo arma `VencimientoHint` con una **etiqueta** pasada a mano por etapa + fecha
  formateada + `(N días hábiles)` vía `calcularVencimiento`).
- En el **inicio**, la **lista de procesos** y el **banner** solo se ve la fecha cruda
  y el estado: `2026-06-24 (vencido)` — **no dice qué vence ni en qué etapa**.

El usuario no puede saber, de un vistazo, **qué exactamente** está por vencer/vencido.

## Objetivo

Mostrar el **mismo mensaje rico de la ficha en todas las vistas** (inicio, lista de
procesos, "Míos"/"Todos", banner de vencimientos): *qué* vence (etiqueta del plazo de la
etapa actual) + *cuándo* (fecha larga es-CO) + *plazo* (`(N días hábiles/calendario)`) +
estado (vencido / vence hoy / por vencer).

Ej.: `⏱ Plazo para subsanar: 24 de junio de 2026 (5 días hábiles) — vencido`

## Diseño (un solo origen de verdad)

La **fecha límite** ya se calcula y persiste en el backend (`Proceso.fechaLimite`,
derivada de `plazoDesdeCampo` en cada transición de etapa). Lo que falta es viajar,
junto a cada item de lista/vencimiento, **el "qué" y el "cuánto"**, hoy solo disponibles
en la ficha. Por eso el dato se calcula **en el backend** (desde la etapa actual) y se
expone en los DTO, y el **cliente lo pinta con un helper compartido** — sin duplicar la
lógica de etiqueta/días por vista.

### 1. Catálogo — etiqueta de plazo data-driven
`ReglasEtapa` gana `plazoEtiqueta?: string` (p. ej. `"Plazo para subsanar"`). Es el
nombre humano de **qué** corre en esa etapa. Opcional; si falta, se usa `etapaNombre`
como fallback (ya disponible). Se siembra incrementalmente en `seed-tipos.json`
(empezando por el ejecutivo de mínima cuantía).

### 2. Backend — descriptor del plazo en los DTO
Helper `descriptorPlazo(etapas, etapaActual)` → `{ etapaNombre, plazoEtiqueta, plazoDias,
plazoTipoDias }`, leído de las reglas de la **etapa actual** (que ya viajan en
`tipoProceso.etapas`). Se incluye en:
- `toProcesoListItem` (endpoint `GET /procesos`).
- los items de `GET /procesos/vencimientos` (requiere agregar `tipoProceso.etapas` al
  `select` de `listVencimientos`).
`plazoDias` se toma del `plazoDias` estático de la etapa; en etapas cuyo término depende
de un valor (`plazoDiasPorValorDe`) queda `null` y el mensaje omite el `(N días)` — la
fecha y la etiqueta igual se muestran (la fecha persistida ya es correcta).

### 3. Cliente — helper de presentación único
En `lib/vencimiento.ts` (donde ya vive `venceUI`) se agrega `vencimientoTexto(item)` que
arma el string completo (etiqueta ?? etapaNombre · fecha larga · `(N días …)` · estado)
y reusa el color/semaforo de `venceUI`. Se aplica en: `inicio`, lista `/procesos` (filas),
y `VencimientosBanner`. La **ficha** mantiene `VencimientoHint` (preview en vivo del
formulario) pero puede migrar su etiqueta al `plazoEtiqueta` data-driven (misma fuente).

## Fuera de alcance / incremental
- Sembrar `plazoEtiqueta` en TODOS los tipos: se hace gradualmente; sin él, cae a
  `etapaNombre` (ya legible).
- `(N días)` exacto en etapas `plazoDiasPorValorDe`: requiere los `datos` del proceso en
  la lista; por ahora se omite el detalle de días en esos casos (la fecha es correcta).

## Verificación
- `tsc` verde (api + client); `vitest` verde.
- En inicio/lista/banner se ve `⏱ <qué>: <fecha larga> (<N días …>) — <estado>`.
- Sin `plazoEtiqueta` sembrado, cae a `etapaNombre` (sigue diciendo "qué").

## Estado: IMPLEMENTADO (2026-06-25, sin commit)
- API: `esquema.ts` +`plazoEtiqueta`; `procesos.dto.ts` +`descriptorPlazo`/`toVencimientoItem`
  (defensivo si falta `tipoProceso`); `listVencimientos` select +`tipoProceso.etapas`;
  `vencimientos()` mapea por `toVencimientoItem`.
- Client: `ProcesoListItem`/`VencimientoItem` +`plazoEtiqueta/plazoDias/plazoTipoDias`
  (+`etapaNombre` en VencimientoItem); `lib/vencimiento.ts` +`vencimientoTexto`; aplicado
  en `inicio`, `VencimientosBanner` y la columna "Vence" de `/procesos`.
- Seed: `plazoEtiqueta` en el ejecutivo (`subsanacion` = "Plazo para subsanar";
  `mandamientoPago` = "Plazo del demandado para pagar o excepcionar"). Re-seed aplicado.
- Gate: api `tsc` + `vitest` 506/506 verde; client `tsc` verde.
- Pendiente incremental: sembrar `plazoEtiqueta` en los demás tipos (verbal/sumario/
  laboral/DdP) — hoy caen a `etapaNombre`.
