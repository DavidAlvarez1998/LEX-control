# Tasks — integracion-notificaciones

## Backend (capacidad)
- [x] `env.notificaciones` en `config/env.ts` (NOTIFICAR_API_URL, NOTIFICAR_TIMEOUT_MS)
- [x] `notificaciones.http.ts` — transporte único (fetch + timeout + HttpError 502)
- [x] `correo.client.ts` — `enviarCorreo`
- [x] `sms.client.ts` — `enviarSms` (maneja `message:"Falló"` como no-enviado sin lanzar)
- [x] `llamadas.client.ts` — `llamar` + `consultarEstadoLlamada` + `consultarBalanceGo4`
- [x] `notificaciones.types.ts` (DTOs) + `index.ts` (barrel)

## Pruebas
- [x] `tests/notificaciones.test.ts` — unitarias con `fetch` mockeado (sin costo)
- [x] `scripts/smoke-notificaciones.ts` — smoke real, exige `--confirmar` (CREADO, NO ejecutado)
- [ ] **Pendiente del usuario:** correr el smoke con su correo/número para validar en vivo cada canal

## Gate
- [x] `tsc --noEmit` verde
- [x] `vitest` verde (notificaciones mockeado)

## Fuera de alcance (posibles changes futuros)
- [ ] Router HTTP + consumo desde frontends
- [ ] Modelo Prisma de log de notificaciones (idempotencia/auditoría)
- [ ] Disparos automáticos desde el negocio (p. ej. avisos de vencimiento)
