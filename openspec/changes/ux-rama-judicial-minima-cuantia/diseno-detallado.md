# Diseño detallado de las propuestas clave (profundización)

Lleva las propuestas de `propuestas-ux.md` a nivel **listo para implementar**: UI exacta, cambios de
datos/back, llamadas a la API, casos borde y esfuerzo. Sigue siendo **diseño** (no se implementa aquí);
cada sección sería su propio change al aprobarse.

---

## 1. Cluster "Claridad y confianza" (Fase 1 · P3+P5+P6+P8+P13) — DETALLE

La Fase 1 es casi toda **front + 1 campo de fecha**. Bajo riesgo, alto valor de comprensión.

### 1.1 Separar visualmente las dos líneas de tiempo (P3)
- **Stepper de etapas** → encabezado: "**Avance en el despacho**" + subcopy "Lo que gestionas tú en
  LEX Control". Sin cambios de lógica.
- **Panel Rama** → encabezado "**Lo que publica el juzgado** 🏛️" + acento de color frío (slate/azul)
  distinto del índigo del stepper, y borde izquierdo del timeline en ese color.
- Una línea puente (microcopy): *"Cuando el juzgado publica una actuación, aquí te sugerimos el avance
  de etapa correspondiente."*
- **Archivos:** `procesos/[id]/page.tsx` (encabezados del stepper y del `ActuacionesJuzgado`). Solo copy/estilo.

### 1.2 Indicador de frescura (P5) — requiere 1 campo
- **Dato nuevo:** `Proceso.actuacionesSyncAt DateTime?` — se setea en `sincronizarProceso` al terminar
  (junto a `idProcesoRama`). Migración aditiva (`pnpm push`).
- **API:** `listarActuaciones`/`getDetalle` exponen `actuacionesSyncAt` y la `fechaUltimaActuacion`
  (la más reciente ya está en la BD).
- **UI:** bajo el botón "Actualizar": `Sincronizado hace {relativa} · última actuación {fecha}`.
  Helper de "hace X" (min/horas/días). Si nunca se sincronizó: "Aún no consultado — usa Actualizar".

### 1.3 Estados persistentes "reservado / no publicado" (P6) — requiere 1 enum/flag
- **Dato nuevo:** `Proceso.ramaEstado` (enum: `OK` | `RESERVADO` | `NO_PUBLICADO` | `SIN_RADICADO`),
  seteado en cada sync según la respuesta (`esPrivado`→RESERVADO; `procesos:[]`→NO_PUBLICADO; ok→OK).
- **UI:** badge en el header del proceso (`🔒 Reservado en la Rama` / `⏳ Aún no publicado`) con tooltip.
  Persistente entre sesiones (no solo tras "Actualizar").

### 1.4 Origen del dato (P8) y contador (P13)
- Junto a `juzgado`/`fechaRadicacion`: chip `de la Rama` cuando el último sync los llenó (se puede
  inferir si el valor coincide con lo que devolvió la Rama, o marcar un set `camposAutollenados` en
  `datos._meta`). Mínimo viable: solo el chip "de la Rama" en juzgado/fecha cuando `actuacionesSyncAt` existe.
- Contador del radicado: subir de `text-xs` a `text-sm`; feedback del sync persiste como nota hasta el
  próximo cambio del campo.

**Esfuerzo Fase 1:** ~1 campo de fecha + 1 enum (push) + cambios de front. Sin tocar la Rama.

---

## 2. P1 — Novedades en la LISTA de procesos (apuesta de impacto)

### Objetivo
Que el abogado vea desde la lista qué procesos tienen **actuaciones nuevas** (no leídas) sin abrirlos.

### Datos / backend
"Nueva" = `ActuacionProceso.createdAt > Proceso.actuacionesVistasAt` (ya existe el sello). Para la lista
hacen falta los **conteos por proceso** sin caer en N+1. Opciones:
- **(A) Denormalizar un contador** `Proceso.actuacionesNuevas Int @default(0)`: se recalcula en cada
  sync (count nuevas vs vistasAt) y se pone a 0 en `marcarActuacionesVistas`. La lista lo lee directo
  (cero costo). **Recomendada** — simple y O(1) en la lista.
