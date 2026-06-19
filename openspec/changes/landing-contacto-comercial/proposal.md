# landing-contacto-comercial

## Por qué

La landing del portal cliente debe servir como **canal de contacto comercial**: un visitante
deja sus datos → se crea un **Prospecto sin asignar** → el admin lo asigna a un comercial (a
cualquiera) **o** un comercial lo **toma** él mismo → luego lo contactan y le hacen seguimiento
en el embudo que ya existe.

## Qué YA existe (se reutiliza, no se reinventa)

- `Prospecto.comercialId` es **nullable** → "sin asignar" es un estado natural del modelo.
- `CanalEntrada.WEB` ya existe.
- `/publico/*` es público (sin auth), con **rate-limit** (30/h) y patrón **honeypot** anti-spam;
  ya hay `POST /publico/solicitud-cuenta` que crea un Prospecto WEB sin asignar.
- `ventas.listProspectos(estado, canal, comercialId)` + el comercial solo ve los suyos (`scope`).
- `ventas` ya deja que el **admin asigne** (`PATCH` set `comercialId`, valida rol con `assertComercial`).
- Embudo, `SeguimientoProspecto`, agenda comercial y comisiones ya operan sobre el Prospecto.

## Qué se construye

**Decisiones del usuario (2026-06-19):** endpoint **nuevo** `/publico/contacto` (no reusar
solicitud-cuenta); asignación = **admin a cualquiera + comercial se auto-toma**.

1. **API pública** — `POST /publico/contacto` (sin auth, rate-limited, honeypot):
   crea un Prospecto `canalEntrada = WEB`, **sin asignar** (`comercialId = null`), `estado = NUEVO`,
   con el mensaje del visitante en `notas` (prefijo "Contacto desde landing:"). Campos: contacto
   (nombre) + al menos uno de (correo, teléfono); empresa y mensaje opcionales. Distinción
   contacto vs solicitud-cuenta por el texto de `notas` (sin tocar schema; un subcanal queda como
   posible mejora futura).
2. **API ventas** — acción **"tomar"** (auto-asignación): un `COMERCIAL` se asigna un prospecto
   **sin dueño** (`comercialId: null → t.userId`). Rechaza con **409** si ya tiene comercial.
   La asignación por el admin a cualquier comercial ya existe (se ratifica en spec).
3. **API ventas** — filtro **"sin asignar"** en `listProspectos` (`comercialId = null`), para que
   admin y comerciales vean la bandeja de no asignados.
4. **Client landing** — sección/formulario **"Habla con un asesor"**: nombre, correo/teléfono,
   mensaje (empresa opcional) → `POST /publico/contacto`; estados de éxito/error; honeypot oculto.
5. **Admin prospectos** — vista/filtro **"Sin asignar"**; botón **"Tomar"** (comercial) y
   **"Asignar a…"** (admin); badge de canal (WEB/Contacto) para distinguir el origen landing.

## Impacto

- **API**: `modules/publico` (nuevo endpoint + schema + service) y `modules/ventas` (acción tomar
  + filtro sin-asignar). **Sin cambio de schema** (`comercialId` ya nullable, `CanalEntrada.WEB` ya existe).
- **Client**: landing (`app/page.tsx`) — formulario de contacto.
- **Admin**: `prospectos` (bandeja sin asignar + Tomar/Asignar).
- RBAC: el endpoint público es abierto (con rate-limit+honeypot); "tomar" exige rol COMERCIAL;
  "asignar a cualquiera" exige admin (lo existente).

## Fuera de alcance

- Notificación/email automático al comercial cuando entra un contacto (otro change).
- Captcha real (por ahora honeypot + rate-limit, como el resto de `/publico`).
- Subcanal/enum para distinguir "contacto" de "solicitud de cuenta" (hoy se distingue por `notas`).

## Decisiones del usuario (2026-06-19)
- Endpoint **nuevo** `/publico/contacto` (form liviano + mensaje), no reusar solicitud-cuenta.
- Asignación: **admin asigna a cualquier comercial** + **comercial puede auto-tomar** uno sin asignar.
