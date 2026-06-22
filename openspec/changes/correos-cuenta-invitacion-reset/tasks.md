# Tasks — correos-cuenta-invitacion-reset

## Backend — plantillas + envoltorio (sin red)
- [x] `notificaciones/plantillas-cuenta.ts` — `plantillaInvitacion({nombre, activationUrl, contexto})`
      y `plantillaReset({nombre, activationUrl})` → `{ subject, html }` (puro, ES, botón + link + 48h)
- [x] `notificaciones/correos-cuenta.ts` — `enviarInvitacionCuenta(...)` / `enviarResetCuenta(...)`:
      arman plantilla, llaman `enviarCorreo`, **try/catch** (log + `return false`), nunca lanzan
- [x] Exportar lo necesario en `notificaciones/index.ts` (barrel)

## Backend — cableado en services (enviar FUERA de la tx)
- [x] `usuarios.service.ts` `createUsuario` → tras commit, `enviarInvitacionCuenta` (contexto según rol:
      ADMIN→admin, COMERCIAL→comercial, USUARIO→empresa) → respuesta `+ correoEnviado`
- [x] `usuarios.service.ts` `resetPassword` → `updateForReset` ahora trae `email`+`nombre`;
      `enviarResetCuenta` → respuesta `+ correoEnviado`
- [x] `mi-empresa.service.ts` `createMiembro` → `enviarInvitacionCuenta` (contexto "empresa")
      → respuesta `+ correoEnviado`
- [x] `mi-empresa.service.ts` `resendActivation` → nuevo `repo.findMiembroContacto` (email/nombre scoped);
      `enviarInvitacionCuenta` (contexto "empresa") → respuesta `+ correoEnviado`

## Frontend (admin + client)
- [x] `lex-control-admin` `usuarios/page.tsx` — "Correo enviado a {email}" / aviso ámbar si falló,
      conservando el bloque de link copiable como respaldo (crear, reset)
- [x] `lex-control-client` `equipo/page.tsx` — idem para crear miembro y reenviar

## Pruebas (gate, sin costo)
- [x] `tests/correos-cuenta.test.ts` — plantillas (link presente, sin `[[falta:`, subject por contexto)
      + envoltorio (`enviarCorreo` mockeado: `to` correcto; un fallo no lanza y retorna `false`)
- [x] `usuarios.test.ts` y `mi-empresa-usuarios.test.ts` — mock de `correo.client` para no tocar la red

## Smoke real (NO gate — de cobro, lo corre el usuario)
- [ ] **Pendiente del usuario:** crear un usuario contra un correo real y verificar: llega el correo,
      el botón abre `/activar?token=` y permite definir contraseña; repetir para reset y mi-empresa

## Gate
- [x] `tsc --noEmit` verde (api + admin + client)
- [x] `vitest` verde (465 tests, +6 nuevos)
- [x] build de ambos frontends verde

## Fuera de alcance (posibles changes futuros)
- [ ] "Olvidé mi contraseña" self-service (`POST /auth/forgot-password` + página pública)
- [ ] Modelo Prisma de log/auditoría de correos (idempotencia, reintentos)
- [ ] Cola asíncrona / reintentos de envío
