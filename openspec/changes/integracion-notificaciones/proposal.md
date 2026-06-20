# integracion-notificaciones

## Por qué

Incorporar al backend la capacidad de **notificar** por tres canales del microservicio interno
**API_NOTIFICAR** (contenedor `solucredito-hablame-1`): **correo** (Amazon SES), **SMS** (Háblame) y
**llamadas TTS** (Go4Clients). Docs fuente: `openspec/roadmap-docs/APIs/api_correo.odt`,
`api_msm.odt`, `api_llamadas.odt`. Sigue y cumple la convención [[convencion-integraciones-externas]].

> Alcance de ESTE change: **solo la capacidad backend (la conexión)**. NO se expone router público,
> NO se consume desde los frontends, NO se envía nada real. Las pruebas reales (de cobro) se hacen
> luego, a propósito, con un número/correo del usuario, vía el script de smoke.

## Decisiones

- **Un solo módulo** `src/modules/notificaciones/` para los tres canales: comparten host
  (`http://10.10.10.211:5020`), proveedor y la característica de NO requerir auth (red interna).
- **Tipo "utilidad transversal"** (como [[documental-storage]]): son acciones de *enviar*, no datos
  que el front consulte → se exponen como funciones del módulo (client), sin router propio. Cuando
  haya un consumidor real (p. ej. "al crear un proceso, avisar por SMS") se llamará desde su service.
- **Configuración** en `env.notificaciones` (`NOTIFICAR_API_URL`, `NOTIFICAR_TIMEOUT_MS`). El host por
  defecto es el interno del doc; en cada entorno se ajusta al alcanzable desde la API.

## Qué se construye

- `notificaciones.http.ts` — transporte (ÚNICO `fetch`): timeout + `HttpError(502)`.
- `correo.client.ts` → `enviarCorreo({to,subject,html})` → `{ enviado, messageId }`.
- `sms.client.ts` → `enviarSms({toNumber,content,isPriority?,isFlash?})` → `{ enviado, mensajeProveedor }`.
  (OJO: el proveedor responde 200 incluso al fallar con `message:"Falló"` → `enviado` solo es true si `"Ok"`.)
- `llamadas.client.ts` → `llamar(...)` (devuelve `campaignId`) + `consultarEstadoLlamada(id)`
  (consultar hasta `termino===true`) + `consultarBalanceGo4()`.
- `notificaciones.types.ts` — DTOs normalizados. `index.ts` — barrel.

## Pruebas

- **Unitarias mockeando `fetch`** (`tests/notificaciones.test.ts`): URL/método/payload, normalización
  y traducción de fallos a 502. SIN red real, SIN costo → entran al gate.
- **Smoke real** (`scripts/smoke-notificaciones.ts`): envía de verdad; exige `--confirmar`; **NO** se
  corre en el gate ni en CI. Pendiente de ejecutar por el usuario con su destino.

## Lo que NO se hace aquí

Sin router, sin cambios en frontends, sin modelos Prisma (no se persiste historial de envíos todavía).
Persistir un log de notificaciones (idempotencia/auditoría) sería un change posterior.
