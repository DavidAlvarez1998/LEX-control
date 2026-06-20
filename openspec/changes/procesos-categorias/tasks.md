# Tareas — procesos-categorias

> ESTADO (2026-06-20): Fases 1–4 APLICADAS y verificadas estáticamente. Gate verde:
> `pnpm push`+`generate` OK · `seed:catalogo` OK (4 categorías, 38 tipos) · API `tsc` +
> `vitest` 449/449 · cliente `tsc`+`build` · admin `tsc`+`build` · smoke de service real
> (listCategorias/listTipos devuelven categoriaSlug+nombreVisual+proximamente). PENDIENTE:
> smoke manual de UI (navegar /procesos y el manager admin) — 5.4/5.5/5.6. SIN commit.


## Fase 1 — Schema + seed (lex-control-api)
- [ ] 1.1 `prisma/schema.prisma`: modelo `CategoriaProceso` (id, slug @unique, nombre, jurisdiccion, orden, activo, proximamente, relación `tipos`) + `@@map("categorias_proceso")`.
- [ ] 1.2 `prisma/schema.prisma`: en `TipoProceso` agregar `categoriaId String?`, relación `categoria CategoriaProceso?` (onDelete: SetNull), `nombreVisual String?`, `@@index([categoriaId])`.
- [ ] 1.3 `pnpm push` + `pnpm generate`.
- [ ] 1.4 `src/seed-catalogo.ts`: lista `CATEGORIAS` (4 civiles, ver design D6) + upsert idempotente por slug.
- [ ] 1.5 `prisma/seed-tipos.json`: agregar `categoriaSlug` a los 8 tipos civiles; `nombreVisual` al ejecutivo.
- [ ] 1.6 `src/seed-catalogo.ts`: en el upsert de tipos, resolver `categoriaSlug`→id y setear `categoriaId` + `nombreVisual`.
- [ ] 1.7 `pnpm seed:catalogo`.

## Fase 2 — API catálogo (lex-control-api)
- [ ] 2.1 `catalog.repository.ts`: métodos `listCategorias`, `createCategoria`, `updateCategoria`, `deleteCategoria`, `countTiposDeCategoria`.
- [ ] 2.2 `catalog.service.ts`: lógica + RBAC (ADMIN escribe; 409 si tiene tipos).
- [ ] 2.3 `catalog.schemas.ts`: `createCategoriaSchema`/`updateCategoriaSchema`; `createTipoProcesoSchema` acepta `categoriaId?` y `nombreVisual?`.
- [ ] 2.4 `catalog.dto.ts`: `serializeTipo` añade `categoriaSlug` (aplanado) y `nombreVisual`; `serializeCategoria`.
- [ ] 2.5 `catalog.router.ts`: `GET /catalogo/categorias` (+`?jurisdiccion`,`?incluirInactivas`), `POST/PATCH/DELETE /catalogo/categorias[/:id]`.

## Fase 3 — Frontend cliente (lex-control-client)
- [ ] 3.1 `lib/procesos.ts`: type `CategoriaProceso`; `TipoProceso += categoriaSlug?, nombreVisual?`.
- [ ] 3.2 `lib/procesos-api.ts`: `getCategorias()`.
- [ ] 3.3 `app/(dashboard)/procesos/page.tsx`: cargar categorías; render genérico Jurisdicción→Categoría→Tipo; borrar `CIVIL_SUBARBOL`, `TIPO_NOMBRE_VISUAL`, caso `esCivil`; `nombreVisual` del tipo; bucket "Otros" (D5).

## Fase 4 — Admin (lex-control-admin)
- [ ] 4.1 `components/categorias-manager.tsx` (espejo de `areas-manager.tsx`).
- [ ] 4.2 `app/(dashboard)/catalogo-procesos/page.tsx`: montar el manager + selector de categoría al crear/editar tipo.
- [ ] 4.3 `lib/*`: fetch de categorías.

## Fase 5 — Verificación (cómo lo vemos)
- [ ] 5.1 `tsc --noEmit` en api + client + admin.
- [ ] 5.2 `pnpm build` client + admin; `pnpm vitest` api (no regresiones).
- [ ] 5.3 `pnpm seed:catalogo` aplica categorías sin error (idempotente al re-correr).
- [ ] 5.4 Smoke: `/procesos` → "Ordinaria · Civil" muestra 4 categorías; "Declarativo" lista 5 tipos; "Liquidación" lista 2; "Jurisdicción Voluntaria" = Próximamente; los 5 antes huérfanos ahora son alcanzables.
- [ ] 5.5 Smoke: una jurisdicción sin categorías (p. ej. Penal) sigue mostrando lista plana.
- [ ] 5.6 Smoke admin: crear/editar/desactivar una categoría; DELETE con tipos = 409.
