# Tasks — client-agenda-universal

## Schema (ya estaba aplicado en el working tree)
- [x] `SeguimientoComercial.clienteId String?` + `cliente Cliente?` `onDelete: SetNull` (BD ya nullable)

## API (comercial.router.ts / comercial.schemas.ts)
- [x] `createSeguimientoSchema.clienteId` opcional; `updateSeguimientoSchema` lo omite
- [x] `POST /seguimientos`: `assertCliente` solo si viene clienteId
- [x] Abrir gating de `GET/POST/PATCH /seguimientos`, `GET /agenda`, completar/cancelar/reabrir a `requireAuth` (baseline)
- [x] **Fix bug**: quitar `empresaIdRequerido` de la posición de middleware (era getter → colgaba la request)
- [x] `GET /agenda`: enriquecer items + vencidas con `registradoPor { nombre, roles, esAdminEmpresa }` (batch, scoped empresaId)

## Frontend cliente
- [x] nav.tsx: quitar `roles: ["COMERCIAL"]` del ítem Agenda
- [x] agenda/page.tsx: quitar `RolEmpresaGuard`
- [x] agenda-comercial-view.tsx: cliente opcional + buscador solo-al-escribir (sin pre-lista) + agendar sin cliente
- [x] vista admin: "Creado por {nombre} · {rol}" por ítem; filtro "Todos los miembros" (miembros activos); cliente null safe en celdas/filas
- [x] comercial-api.ts: `AgendaItem.cliente` opcional + `registradoPor`; `addSeguimiento(clienteId?)`

## Verify
- [x] `pnpm --dir lex-control-api build` (tsc) limpio
- [x] `pnpm --dir lex-control-client build` (next) limpio
- [x] `pnpm --dir lex-control-api test` → 374/374 (test módulo-gate reapuntado a /alertas + nuevo test baseline)
- [x] Smoke en vivo 3/3: USUARIO sin rol crea actividad SIN cliente (201) · ve su agenda (200) · admin ve `registradoPor` (nombre+roles). Limpieza: usuario+actividad temporales borrados
