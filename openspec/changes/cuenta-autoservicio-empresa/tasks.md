# Tareas — cuenta-autoservicio-empresa

> Aplicar por capas. Gate de verificación: `tsc` verde en los 3 repos + `pnpm test` (vitest API).
> Smoke real del correo queda pendiente (no bloquea el merge, sí el cierre del change).
> Estado: IMPLEMENTADO+VERIFICADO (tests/tsc/build), SIN COMMIT. Falta smoke real + commit.

## 1. Schema (`lex-control-api`)
- [x] `schema.prisma`: agregar `Usuario.telefono String?` (comentario: notificación personal).
- [x] `pnpm push` (NO `pnpm migrate` — resetea la DB) + `pnpm generate`. (aplicado a DEMO-ROUTER)

## 2. Config / plan trial
- [x] `env`: agregar `selfSignupPlanClave` (`PLAN_AUTOSERVICIO_CLAVE`, default `"trial"`).
- [x] Sembrar en seed-foundations un Plan `trial` `activo=false` (oculto del catálogo público) con
      cuotas `ADMINISTRADOR:1` + `JURIDICO:1`. Verificado en DB.

## 3. API — `modules/publico`
- [x] `publico.schemas.ts`: `solicitudCuentaSchema` nuevo (nombreEmpresa, nit, tarjeta?, email,
      telefono, nombreContacto, website?). Quitados emailEmpresa/telefonoEmpresa/planClave.
- [x] `publico.service.ts`: `solicitarCuenta()` reescrito → tx Empresa + Suscripción(trial) +
      Usuario(ADMINISTRADOR, PENDIENTE, token 48h) + Prospecto GANADO; correo best-effort fuera de tx.
      Reusa `generateActivationToken`, `activationUrl`, `enviarInvitacionCuenta` contexto `"empresa"`.
      409 si email/NIT existen. `resolverPlanTrial` con degradación (sin suscripción + log).
- [x] `publico.repository.ts`: helpers transaccionables (findUsuarioByEmail/findEmpresaByRfc/
      createEmpresa/createSuscripcion/createUsuario/createRolEmpresa).
- [x] `publico.router.ts`: sin cambios (honeypot → 200 no-op; éxito 201; 409 vía error middleware).
- [x] Tests (vitest): honeypot, alta feliz (Empresa+Usuario+Suscripción+Prospecto GANADO), plan
      inexistente→sin suscripción, email 409, NIT 409, payload inválido 400, no-inyección de
      estado/rol/empresaId/planId. **518/518 verde.**

## 4. Client — landing (`lex-control-client`)
- [x] `lib/publico-api.ts`: tipo `SolicitudCuenta` actualizado (nombreEmpresa, nit, tarjeta?, email,
      telefono, nombreContacto, website?).
- [x] `app/page.tsx` "Crea tu cuenta": campos nuevos con los labels pedidos; quitado selector de plan;
      honeypot oculto; "Quiero este plan"→"Empezar gratis" (solo baja al form).
- [x] Estado de éxito: "Revisa tu correo … para activar tu cuenta y entrar a tu despacho".
- [x] Estado de error: 409 muestra el mensaje del servidor (correo/NIT) vs error genérico.

## 5. Verificación
- [x] `tsc` verde en api + client.
- [x] vitest API verde (518/518). eslint client 0 errores. `next build` verde.
- [ ] Smoke manual: enviar form → llega correo → `/activar?token=` → set password → login como
      ADMINISTRADOR de la empresa nueva. (pendiente, requiere SES real)

## 6. Cierre
- [x] Actualizar `state.yaml` (apply/verify).
- [ ] Archivar el change a `openspec/specs/` (tras smoke + commit).
- [ ] Commit por capas (api / client) en rama `feat/cuenta-clientes`.
