# spec — correos de cuenta (invitación / restablecimiento)

Comportamiento canónico de los correos transaccionales de cuenta. Consume `enviarCorreo`
(Amazon SES) de [[convencion-integraciones-externas]]; no introduce transporte propio.

## Disparadores

| Disparador | Endpoint | Tipo de correo | Destinatario |
|---|---|---|---|
| Admin de plataforma crea usuario | `POST /usuarios` | Invitación | el usuario creado |
| Admin de empresa crea miembro | `POST /mi-empresa/usuarios` | Invitación | el miembro creado |
| Admin de empresa reenvía activación | `POST /mi-empresa/usuarios/:id/activation` | Invitación | el miembro |
| Admin de plataforma restablece contraseña | `POST /usuarios/:id/reset-password` | Restablecimiento | el usuario afectado |

No hay correo self-service de "olvidé mi contraseña": el reset siempre lo origina un admin.

## Contenido del correo

- Idioma español, cuerpo HTML sobrio (el proveedor lo envuelve en su plantilla con logo).
- Debe incluir: saludo por nombre, una línea de propósito (invitación vs restablecimiento), un
  **botón/enlace** a la `activationUrl` ya construida, el enlace en texto plano como fallback, la
  nota de **expiración a las 48 horas**, y una línea "si no esperabas este correo, ignóralo".
- La `activationUrl` apunta a `/activar?token=…` en el portal correcto (`clientUrl` para usuarios de
  empresa, `adminUrl` para ADMIN/COMERCIAL), según la lógica existente `activationUrl(raw, rol)`.
- El `subject` no puede ser vacío y difiere por tipo (invitación vs restablecimiento).

## Garantías (no negociables)

- **El envío es best-effort y no rompe la operación.** La creación/restablecimiento se confirma
  primero; el correo se envía después, fuera de la transacción. Un fallo de SES NO aborta ni revierte
  la operación ni lanza error al cliente.
- **Respaldo siempre disponible.** La respuesta sigue incluyendo `activationUrl` y agrega
  `correoEnviado: boolean`. La UI muestra el resultado del envío y conserva el enlace copiable.
- **Cambio aditivo.** Ningún campo existente cambia de forma ni semántica; solo se añade `correoEnviado`.

## No-objetivos

- Persistir historial/auditoría de correos enviados.
- Reintentos automáticos o cola asíncrona.
- Notificar por SMS o llamada en estos flujos.