- (B) Subconsulta/`groupBy` en `listProcesos` (sin campo nuevo): correcto pero más caro y depende de
  paginación. Descartada para v1.
- **Endpoint:** `listProcesos` (DTO de fila) agrega `actuacionesNuevas: number`.

### UI (lista)
- Columna "Novedades" (o píldora junto al título): `🟢 2 nuevas` si >0; `·` si 0.
- Filtro nuevo "Con novedades" (toggle) → `where actuacionesNuevas > 0`.
- Header: contador global "N procesos con novedades del juzgado" (suma) como pill clicable que aplica el filtro.
- Ordenar por novedades opcional.

### Casos borde
- Proceso sin radicado / no judicial → sin píldora.
- Reservado/no publicado → sin novedades (no rompe).
- "Marcar como vistas" en la ficha → la píldora de la lista baja a 0 al refrescar.

### Esfuerzo
Medio: 1 campo denormalizado + recálculo en 2 puntos (sync, marcar-vistas) + columna/filtro en la lista.

---

## 3. P9 — Importar los documentos del expediente (PDF reales) — la de mayor impacto

### Capacidad (verificada)
- `GET /Proceso/Documentos/{idProceso}` → lista `{ idRegDocumento, nombre, descripcion, fechaCarga, ... }`.
- `GET /Descarga/Documento/{idRegDocumento}` → **PDF** (`application/pdf`).
- Actuaciones traen `conDocumentos` (bool) y `idRegActuacion` (para correlacionar).

### Backend
- **Cliente rama-judicial** (extender el módulo): `obtenerDocumentos(idProceso)` (Endpoint E, DTO) y
  `descargarDocumento(idRegDocumento): Promise<Buffer>` (Endpoint F; valida `content-type: application/pdf`,
  límite de tamaño, timeout). Respeta el §4 anti-bloqueo (delay entre descargas).
- **Persistencia:** reusar `DocumentoProceso` (sube el binario a tecnovapp → guarda `url`=path,
  `categoria` inferida del nombre como ya hace `categoriaDoc(...)`, `nombre`=descripción, `tipo`=application/pdf).
  - **Anti-duplicado:** nuevo campo `DocumentoProceso.origenRamaIdReg String? @unique?` (o índice
    `(procesoId, origenRamaIdReg)`) → re-importar no duplica.
- **Servicio:** `importarDocumentosRama(t, procesoId, { idRegs?: string[] })` — lista, filtra los ya
  importados, descarga+sube los seleccionados (o todos), idempotente. **No** auto-importa todo en el
  sync normal (sería costoso y muchos requests); es **on-demand** por acción del usuario.
- **Endpoints:** `GET /:id/rama/documentos` (lista lo disponible en la Rama, marca cuáles ya están
  importados) · `POST /:id/rama/documentos/importar` `{ idRegs }`.

### UI (ficha)
- En el panel "Lo que publica el juzgado", subsección o pestaña "**Documentos del expediente**":
```
 Documentos del expediente (Rama)                    [ Traer del juzgado ↻ ]
 ☐ 09-mar  Certificación bancaria parte demandante      ya en el proceso ✓
 ☑ 03-mar  Auto que ordena entrega de títulos           [ ver PDF ] [ guardar ]
 ☐ 25-feb  Constancia constitución título judicial
                                   [ Importar seleccionados (2) ]
```
- En el **timeline**, actuaciones con `conDocumentos` muestran 📎 y un atajo "ver documentos".
- Los importados aparecen también en el panel "Documentos" del proceso (un mismo `DocumentoProceso`),
  con un chip "del juzgado".

### Casos borde / riesgos
- **Rate-limit:** importar todo = N requests → batch con delays (reusar §4). Avisar progreso.
- **Documentos grandes / no-PDF:** validar content-type y tamaño; si falla uno, seguir con los demás.
- **Reservado:** sin documentos.
- **Almacenamiento:** depende de [[reestructura-almacenamiento-documentos]] (tecnovapp, ruta por módulo/año/mes).
- **Legal:** son documentos públicos del expediente; ok guardarlos en el proceso del despacho.

