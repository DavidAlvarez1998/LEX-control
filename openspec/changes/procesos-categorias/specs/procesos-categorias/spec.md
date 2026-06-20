# procesos-categorias

Capability: un nivel de **categoría** (clase de proceso) entre Jurisdicción y Tipo, gestionado
en datos (catálogo `CategoriaProceso`), que estructura la navegación de Procesos de forma
escalable para cualquier jurisdicción. Reemplaza el sub-árbol civil hardcodeado.

## ADDED Requirements

### Requirement: Catálogo de categorías de proceso por jurisdicción
El sistema SHALL mantener un catálogo `CategoriaProceso` donde cada categoría pertenece a una
`Jurisdiccion` y tiene `slug` único, `nombre`, `orden`, `activo` y `proximamente`. El catálogo es
global y solo ADMIN lo modifica.

#### Scenario: Listar categorías activas de una jurisdicción
- **GIVEN** la jurisdicción `ORDINARIA_CIVIL` con categorías `declarativo`, `ejecutivo`, `liquidacion`, `jurisdiccion-voluntaria`
- **WHEN** un usuario autenticado pide `GET /catalogo/categorias?jurisdiccion=ORDINARIA_CIVIL`
- **THEN** recibe las categorías activas ordenadas por `orden`
- **AND** un usuario no-ADMIN no ve las inactivas (sin `?incluirInactivas`)

### Requirement: Un tipo de proceso pertenece a una sola categoría
`TipoProceso` SHALL referenciar **como máximo una** `CategoriaProceso` vía `categoriaId` opcional.
Borrar una categoría SHALL dejar `categoriaId = null` en sus tipos (no borra el tipo).

#### Scenario: Tipo asignado a categoría
- **GIVEN** el tipo "Proceso verbal" con `categoriaId` de `declarativo`
- **WHEN** se serializa al frontend
- **THEN** el DTO incluye `categoriaSlug: "declarativo"`

#### Scenario: Borrar categoría con tipos
- **GIVEN** la categoría `declarativo` con tipos asignados
- **WHEN** un ADMIN hace `DELETE /catalogo/categorias/:id`
- **THEN** responde **409** y no borra (debe reasignar/desactivar primero)

### Requirement: Navegación de Procesos data-driven por categoría
La vista `/procesos` SHALL derivar el nivel de categoría **del catálogo** para cualquier
jurisdicción, sin lógica hardcodeada por jurisdicción.

#### Scenario: Jurisdicción con categorías muestra el nivel categoría
- **GIVEN** "Ordinaria · Civil" con 4 categorías
- **WHEN** el usuario abre esa jurisdicción
- **THEN** ve tarjetas de categoría (Declarativo, Ejecutivo, Liquidación, Jurisdicción Voluntaria)
- **AND** al elegir "Declarativo" ve los tipos cuya categoría es `declarativo`

#### Scenario: Jurisdicción sin categorías cae a lista plana
- **GIVEN** una jurisdicción sin categorías activas (p. ej. Penal)
- **WHEN** el usuario la abre
- **THEN** ve la lista plana de tipos (comportamiento previo), sin nivel de categoría

#### Scenario: Categoría "Próximamente"
- **GIVEN** la categoría `jurisdiccion-voluntaria` con `proximamente = true` y sin tipos
- **WHEN** se muestra en la grilla de categorías
- **THEN** aparece con badge "Próximamente" y no es seleccionable

### Requirement: Cobertura completa (sin tipos huérfanos)
Todo `TipoProceso` con categoría SHALL ser alcanzable por la navegación de su jurisdicción. Un
tipo sin categoría en una jurisdicción que sí tiene categorías SHALL agruparse bajo una tarjeta
sintética "Otros" del frontend, nunca quedar inalcanzable.

#### Scenario: Los antes huérfanos quedan enrutados
- **GIVEN** los tipos civiles Monitorio, Sucesión, Pertenencia, Restitución y Reorganización
- **WHEN** se navega "Ordinaria · Civil"
- **THEN** todos son alcanzables desde su categoría (Declarativo o Liquidación)

### Requirement: Nombre visual del tipo
`TipoProceso` SHALL soportar `nombreVisual` opcional; el frontend SHALL mostrar
`nombreVisual` cuando exista, en lugar del nombre completo del catálogo.

#### Scenario: Ejecutivo se muestra abreviado
- **GIVEN** el tipo "Proceso ejecutivo (singular o mixto)" con `nombreVisual = "Ejecutivo"`
- **WHEN** se lista bajo su categoría
- **THEN** la tarjeta muestra "Ejecutivo"

### Requirement: Gestión admin de categorías
ADMIN SHALL crear, editar, activar/desactivar, reordenar y eliminar categorías desde el portal
admin; el resto de usuarios no.

#### Scenario: ADMIN crea una categoría
- **GIVEN** un ADMIN en `/catalogo-procesos`
- **WHEN** crea la categoría "Ejecutivo" para `ORDINARIA_LABORAL`
- **THEN** queda disponible en el catálogo y aparece en la navegación de esa jurisdicción
- **AND** un usuario no-ADMIN recibe 403 si intenta crear/editar/borrar
