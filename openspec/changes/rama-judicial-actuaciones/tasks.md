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

## v2 — asistencia avanzada (PENDIENTE)
- [ ] Detección de hitos por keywords (§3a del flujo) → sugerir avance de etapa + pre-rellenar fechas
- [ ] CRON **2×/día configurable** que recorre todos los procesos con radicado (batching anti-bloqueo §4 del spec)
      - Default `ACTUALIZAR_PROCESOS_CRON=0 0,12 * * *` (00:00 y 12:00 hora Bogotá). Decisión del usuario:
        dos corridas — la del mediodía recoge lo que el juzgado publica en horario laboral, así se ve
        el mismo día sin esperar a la madrugada. Configurable por env: si el run de mediodía da mucho
        429, se baja a 1×/día sin tocar código.
- [ ] Notificar novedades (in-app/correo, reusa [[correos-cuenta-invitacion-reset]])
- [ ] Marcar "nuevas" de forma persistente (last-seen por proceso/usuario), no solo por sesión
- [ ] Sugerir `juzgado`/`despachoJuzgado` desde la consulta al validar

## Correcciones legales detectadas (ver validacion-ley-y-realidad.md) — decisión del usuario
- [ ] A6: separar plazo del mandamiento (pagar 5 días art.431 vs excepciones 10 días art.442)
- [ ] A1: cita de cuantía art.25 (no 18)
- [ ] (menor) A10: rango remate hasta art.461