### Esfuerzo
Alto (cliente + storage + modelo + UI). **Mayor impacto funcional** — el abogado deja de bajar PDFs a mano del portal.

---

## 4. P12 — Validación en vivo + preview antes de vincular el radicado

### Flujo
1. El usuario teclea el radicado. El contador en vivo marca dígitos (ya existe).
2. Al llegar a 23 dígitos (debounce ~400 ms) → `GET /procesos/validar-radicado?radicado=…` (ya existe).
3. Mostrar una tarjeta de **preview** (sin guardar nada todavía):
```
 ✓ 23 dígitos
 ┌ Encontrado en la Rama ─────────────────────────────────┐
 │ JUZGADO 002 CIVIL MUNICIPAL DE PEREIRA · radicó 04-jun-26 │
 │ Demandante: FINOVA SAS · Demandado: ELDER J. GESAMA …     │
 │              [ Vincular y traer datos ]                   │
 └───────────────────────────────────────────────────────────┘
```
4. "Vincular y traer datos" → guarda el radicado + dispara el sync (lo que hoy hace al Guardar). El
   autollenado queda **explícito y confirmado** (no "mágico").

### Estados
- `encontrado` → preview con datos + botón. · `procesos:[]` → "No aparece aún en la Rama (puede tardar
  días). Puedes vincularlo igual." · `esPrivado` → "Reservado: no veremos sus actuaciones." · error/red
  → "No se pudo consultar; reintenta." · <23 díg → solo el contador, sin llamar.

### Esfuerzo
Medio (front: debounce + tarjeta de preview; el endpoint ya existe). Aplica en **ficha y en el form de crear**.

---

## 5. P10 / P11 — Autopoblar Partes (Sujetos) y card "Estado en el juzgado" (Detalle)

### Backend (extender el cliente rama-judicial)
- `obtenerDetalle(idProceso)` (Endpoint Detalle) → DTO `{ tipoProceso, claseProceso, ubicacion,
  ponente, contenidoRadicacion, ultimaActualizacion }`.
- `obtenerSujetos(idProceso)` (Endpoint Sujetos) → `[{ tipoSujeto, nombreRazonSocial, identificacion }]`.
- Endpoints `GET /:id/rama/detalle` y `GET /:id/rama/sujetos` (on-demand; o cachear en el sync).

### P11 — Card "Estado en el juzgado" (Detalle)
Bloque compacto en la ficha (junto al panel Rama):
```
 🏛️ Estado en el juzgado                 (sincronizado hace 2 h)
 Ubicación: Secretaría   ·   Tipo: Ejecutivo · Mínima cuantía
 Ponente: Juzgado 2 Civil Municipal   ·   Últ. actualización Rama: 17-jun
```
"Ubicación" es muy útil (dónde está físicamente el expediente). Esfuerzo medio.

### P10 — Importar Partes desde Sujetos
Al validar/vincular el radicado, ofrecer "Importar partes del juzgado":
```
 La Rama reporta estas partes:
   Demandante  FINOVA SAS                 → ya está (nuestro cliente) ✓
   Demandado   ELDER JOVANNY GESAMA …     [ crear como Ejecutado ]
                          [ Importar las que faltan ]
```
Crea/cotejas `ParteProceso`/`Litigante`. **No pisa** lo existente: sugiere. Esfuerzo medio (mapear
`tipoSujeto`→`RolParte`, dedup por nombre/identificación).

---

## Resumen de cambios de DATOS que implicarían (si se aprueban)

| Propuesta | Cambio de datos |
|---|---|
| P5 frescura | `Proceso.actuacionesSyncAt DateTime?` |
| P6 estados | `Proceso.ramaEstado` (enum OK/RESERVADO/NO_PUBLICADO/SIN_RADICADO) |
| P1 novedades en lista | `Proceso.actuacionesNuevas Int @default(0)` (denormalizado) |
| P9 documentos | `DocumentoProceso.origenRamaIdReg String?` (idempotencia) |
| P10/P11 | ninguno obligatorio (on-demand; opcional cachear Detalle/Sujetos en `datos._meta`) |

Todos aditivos (nullable / default) → `pnpm push` sin pérdida. El resto es cliente nuevo (mismos
patrones del módulo `rama-judicial`) + UI.
