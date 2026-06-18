# Tasks — Track 1: Migraciones + CI

## Migraciones (baseline) — lex-control-api
- [x] Generar `prisma/migrations/0_init/migration.sql` con `migrate diff --from-empty` (offline, 50 tablas)
- [x] `prisma/migrations/migration_lock.toml` (provider mysql)
- [x] `migrate resolve --applied 0_init` → marca baseline aplicado SIN ejecutar SQL ni tocar datos
- [x] `migrate status` = "Database schema is up to date!"
- [x] `MIGRATIONS.md` con el flujo seguro (NUNCA `migrate dev` contra DB compartida; diff offline + deploy)
- [ ] Smoke: `pnpm generate` + `pnpm build` siguen verdes; suite 442 verde

## CI — GitHub Actions
- [x] `lex-control-api/.github/workflows/ci.yml`: build (generate+tsc) + test (MySQL service + db push + seed + vitest)
- [x] `lex-control-client/.github/workflows/ci.yml`: build + lint
- [x] `lex-control-admin/.github/workflows/ci.yml`: build + lint

## Cierre
- [ ] Commit por repo (api + client + admin) + bump superrepo + commit del change
- [ ] (CI real corre en GitHub al hacer push — la primera corrida puede requerir tuning de seeds)
