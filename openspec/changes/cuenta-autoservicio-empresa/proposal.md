# cuenta-autoservicio-empresa

## Por qué

Hoy la sección **"Crea tu cuenta"** de la landing del portal cliente NO crea nada usable: envía los
datos a `POST /publico/solicitud-cuenta`, que solo crea un **Prospecto WEB sin asignar** (estado
`NUEVO`) para que un comercial lo contacte y, eventualmente, lo "gane" y aprovisione la empresa a
mano. Es un embudo de ventas, no un alta.

El usuario quiere lo contrario: que al enviar el formulario **se cree de una la Empresa y el Usuario
administrador**, y que **llegue un correo con el link de activación** para que el abogado entre,
ponga su contraseña y empiece a trabajar su despacho inmediatamente — autoservicio real.

## Qué cambia

`POST /publico/solicitud-cuenta` pasa de "crear Prospecto pendiente" a **aprovisionar el tenant
completo** en una transacción:

1. **Empresa** (`activo = true`) con el nombre del despacho, NIT/CC y correo.
2. **Suscripción** a un **plan trial por defecto** (config por env) → la empresa nace usable.
3. **Usuario** administrador de la empresa (`rol = USUARIO`, `esAdminEmpresa = true`,
   `RolEmpresa.ADMINISTRADOR`), **inactivo** hasta que active por correo (token 48 h, igual que el
   alta de usuarios que ya existe).
4. **Prospecto** `GANADO` ligado a la empresa (`canalEntrada = WEB`, sin comercial) — solo para que
   el alta web quede en el funnel/métricas, sin exigir contacto ni comisión.
5. **Correo de invitación** (SES, reusando `enviarInvitacionCuenta`, contexto `empresa`) con el
   `activationUrl` al portal cliente `/activar?token=…`.

La activación (poner contraseña) reusa el flujo existente `setPassword` sin cambios.

### Formulario (landing `app/page.tsx`, sección "Crea tu cuenta")

| Campo (label nuevo)              | Se guarda en                                   | Req. |
|----------------------------------|------------------------------------------------|------|
| Despacho / abogado               | `Empresa.nombre`                               | sí   |
| Nit/cc                           | `Empresa.rfc`                                  | sí   |
| Tarjeta profesional              | `Usuario.tarjetaProfesional`                   | no   |
| Correo                           | `Usuario.email` (login) + `Empresa.email`      | sí   |
| Teléfono notificación personal   | `Usuario.telefono` (**campo nuevo**)           | sí   |
| Nombre usuario                   | `Usuario.nombre`                               | sí   |
| `website` (honeypot, oculto)     | —                                              | —    |

Se **quita el selector de plan** del alta (el plan es trial automático). Los planes siguen
mostrándose en la sección de precios como información.

## Alcance

- **API** (`lex-control-api`):
  - `modules/publico` — `solicitud-cuenta` reescrito (schema + service + repo) para aprovisionar
    Empresa + Suscripción + Usuario + Prospecto y disparar el correo.
  - `prisma/schema.prisma` — **único cambio de schema**: agregar `Usuario.telefono String?`.
    Se aplica con `pnpm push` (la DB no usa migrate en dev).
  - Reusa: `generateActivationToken`/`hashActivationToken`, `activationUrl`, `enviarInvitacionCuenta`
    + plantilla `invitacion` (contexto `empresa`), `enviarCorreo` (SES), `setPassword` (activación).
- **Client** (`lex-control-client`):
  - `app/page.tsx` — formulario "Crea tu cuenta" con los campos nuevos; quitar selector de plan;
    estados éxito/error ("revisa tu correo para activar la cuenta").
  - `lib/publico-api.ts` — tipo `SolicitudCuenta` actualizado.
- **No** toca: el modelo de roles/cuotas (reusa `RolEmpresa.ADMINISTRADOR`), `/activar`, ni el
  portal admin.

## Qué NO hace

- No agrega aprobación manual del admin: el alta es inmediata (el gate es la activación por correo).
- No cobra: la suscripción nace en el plan trial; el upgrade/pago es otro flujo.
- No agrega captcha real (sigue honeypot + rate-limit de `/publico`, como el resto).
- No crea Comisión para el Prospecto GANADO (no hay comercial en un alta autoservicio).
- No reemplaza `POST /publico/contacto` ("Habla con un asesor"), que sigue siendo lead a comercial.

## Decisiones del usuario (2026-06-26)

- **Plan**: trial por defecto (no el elegido en el form; no "sin plan").
- **Comercial**: sí dejar rastro → **Prospecto GANADO automático** ligado a la empresa.
- **Nit/cc**: un solo campo → `Empresa.rfc` (sirve para NIT de despacho o CC de abogado solo).
- **Teléfono de notificación**: agregar `Usuario.telefono` (más correcto que reusar `Empresa.telefono`).

## Riesgos / mitigaciones

- **Abuso** (endpoint público que ahora crea tenants reales): mitigado por honeypot + rate-limit
  (30/h) ya existentes, **cuenta inactiva** hasta activar por correo, **email único** (`Usuario.email`)
  y **NIT único** (`Empresa.rfc @unique`) que rechazan duplicados, y `Empresa.activo = false` que
  un admin puede usar para bloquear (ya existe). Correo duplicado → 409 con mensaje claro.
- **Correo no entregado**: el envío es best-effort (no rompe la transacción). Si falla, el admin
  puede reenviar con el `resetPassword` existente. Se documenta como pendiente de smoke real.
- **Plan trial inexistente**: si la clave de env no resuelve a un Plan, el alta degrada creando la
  empresa **sin** suscripción y loggea (no se bloquea el alta). El seed debe garantizar el plan.

## Rollback

Revertir el service de `solicitud-cuenta` a su versión "crea Prospecto NUEVO" y restaurar el form.
El campo `Usuario.telefono` es aditivo y nullable: puede quedar sin uso sin romper nada.
