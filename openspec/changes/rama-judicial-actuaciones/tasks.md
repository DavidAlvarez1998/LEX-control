# Tasks — rama-judicial-actuaciones

## v1 — núcleo + asistencia ligera (IMPLEMENTADO)

### Backend (lex-control-api)
- [x] `env.ramaJudicial` (RAMA_JUDICIAL_URL puerto 448, timeout, delayPaginas, User-Agent)
- [x] Módulo `rama-judicial/`: `rama-judicial.http.ts` (fetch único + User-Agent + 502),
      `rama-judicial.client.ts` (`consultarRadicado` A, `obtenerActuaciones` B paginado),
      `rama-judicial.types.ts`, `index.ts`
- [x] Schema: modelo `ActuacionProceso` (@@map actuaciones_tramite, @@unique procesoId+huella) +
      `Proceso.idProcesoRama` + relación; `pnpm generate` + `pnpm push` (BD in sync)
- [x] `procesos/actuaciones.service.ts`: `validarRadicado`, `sincronizarActuaciones` (idempotente
      por huella, cachea idProcesoRama, autollena `datos.ultimaActuacion`), `listarActuaciones`
- [x] Endpoints en `procesos.router.ts`: GET `/validar-radicado`, GET `/:id/actuaciones`,
      POST `/:id/actuaciones/sincronizar`

### Frontend (lex-control-client)
- [x] `procesos-api.ts`: `validarRadicado`, `listActuaciones`, `sincronizarActuaciones` + tipos
- [x] Ficha `procesos/[id]`: panel **Actuaciones del juzgado** (timeline + botón "Actualizar" +
      badge "nueva" + estados reservado/no-publicado) — solo procesos judiciales con radicado
- [x] `RadicadoDato`: validación contra la Rama al guardar (feedback ✓ encontrado / aún no aparece)

### Pruebas
- [x] `tests/rama-judicial.test.ts` (fetch mockeado: URL/User-Agent, procesos:[], 403→502, paginación)
- [x] `tests/actuaciones.service.test.ts` (normalizar, validar, sync idempotente, cache, autollenar)
- [x] `scripts/smoke-rama-judicial.ts` — smoke real (lectura, gratis); verificado: 64 actuaciones

### Gate
- [x] `tsc` API + client verde
- [x] `vitest` 476 (+11) verde
- [x] build client verde
- [x] `pnpm push` (BD in sync; tabla actuaciones_tramite creada)

## v2 — asistencia avanzada (IMPLEMENTADA · plan en v2-plan.md)
- [x] **#1 Detección de hitos → SUGERIR avance de etapa (incremento 2)**
      - `procesos/hitos-actuaciones.ts` (puro): keyword→{etapaKey,campoFecha} con matching difuso
        (normaliza tildes/mayúsc); solo sugiere si la etapa/campo existen y el campo está vacío. NO auto-avanza.
      - `sugerenciasDeProceso` + endpoint GET `/:id/actuaciones/sugerencias`.
      - Ficha: card "Sugerencias de la Rama" con botón "Usar fecha" (pre-llena → dispara auto-avance del motor).
      - Test `hitos-actuaciones` (5 casos).
- [x] **#2 Notificar novedades por CORREO (incremento 2)**
      - `notificaciones/correos-actuaciones.ts` `enviarNovedadActuaciones` (best-effort). Dispara desde el
        CRON (`sincronizarProceso(_, {notificar:true})`) cuando hay nuevas, al **responsable** del proceso.
      - Smoke real enviado a adjuan123@gmail.com (enviado=true). Test con enviarCorreo mockeado.
      - **DIFERIDO:** campanita in-app global (modelo Notificacion + topbar) → follow-up; la señal "no leídas"
        en la ficha la da el #3.
- [x] **#3 "Nuevas" persistente (incremento 2)**
      - Schema `Proceso.actuacionesVistasAt` (push hecho). `listarActuaciones` devuelve `nueva` por ítem
        (createdAt > vistasAt); POST `/:id/actuaciones/marcar-vistas`. Ficha: badges persistentes + contador
        + botón "Marcar como vistas". (Simplificación: por-proceso, no por-usuario.)
- [x] **#4 Autollenar juzgado + fecha de radicación si están vacíos (incremento 2 + 3)**
      - `sincronizarProceso`: del Endpoint A toma `despacho` y `fechaProceso`; setea `despachoJuzgado`
        (columna) + `datos.juzgado` + `datos.fechaRadicacion` + `datos.ultimaActuacion` SOLO si el campo
        existe en el esquema del tipo y está vacío (guarda por esquema → sin claves desconocidas, no pisa).
      - DTO `ProcesoRama +fechaProceso`. UX: al guardar un radicado de 23 díg en la ficha, se consulta la
        Rama y se autocompletan juzgado + fecha + actuaciones (RadicadoDato auto-sincroniza al guardar).
      - Contador de dígitos en vivo en el input del radicado (✓ 23 / faltan N / sobran N).
- [x] **Sincronización masiva + anti-bloqueo (cron) — IMPLEMENTADO (incremento 1)**
      - Retry + backoff exponencial en `rama-judicial.http.ts` (403/429/5xx/red; env retryAttempts/initial/max;
        intentos=1 en test).
      - `actuaciones.service.ts`: core `sincronizarProceso(proceso)` (sin tenant, compartido con on-demand)
        + `sincronizarTodas()` con lotes (batchSize 8), esperas (delayRequest 1.2s / delayLote 5s) y pausa
        (45s) tras N errores seguidos; un fallo por proceso NO detiene el barrido. Env: RAMA_JUDICIAL_BATCH_SIZE,
        _DELAY_REQUEST_MS, _DELAY_LOTE_MS, _MAX_CONSECUTIVE_ERRORS, _PAUSE_ON_ERRORS_MS.
      - `scripts/sync-actuaciones.ts` — lo ejecuta el **cron del SO** (la API no tiene scheduler propio;
        evita doble corrida con múltiples instancias).
      - Test `sincronizarTodas` (tolera fallos, totaliza). Gate: tsc + vitest 477.
      - **PENDIENTE DEL USUARIO (ops):** crontab 2×/día →
        `0 0,12 * * * cd /ruta/lex-control-api && pnpm exec tsx scripts/sync-actuaciones.ts`
        (00:00 y 12:00 Bogotá; mediodía recoge lo publicado en horario laboral). Si el mediodía da mucho 429,
        se baja a 1×/día sin tocar código.
- [ ] (follow-up) Campanita in-app global (modelo Notificacion + topbar en ambos portales)
- [ ] (follow-up) "Nuevas" por-usuario (hoy es por-proceso)
- [ ] (follow-up · documentado en specs/rama-judicial/spec.md) Aprovechar la superficie EXTRA de la
      CPNU (explorada en vivo, no consumida): Detalle (tipo/clase/ubicación), Sujetos (autopoblar
      Partes), Documentos + Descarga (importar los PDFs del expediente al proceso). Cada uno respeta
      el §4 anti-bloqueo; la descarga es por `idRegDocumento`.

## Correcciones legales detectadas (ver validacion-ley-y-realidad.md) — decisión del usuario
- [ ] A6: separar plazo del mandamiento (pagar 5 días art.431 vs excepciones 10 días art.442)
- [ ] A1: cita de cuantía art.25 (no 18)
- [ ] (menor) A10: rango remate hasta art.461
