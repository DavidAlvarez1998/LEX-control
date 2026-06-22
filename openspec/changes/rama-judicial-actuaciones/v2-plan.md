# v2 — plan de implementación (incrementos 2-5)

Incremento 1 (cron masivo + anti-bloqueo) ya está. Este doc planea las 4 piezas
restantes pedidas por el usuario. Todas sobre lo ya construido (sync + actuaciones).

## #1 — Detección de hitos → SUGERIR avance de etapa (mayor valor)
- **Backend** `procesos/hitos-actuaciones.ts` (puro): mapa keyword→{etapaKey, campoFecha}
  (ADMITE→calificacion/fechaAdmision, MANDAMIENTO→mandamientoPago/fechaMandamiento,
  NOTIFIC→/fechaNotificacion, EXCEPCIONES→/contesto, SENTENCIA, LIQUIDACION/AVALUO/REMATE,
  TERMINA/ARCHIVO). `detectarHitos(actuaciones, etapas, datos)` → sugerencias **solo si** la
  etapa/campo existe en el tipo y el dato está vacío. Matching difuso (normaliza tildes/mayúsc,
  `includes`). NO auto-avanza (el motor exige el doc del juez); solo sugiere + propone fecha.
- **Endpoint** `GET /:id/actuaciones/sugerencias`.
- **Frontend** (ficha): card "Sugerencias de la Rama" → "Posible avance a *Mandamiento de pago*
  (09-mar) · [Usar fecha]". El botón hace `actualizarProceso(datos[campoFecha]=fecha)` (dispara el
  auto-avance del motor si se cumplen los requisitos). El abogado adjunta el doc y confirma.

## #2 — Notificar novedades (por CORREO; in-app diferido)
- Dispara cuando el **cron** encuentra actuaciones nuevas (no en el on-demand: ahí el abogado ya las
  ve en pantalla). `sincronizarProceso(proceso, { notificar })`; el cron pasa `notificar: true`.
- **Backend** `notificaciones/correos-actuaciones.ts`: `enviarNovedadActuaciones({to, nombre,
  procesoTitulo, radicado, nuevas, ultima})` → plantilla HTML; best-effort (try/catch, nunca lanza),
  reusa `enviarCorreo` (SES). Destinatario: el **responsable (abogado)** del proceso (si tiene email).
- **Smoke** real contra `adjuan123@gmail.com`.
- **Diferido:** campanita in-app global (necesita modelo Notificacion + topbar en ambos portales) →
  follow-up propio. La señal "no leídas" en la ficha la da el #3.

## #3 — "Nuevas" persistente (no leídas, sobrevive a la sesión)
- **Schema:** `Proceso.actuacionesVistasAt DateTime?`.
- **Backend:** `listarActuaciones` devuelve `nueva` por ítem (`createdAt > actuacionesVistasAt`);
  nuevo `POST /:id/actuaciones/marcar-vistas` → setea `actuacionesVistasAt = now`.
- **Frontend:** badge "nueva" persistente (del flag del API) + "✓ N nuevas desde tu última visita" +
  botón "Marcar como vistas". (Simplificación v1: por-proceso, no por-usuario.)

## #4 — Autollenar el juzgado (auto solo si está vacío)
- En `sincronizarProceso`: cuando se llama al Endpoint A (idProcesoRama no cacheado) capturamos
  `despacho`; si `Proceso.despachoJuzgado` está vacío, lo seteamos. No pisa lo que el abogado escribió.

## Cambios de datos (resumen)
- `Proceso.actuacionesVistasAt DateTime?` (#3) — `pnpm push`.

## Gate
- tsc API + client · vitest (hitos puro, correos-actuaciones mock, marcar-vistas/nueva) · build client.
- Smokes reales: novedad por correo a adjuan123@gmail.com; (cron ya tiene script).
