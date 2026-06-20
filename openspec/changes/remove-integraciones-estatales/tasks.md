# Tasks — remove-integraciones-estatales

## API (lex-control-api)
- [x] Borrar el módulo `src/modules/integraciones/` completo
- [x] Quitar `import` y `app.use("/integraciones", …)` en `src/app.ts`
- [x] Quitar el bloque `env.integraciones` en `src/config/env.ts`
- [x] Borrar `tests/integraciones.test.ts`, `tests/integraciones-sync.test.ts`
- [x] Borrar `scripts/smoke-integraciones-sync.ts`
- [x] Quitar del schema Prisma: `Proceso.actuaciones`, enum `EstadoSyncIntegracion`,
      modelos `ActuacionJudicial`, `IntegrationSyncLog`, `ProviderConfig`
- [x] `pnpm generate` — regenerar cliente Prisma
- [x] `pnpm push` — **no requerido**: las 3 tablas (`actuaciones_judiciales`,
      `integration_sync_logs`, `provider_configs`) nunca existieron en la BD viva
      (verificado: `Table 'LEX.…' doesn't exist`). Esquema y DB ya consistentes.
- [x] Gate: `tsc --noEmit` + `vitest` (449 tests verdes)

## Portal cliente (lex-control-client)
- [x] Borrar `src/lib/integraciones-api.ts` y `src/components/actuaciones-proceso.tsx`
- [x] Quitar uso/flag en `procesos/[id]/page.tsx`
- [x] Quitar tarjetas de marketing en la landing (`src/app/page.tsx`)
- [x] Gate: `tsc --noEmit` + `next build` verdes

## OpenSpec
- [x] Documentar la eliminación en este change (proposal + spec delta REMOVED)
- [x] Borrar la spec canónica `openspec/specs/integraciones-estatales/`
