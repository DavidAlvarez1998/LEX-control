# design — correos-cuenta-invitacion-reset

## Descubrimientos (estado actual, verificado en código)

- `enviarCorreo({to,subject,html}) → {enviado, messageId}` en
  `notificaciones/correo.client.ts`. **Lanza `HttpError(502)`** si el transporte falla
  (`notificaciones.http.ts`). No hay validación zod en el módulo; valida el caller.
- `activationUrl(raw, rol)` en `usuarios/usuarios.shared.ts`:
  `${rol==="USUARIO" ? env.clientUrl : env.adminUrl}/activar?token=${raw}`. Sirve igual para
  invitación y para reset (ambos van a `/activar?token=` → `POST /auth/set-password`).
- `ACTIVATION_TTL_MS = 48h` (usuarios.shared.ts). Las plantillas mencionan "48 horas".
- **createUsuario** (`usuarios.service.ts`) genera token dentro de una `$transaction`, retorna
  `{ user, activationUrl }`. `user` viene de `PUBLIC_SELECT` → **incluye `email` y `nombre`**.
- **resetPassword** (`usuarios.service.ts`) → `updateForReset` retorna `usuario` (tiene `rol`);
  hay que asegurar que el select traiga también `email` y `nombre` para poder enviar.
- **createMiembro** y **resendActivation** (`mi-empresa.service.ts`) mismo patrón; `createMiembro`
  retorna el `user` (con email/nombre), `resendActivation` retorna `{ activationUrl }` — verificar
  que tenga email/nombre del miembro (si no, leerlos en el service antes de enviar).

## Punto clave: enviar FUERA de la transacción

La creación de usuario corre en `prisma.$transaction`. **No** meter el `await enviarCorreo` dentro:
una red lenta/caída no debe abortar la creación ni alargar el lock de sillas. Patrón:

```ts
const { user, activationUrl } = await crearEnTx(...);   // commit ya hecho
const correoEnviado = await enviarInvitacionCuenta({     // best-effort, nunca lanza
  to: user.email, nombre: user.nombre, activationUrl, contexto,
});
return { user, activationUrl, correoEnviado };
```

`enviarInvitacionCuenta` envuelve en try/catch:

```ts
export async function enviarInvitacionCuenta(p): Promise<boolean> {
  try {
    const { subject, html } = plantillaInvitacion(p);
    const { enviado } = await enviarCorreo({ to: p.to, subject, html });
    return enviado;
  } catch (err) {
    logger.warn({ err, to: p.to }, "no se pudo enviar correo de invitación");
    return false;
  }
}
```

## Plantillas (`plantillas-cuenta.ts`)

Funciones puras → fáciles de testear sin red. El `contexto` ajusta el saludo/copy:

- `contexto: "admin"` → "Te invitaron a administrar LEX Control."
- `contexto: "comercial"` → "Te crearon una cuenta de comercial en LEX Control."
- `contexto: "empresa"` → "Te invitaron a unirte al equipo de {empresaNombre} en LEX Control."
  (si no hay nombre de empresa disponible barato, usar copy genérico de equipo).

Cuerpo común: saludo por `nombre`, una línea de qué es, **botón** `Activar mi cuenta` (anchor con
estilo inline; SES respeta HTML) + el enlace en texto plano como fallback, nota "el enlace vence en
48 horas", y "si no esperabas este correo, ignóralo". Reset cambia el verbo: "Restablece tu
contraseña" / botón `Definir nueva contraseña`.

Reglas de calidad probadas en unit test: el `html` **contiene** `activationUrl`, **no** contiene la
marca `[[falta:` (placeholder sin resolver), y el `subject` no está vacío.

## Contrato de respuesta (aditivo, no rompe nada)

| Endpoint | Antes | Ahora |
|---|---|---|
| `POST /usuarios` | `{ user, activationUrl }` | `+ correoEnviado: boolean` |
| `POST /usuarios/:id/reset-password` | `{ activationUrl }` | `+ correoEnviado: boolean` |
| `POST /mi-empresa/usuarios` | `{ user, activationUrl }` | `+ correoEnviado: boolean` |
| `POST /mi-empresa/usuarios/:id/activation` | `{ activationUrl }` | `+ correoEnviado: boolean` |

Los clientes viejos ignoran el campo nuevo; la UI lo usa para el mensaje de confirmación.

## Frontend

`activationUrl` ya se muestra hoy. Solo se añade, encima del bloque del link:
- `correoEnviado === true` → "✓ Correo enviado a {email}".
- `correoEnviado === false` → "⚠ No se pudo enviar el correo. Comparte este enlace:".
El bloque del link (copiar) se conserva en ambos casos como respaldo (decisión del usuario).

## Entornos / dev

En dev `NOTIFICAR_API_URL` apunta al host interno (no alcanzable) → `enviarCorreo` fallará con 502,
`correoEnviado=false`, y el flujo sigue con el link visible. Es el comportamiento deseado: no hay que
desactivar nada. En prod/staging se setea `NOTIFICAR_API_URL` al host alcanzable y el correo entrega.

## Preguntas abiertas / a confirmar al implementar

- Nombre de empresa en el correo de invitación de equipo: ¿vale la pena un join extra solo para el
  copy? Si encarece, usar copy genérico ("tu equipo en LEX Control"). Decidir en impl.
- `resendActivation`: confirmar si su select trae email/nombre; si no, añadirlos.
