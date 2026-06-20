# remove-integraciones-estatales

## Por qué

La capacidad **Integraciones Estatales** (jurisprudencia de la Corte Constitucional vía la API
pública Socrata/SODA de `datos.gov.co`, + el motor de sincronización de actuaciones judiciales por
radicado con proveedores tipo CPNU/RUES) **nunca quedó conectada ni validada en producción**:

- El adapter de la Corte Constitucional apuntaba a un `datasetId` **placeholder** (`9kfd-kup7`) →
  devolvía `502` en vivo (nunca se configuró el dataset real de la relatoría).
- La sincronización de actuaciones (Fase B) estaba **bloqueada** por infraestructura/llaves
  (CPNU requiere scraping con Redis+Playwright; RUES requiere llaves de pago). En dev solo corría
  contra un **mock** determinista; en producción quedaba apagada.
- En el portal, el bloque "Actuaciones del juzgado" estaba **oculto** (`MOSTRAR_ACTUACIONES_JUZGADO
  = false`) y la landing **anunciaba** la función ("Consulta judicial", "Datos del juzgado al día")
  sin respaldo real.

Mantener código y propaganda de una función inexistente confunde y da impresión de algo que no se
entrega. Se decide **eliminarla por completo** del proyecto.

## Qué se elimina

### API (`lex-control-api`)
- Módulo completo `src/modules/integraciones/` (adapter Corte Constitucional, motor de sync,
  mock de actuaciones, proveedores, crypto de credenciales, router/service/repository/schemas/types).
- Montaje de rutas `app.use("/integraciones", …)` y su import en `src/app.ts`.
- Bloque de configuración `env.integraciones` en `src/config/env.ts`
  (`CORTE_CONST_API_URL`, `CORTE_CONST_DATASET`, `SOCRATA_APP_TOKEN`, `INTEGRACIONES_*`).
- Tests `tests/integraciones.test.ts`, `tests/integraciones-sync.test.ts` y el script
  `scripts/smoke-integraciones-sync.ts`.
- **Modelos Prisma** `ActuacionJudicial`, `IntegrationSyncLog`, `ProviderConfig`, el enum
  `EstadoSyncIntegracion` y la relación `Proceso.actuaciones` (tablas
  `actuaciones_judiciales`, `integration_sync_logs`, `provider_configs`).

### Portal cliente (`lex-control-client`)
- `src/lib/integraciones-api.ts` y `src/components/actuaciones-proceso.tsx`.
- Uso del bloque "Actuaciones del juzgado" en `procesos/[id]` y la flag
  `MOSTRAR_ACTUACIONES_JUZGADO`.
- Las tarjetas de marketing "Consulta judicial" y "Datos del juzgado al día" en la landing.

### OpenSpec
- Se retira la spec canónica `openspec/specs/integraciones-estatales/`.
  Los changes en `openspec/changes/archive/` que la introdujeron se conservan como **historia**.

## Impacto / migración

- **Base de datos:** las 3 tablas (`actuaciones_judiciales`, `integration_sync_logs`,
  `provider_configs`) **nunca existieron en la BD viva** (verificado: `Table 'LEX.…' doesn't
  exist`) — el esquema las declaraba pero nunca se aplicaron. Por eso **no se requiere `pnpm push`**:
  esquema y base ya quedan consistentes tras quitarlas del schema.
- **Contrato HTTP:** desaparece el prefijo `/integraciones` (sin clientes reales que dependan de él).
- Sin impacto en otros módulos: ninguna otra capa importaba el módulo.

## Reactivación futura

Si más adelante se retoma la integración judicial, se parte desde cero con un dataset/proveedor
real ya validado (no se "reactiva" código muerto).
