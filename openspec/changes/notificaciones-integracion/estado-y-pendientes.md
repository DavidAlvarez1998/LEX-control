# Notificaciones (correo / SMS / llamada) — estado y pendientes

> Fecha: 2026-06-20. Estado tras **pruebas en vivo** contra el microservicio real.
> Módulo: `lex-control-api/src/modules/notificaciones/` (sin router HTTP; solo
> capacidad backend). Smoke: `scripts/smoke-notificaciones.ts` (envía DE VERDAD,
> exige `--confirmar`, es de COBRO). Docs del proveedor:
> `openspec/roadmap-docs/APIs/*.odt`.

## Microservicio (de Finova, NO es nuestro código)

- Host: `NOTIFICAR_API_URL` (default `http://10.10.10.211:5020`), contenedor
  `solucredito-hablame-1` / proyecto `API_NOTIFICAR`. Sin auth (red interna), HTTP.
- Alcanzable desde el server de la app. Timeout cliente:
  `NOTIFICAR_TIMEOUT_MS` (default **15000 ms**).

## Estado por canal (probado en vivo 2026-06-20)

| Canal | Proveedor | Endpoint | Estado |
|---|---|---|---|
| 📧 Correo | Amazon SES | `POST /email/enviar` | ✅ **Funciona y entrega** (remitente fijo `info@finova.com.co`) |
| 📞 Llamada | Go4Clients TTS | `POST /go4/llamar` + `GET /go4/estado/:id` | ✅ **Funciona** (ver caveats) |
| 💬 SMS | Háblame | `POST /notificarViaSMS` | ❌ **No entrega** (responde `"Ok"` pero el SMS no llega) |

## Caveats / hallazgos

1. **Timeout de la llamada (bug nuestro, menor):** el disparo a Go4 tarda > 15 s →
   con el default `NOTIFICAR_TIMEOUT_MS=15000` la llamada falla con "el servicio no
   respondió a tiempo". Correo y SMS responden rápido. **Fix sugerido:** subir el
   timeout (global a ~30-60 s, o específico mayor en `llamadas.client.ts`).
   Workaround usado en pruebas: `NOTIFICAR_TIMEOUT_MS=60000`.
2. **Llamada lenta en encolarse:** la campaña queda `PROGRAMMED` un rato antes de
   marcar; hay que consultar `GET /go4/estado/:id` varias veces hasta
   `termino:true` (estado `answered` / `no_answer` / `failed`). Saldo Go4 OK:
   `GET /go4/balance` → `PLAN SOLUCREDITO V2`, balance ~464.
3. **SMS no entrega (pendiente, lado Finova):** nuestra petición es correcta
   (`toNumber` con indicativo sin `+`, ej. `573162977528`; `content`, `isPriority`,
   `isFlash` — idéntico a `api_msm.odt`). El microservicio responde `{"message":"Ok"}`
   = Háblame **aceptó**, pero el SMS no llega. **No expone saldo ni estado de
   entrega** de SMS (todos los GET de tanteo dan 404). → revisar en la cuenta de
   **Háblame** del microservicio: saldo, remitente/línea aprobada, o credenciales
   de prueba. **No es bug de `lex-control-api`.**

## Requerimientos para Finova (su microservicio)

1. **SMS Háblame:** averiguar por qué acepta (`"Ok"`) pero no entrega (saldo /
   remitente / cuenta demo).
2. **Caller ID de la llamada configurable:** hoy el número de **origen** sale fijo
   `573226962139` (campo `sender`/`source` en la respuesta cruda de Go4) y la API
   `/go4/llamar` **no tiene parámetro de origen** (solo `telefono`, `mensaje`,
   `voice`, `speed`, `campaignName`, `earliestTimeToCall`, `callbackUrl`). Para
   poder elegirlo: (a) que el microservicio exponga `sender`/`from` y lo pase a
   Go4, y (b) que ese número esté **registrado/aprobado** en Go4/operador (el
   caller ID debe estar verificado o el carrier lo rechaza/reemplaza).

## Formatos de número

- **SMS:** `573XXXXXXXXX` (indicativo país, sin `+`).
- **Llamada:** acepta `3XXXXXXXXX` / `573XXXXXXXXX` / `+57...` (Go4 normaliza).

## Pendiente — ADJUNTOS en el correo (bloquea "Notificar al demandado")

> Solicitado 2026-06-23. Caso de uso: en la ficha del **proceso ejecutivo de
> mínima cuantía**, etapa "Mandamiento de pago", un botón **"Notificar"** que envíe
> a **cada demandado** (Litigante con correo) un correo con **el mandamiento de pago
> y la constancia de notificación adjuntos**.

**BLOQUEO:** el canal de correo (`enviarCorreo`) y el microservicio solo aceptan
`{ to, subject, html }` (`POST /email/enviar`) — **NO soporta adjuntos**. Por eso el
botón no se puede implementar como "correo con archivos adjuntos" hoy.

**Caminos:**
1. **Pedir adjuntos al microservicio** (decisión del usuario 2026-06-23): que Finova/
   solucredito agregue soporte de adjuntos (raw MIME / multipart) a `/email/enviar`.
   Cuando exista, `enviarCorreo` gana un parámetro `adjuntos[]` y se construye el botón.
2. Alternativa no elegida: enviar **enlaces** a los PDFs (tecnovapp) en el HTML — pero
   hay que verificar que un externo pueda abrir el link sin login (tecnovapp protege).

**Notas para cuando se implemente:**
- A quién: partes con `rol = Demandado` que tengan `email`/`correos` (Litigante).
- Qué adjuntar: `mandamiento-pago.pdf` (único) + las `Notificación: *` (multi, ya se
  suben en la ficha, ancladas a `fechaNotificacion`).
- **Legal:** un correo NO es notificación judicial formal (art. 430 CGP la surte el
  juzgado: personal/aviso). El correo debe aclararlo; es envío de gestión/cortesía.
- **De cobro:** cada correo cuesta (cuenta SES del proveedor).
