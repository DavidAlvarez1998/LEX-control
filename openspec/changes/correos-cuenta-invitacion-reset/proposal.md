# correos-cuenta-invitacion-reset

## Por qué

Hoy, cuando se crea un usuario o se restablece su contraseña, la API **genera el token y la
`activationUrl`** pero **no envía nada**: el link queda en la respuesta para que el admin lo
copie y lo comparta a mano. Esto es frágil (links pegados por chat) y bloquea el onboarding real.

Este change conecta esos flujos con la capacidad de **correo (Amazon SES)** que ya existe
(`enviarCorreo` de [[convencion-integraciones-externas]] / `integracion-notificaciones`). Es el
"consumidor real" que aquel change dejó anotado en *Fuera de alcance* ("disparos automáticos desde
el negocio"). No se construye transporte nuevo: solo se **invoca** lo existente con una plantilla.

Tres disparadores, todos sobre el mismo endpoint público `/auth/set-password` (página `/activar?token=`):

1. **Admin de plataforma crea un usuario** (`POST /usuarios`) — sea ADMIN, COMERCIAL o USUARIO de
   empresa (incluido el administrador de empresa) → **correo de invitación** con el link.
2. **Admin de empresa crea un miembro de su equipo** (`POST /mi-empresa/usuarios`) → **correo de
   invitación**. También al **reenviar** (`POST /mi-empresa/usuarios/:id/activation`).
3. **Restablecer contraseña** (`POST /usuarios/:id/reset-password`, hoy solo lo dispara el ADMIN) →
   **correo de restablecimiento** con el link, dirigido al usuario afectado.

## Decisiones

- **Reset = solo lo dispara el admin** (decisión del usuario). NO se agrega "olvidé mi contraseña"
  self-service ni endpoint `POST /auth/forgot-password` ni página pública nueva. Se reusa el flujo
  existente; lo único que cambia es que ahora **el correo llega al usuario** en vez de mostrarse al admin.
- **El link sigue en la respuesta y en la UI como respaldo** (decisión del usuario). La respuesta
  añade `correoEnviado: boolean`; la UI muestra "Correo enviado a X" y, debajo, el link copiable por
  si el correo falla o tarda. No se rompe ningún contrato existente (solo se agrega un campo).
- **El envío NO debe romper la operación.** El correo se manda **después** de que la creación/reset
  ya está confirmada (fuera de la transacción). Si SES falla, se **registra y se sigue**:
  `correoEnviado=false` y el admin usa el link de respaldo. Nunca lanza error al caller.
- **Plantillas HTML mínimas y propias**, en español, en un solo lugar
  (`notificaciones/plantillas-cuenta.ts`). El proveedor ya envuelve el HTML en su plantilla con logo,
  así que el cuerpo es sobrio: saludo + qué es + botón/enlace + nota de expiración (48 h) + "si no
  esperabas esto, ignóralo". Se reusa el motor existente solo como strings (no Handlebars).
- **Una sola URL base por destino** ya resuelta por `activationUrl(raw, rol)` (clientUrl vs adminUrl).
  No se toca esa lógica; las plantillas reciben la URL ya construida.

## Qué se construye

**Backend (`lex-control-api`)**
- `notificaciones/plantillas-cuenta.ts` — `plantillaInvitacion({nombre, activationUrl, contexto})` y
  `plantillaReset({nombre, activationUrl})` → `{ subject, html }` (puro, testeable, sin red).
- `notificaciones/correos-cuenta.ts` — `enviarInvitacionCuenta(...)` y `enviarResetCuenta(...)`:
  arman la plantilla, llaman `enviarCorreo`, **atrapan errores** y devuelven `boolean` (enviado).
- Cableado en `usuarios.service.ts` (`createUsuario`, `resetPassword`) y `mi-empresa.service.ts`
  (`createMiembro`, `resendActivation`): enviar tras confirmar y propagar `correoEnviado` en la respuesta.

**Frontend (admin + client)**
- `usuarios/page.tsx` (admin) y `equipo/page.tsx` (client): tras crear/reset/reenviar, mostrar
  "✓ Correo enviado a {email}" cuando `correoEnviado`, y el bloque del link como respaldo
  ("¿No le llegó? Copia este enlace"). Si `correoEnviado=false`, avisar que se use el link.

## Pruebas

- **Unitarias** (gate, sin red): plantillas (link presente, sin `[[falta:]]`, subject correcto por
  contexto) + services con `enviarCorreo` mockeado (se llama con el `to`/`subject` correctos; un fallo
  de envío **no** lanza y deja `correoEnviado=false`; la creación/reset igual retorna el link).
- **Smoke real** (no gate, de cobro): reusar/extender `scripts/smoke-notificaciones.ts correo` o crear
  el usuario contra un correo real del usuario y verificar recepción + que el link activa la cuenta.

## Lo que NO se hace aquí

- Sin "olvidé mi contraseña" self-service (descartado por el usuario).
- Sin modelo Prisma de log/auditoría de correos enviados (sería change posterior; hoy basta `correoEnviado`).
- Sin reintentos/cola asíncrona de envío (best-effort en el request; el link es el respaldo).
- Sin tocar SMS/llamadas para estos flujos (solo correo).
