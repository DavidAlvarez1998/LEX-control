# procesos-categorias

## Por qué

La vista de **Procesos** inserta un nivel de **categorías** (la *clase de proceso*:
Declarativo / Ejecutivo / Liquidación / Jurisdicción Voluntaria) entre la Jurisdicción
y el Tipo. Hoy ese nivel está **hardcodeado en el frontend y solo para Civil**
(`CIVIL_SUBARBOL` en `lex-control-client/src/app/(dashboard)/procesos/page.tsx`),
más un hack de renombre visual (`TIPO_NOMBRE_VISUAL`). Dos problemas reales:

1. **No escala.** Las otras jurisdicciones (Laboral, Familia, Contencioso…) van a crecer
   con sus propias clases de proceso. Con el modelo actual, cada una exigiría otro bloque
   `if (esXxx)` hardcodeado en React.
2. **Bug de cobertura (tipos huérfanos).** De los **8** tipos civiles del catálogo, el
   sub-árbol solo enruta **3** (Verbal, Verbal Sumario, Ejecutivo). Los otros **5**
   (Monitorio, Sucesión, Pertenencia, Restitución de inmueble arrendado, Reorganización)
   **no tienen camino** por la navegación Jurisdicción→Civil (solo aparecen vía la vista
   "Sección"). Quedan invisibles bajo Civil.

La "categoría" es una **taxonomía legal real** (clase de proceso del CGP) que aplica a
todas las jurisdicciones, no un detalle visual de Civil. Debe vivir en datos, no en código.

## Qué se construye

1. **Modelo nuevo `CategoriaProceso`** (espeja `AreaPractica`): `slug` único, `nombre`,
   `jurisdiccion`, `orden`, `activo`, `proximamente`. Catálogo global gestionado por ADMIN.
2. **FK `TipoProceso.categoriaId`** (opcional, `onDelete: SetNull`) — **una sola** categoría
   por tipo (la clase es excluyente). Y **`TipoProceso.nombreVisual`** opcional (mata el hack
   `TIPO_NOMBRE_VISUAL`).
3. **API**: `GET /catalogo/categorias` (con `?jurisdiccion`, `?incluirInactivas` para ADMIN)
   + CRUD ADMIN (POST/PATCH/DELETE, 409 si tiene tipos); el DTO de tipo expone `categoriaSlug`
   y `nombreVisual`.
4. **Seed**: las 4 categorías civiles + asignación de los **8** tipos civiles a su categoría
   (resuelve los huérfanos). Patrón upsert idempotente por `slug`.
5. **Frontend cliente genérico**: `/procesos` deriva el nivel de categoría **del catálogo
   para CUALQUIER jurisdicción**. Se borran `CIVIL_SUBARBOL`, `TIPO_NOMBRE_VISUAL` y el
   caso especial `esCivil`.
6. **Admin**: `CategoriasManager` (espejo de `AreasManager`) en `/catalogo-procesos` +
   selector de categoría al crear/editar un tipo.

## Impacto

- **Schema:** modelo `CategoriaProceso` + `TipoProceso.categoriaId` + `TipoProceso.nombreVisual`
  — aditivo, aplicar con `pnpm push`.
- **API:** módulo catálogo (router→service→repository→dto) gana categorías; `serializeTipo`
  añade 2 campos; seed extendido.
- **Frontend cliente:** `procesos/page.tsx` data-driven (borra hardcode); `lib/procesos.ts`
  y `lib/procesos-api.ts` ganan el type + fetch.
- **Admin:** componente nuevo reusando el patrón de áreas.
- **Reusa:** el patrón íntegro de `AreaPractica` (modelo, seed upsert, router CRUD, manager admin).

## Rollback

100% aditivo y opcional: `categoriaId`/`nombreVisual` son nullable; sin categorías activas el
front cae a **lista plana** (comportamiento previo, sin el hardcode). Rollback = revertir schema
(`db push`), quitar el endpoint y restaurar el render plano. No toca procesos existentes ni la
facturación/áreas.
