# Proposal — Track 1: Migraciones Prisma (baseline) + CI

## Why
Dos huecos de **operación/producción** (no tocan el frontend):

1. **Sin historial de migraciones.** La DB se gestionaba con `prisma db push` → no hay
   migraciones versionadas. Consecuencia: ningún cambio de schema es **auditable ni
   reversible**, y `prisma migrate dev` (el script `pnpm migrate`) **RESETEA** la DB
   (pérdida de datos) — peligroso en una DB compartida/prod.
2. **Sin CI.** `tsc`/`build`/`test` solo corren local → regresiones pueden llegar a `main`.

## What
1. **Baseline de migraciones** (procedimiento oficial de Prisma para DB existente):
   `migrate diff --from-empty` genera `0_init/migration.sql` (50 tablas) y
   `migrate resolve --applied 0_init` lo marca aplicado **sin ejecutar SQL ni tocar datos**.
   → la DB queda "managed by Migrate", `migrate status` = up to date.
2. **Flujo seguro documentado** (`MIGRATIONS.md`): NUNCA `migrate dev` contra la DB
   compartida (resetea); nuevas migraciones vía `migrate diff` (offline) + `migrate deploy`.
3. **CI** (GitHub Actions) en los 3 repos: instala, `prisma generate`, `tsc`/`build`; el API
   además corre los **442 tests** contra un MySQL efímero (service container) sembrado con
   `db push` + seeds; los frontends corren `build` + `lint`.

## Non-goals
- No migrar `db push` del flujo de prototipado local (sigue disponible); solo se agrega el
  carril de migraciones para prod. No tocar el frontend ni el schema (cero cambios de datos).

## Rollback
El baseline es reversible (borrar `prisma/migrations/` + la fila de `_prisma_migrations`).
La CI es aditiva (archivos `.github/workflows`). El schema/datos NO se tocaron.
