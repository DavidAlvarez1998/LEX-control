# Diseño — procesos-categorias

## D1: FK `categoriaId` (1:N), NO M:N — decisión clave

`AreaPractica` usa M:N (`TipoProcesoArea`) porque un tipo **sirve a varias áreas** a la vez
(un Proceso Verbal es `civil` **y** `comercial-societario`). La **categoría es distinta**: la
*clase de proceso* es **mutuamente excluyente** — un proceso es Declarativo **o** Ejecutivo, no
ambos — y la navegación necesita **un único camino** por tipo. Por eso:

- `TipoProceso.categoriaId String?` + relación a `CategoriaProceso`, `onDelete: SetNull`.
- Categoría y Área son **ejes ortogonales**: categoría = navegación/clase (1 por tipo);
  área = etiqueta de práctica/filtro (N por tipo). Coexisten sin colisión.

## D2: Categorías "Próximamente" → flag en datos, no derivadas

Categorías vacías (teaser, p. ej. "Jurisdicción Voluntaria") **no se pueden derivar de los
tipos** (no hay ninguno). Por eso son entradas reales del catálogo con
`proximamente: Boolean @default(false)`. Una categoría `proximamente` se muestra como tarjeta
con badge y sin hojas; no es seleccionable hasta tener tipos.

## D3: Frontend genérico para TODAS las jurisdicciones

Se elimina el caso especial `esCivil`. Regla única:

- Si la jurisdicción seleccionada tiene **≥1 categoría activa** → se muestra el **nivel de
  categoría** (tarjetas), y al elegir una, las hojas son `tipos.filter(t => t.categoriaSlug === catSel)`.
- Si **no tiene categorías** → **lista plana** de tipos (comportamiento actual, retrocompatible).
- `?cat=` pasa a ser el **slug de categoría** para cualquier jurisdicción (antes solo civil).

## D4: `nombreVisual` reemplaza `TIPO_NOMBRE_VISUAL`

`TipoProceso.nombreVisual String?` opcional. El front muestra `nombreVisual ?? sinPrefijoProceso(nombre)`.
El seed pone `nombreVisual: "Ejecutivo"` al tipo "Proceso ejecutivo (singular o mixto)". El mapa
hardcodeado desaparece.

## D5: Tipos sin categoría no se pierden

Un tipo con `categoriaId = null` en una jurisdicción que SÍ tiene categorías se agrupa en una
tarjeta **"Otros"** (categoría sintética del front, no del catálogo). Garantiza que ningún tipo
quede inalcanzable, aun durante la transición.

## D6: Clasificación civil (asignación inicial del seed)

Basado en la clasificación del CGP (clases de proceso). Es **dato editable** por ADMIN, así que
una asignación discutible se corrige sin tocar código:

| Categoría (slug) | `proximamente` | Tipos civiles asignados |
|---|---|---|
| `declarativo` | no | Proceso verbal · Proceso verbal sumario · Proceso monitorio · Proceso de pertenencia · Restitución de inmueble arrendado |
| `ejecutivo` | no | Proceso ejecutivo (singular o mixto) → `nombreVisual: "Ejecutivo"` · Proceso ejecutivo (legado, 2 procesos, migrado a esta categoría) |

Nota (decisión del usuario 2026-06-20): Civil queda **solo con Declarativo y Ejecutivo**. Se
eliminaron las categorías `liquidacion` y `jurisdiccion-voluntaria` y los tipos Sucesión (civil)
y Reorganización (0 procesos, sacados del seed). El legado "Proceso ejecutivo" (2 procesos) se
movió a Ejecutivo (one-off en BD; no está en el seed). Queda pendiente unificar ese legado con
"Proceso ejecutivo (singular o mixto)" migrando sus 2 procesos.

## D7: Orden y consistencia

- Las categorías se ordenan por `orden` (como las áreas).
- El nivel de jurisdicción reusa el orden ya fijado en `JURISDICCION_LABEL` (Penal primero).

## D8: Seguridad / RBAC

- `GET /catalogo/categorias`: cualquier autenticado (como `/catalogo/areas`); `?incluirInactivas`
  solo ADMIN.
- POST/PATCH/DELETE categorías: **solo ADMIN** (catálogo global), igual que áreas.
- DELETE devuelve **409** si la categoría tiene tipos asignados.
