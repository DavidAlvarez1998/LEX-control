# Tasks — landing-contacto-comercial

## API · publico (nuevo endpoint)
- [x] `publico.schemas.ts`: `contactoSchema` (nombreContacto req; email/telefono — al menos uno;
      nombreEmpresa?, mensaje?, honeypot `website?`).
- [x] `publico.service.ts`: `contactar(body)` → honeypot guard; crea Prospecto `canalEntrada=WEB`,
      `comercialId=null`, `estado=NUEVO`, `notas="Contacto desde landing: …"`. Reusa `PublicoRepository.createProspecto`.
- [x] `publico.router.ts`: `POST /publico/contacto` (validate, asyncHandler, 201).
- [x] Tests: crea sin asignar · falta email+tel → 400 · honeypot → ok sin crear.

## API · ventas (tomar + filtro sin-asignar)
- [x] `ventas.service.ts`: `tomarProspecto(t, id)` → requiere rol COMERCIAL; si `comercialId!=null` → 409;
      set `comercialId = t.userId`. (No permitir robar uno ajeno.)
- [x] `ventas.service.ts`: `listProspectos` acepta `comercialId="ninguno"` (o flag `sinAsignar`) → `comercialId: null`.
- [x] `ventas.router.ts`: `POST /ventas/prospectos/:id/tomar` (requireAuth + rol COMERCIAL) + soporte del filtro.
- [x] Tests: comercial toma sin-dueño OK · tomar ya-asignado → 409 · filtro sin-asignar devuelve solo null · admin asigna a cualquiera (ya existe, ratificar).

## Client · landing
- [x] `lib`: `enviarContacto(body)` → `POST /publico/contacto` (sin token).
- [x] `app/page.tsx` (o componente nuevo `ContactoComercial`): sección "Habla con un asesor" con
      form (nombre, correo/teléfono, mensaje, empresa opcional, honeypot oculto), estados éxito/error.

## Admin · prospectos
- [x] Filtro/pestaña **"Sin asignar"** (comercialId null) en la lista.
- [x] Botón **"Tomar"** (visible a COMERCIAL) → `POST /ventas/prospectos/:id/tomar`.
- [x] Botón **"Asignar a…"** (admin) → reusa el PATCH de asignación existente.
- [x] Badge de canal (WEB / contacto landing) en la fila/detalle.

## Verificación
- [x] `tsc` + tests api verdes; build admin + client.
- [ ] Smoke: enviar contacto desde landing → aparece sin asignar → comercial lo toma / admin lo asigna.
