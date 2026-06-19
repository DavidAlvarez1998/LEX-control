# Tramite Catalog Specification (delta)

## ADDED Requirements

### Requirement: Editar un tipo conserva sus reglas avanzadas
Al actualizar un `TipoProceso` desde el admin, el sistema MUST **preservar** las propiedades
avanzadas que el formulario del catálogo no edita, fusionándolas sobre un snapshot del tipo
original. El form SHALL editar solo metadata básica (nombre, descripción, jurisdicción,
áreas, `esJudicial`) y la estructura simple de campos/etapas (label, orden, `camposRequeridos`,
`plazoDias`); todo lo demás se conserva tal cual.

#### Scenario: Editar metadata no borra lo avanzado
- **GIVEN** un `TipoProceso` con campos que tienen `mostrarSi`/`requeridoSi`/`soloFicha` y
  etapas con `documentosRequeridos`/`requeridosSi`/`opcionalesSi`/plazos/ramas/`disponibleSi`
- **WHEN** un admin edita su nombre o descripción y guarda
- **THEN** `esquemaFormulario` y `etapas` conservan todas esas propiedades avanzadas
  (solo cambia lo editado), vía merge sobre el original

#### Scenario: Aviso al editar un tipo avanzado
- **GIVEN** un tipo cuyo esquema o etapas usan reglas avanzadas
- **WHEN** se abre su edición en el admin
- **THEN** se muestra un aviso de que esas reglas se **conservan** y que para cambiarlas se
  edita el catálogo semilla

#### Scenario: Eliminar una fila sí la quita
- **GIVEN** la edición de un tipo en el admin
- **WHEN** se elimina una fila de campo o de etapa y se guarda
- **THEN** ese campo/etapa se elimina del tipo (el merge no preserva lo removido), hasta
  que un reseed lo restaure

### Requirement: El seed es la fuente de verdad de los tipos curados
`prisma/seed-tipos.json` MUST ser la fuente de verdad de los tipos **curados** (verbal,
verbal sumario, laboral, Derecho de Petición, tutela). `pnpm seed:catalogo` MUST aplicar el
JSON por **upsert**, sobrescribiendo `esquemaFormulario` y `etapas` en BD. Las ediciones del
admin a esos tipos SHALL considerarse transitorias (viven solo en BD) y serán revertidas por
el próximo `seed:catalogo`.

#### Scenario: Reseed sobrescribe ediciones del admin a un tipo curado
- **GIVEN** un tipo curado editado desde el admin (cambios solo en BD)
- **WHEN** se corre `pnpm seed:catalogo`
- **THEN** el `esquemaFormulario`/`etapas` del tipo vuelve a lo definido en `seed-tipos.json`

#### Scenario: El upsert no borra los procesos existentes
- **GIVEN** procesos ya creados de un tipo curado
- **WHEN** se corre `pnpm seed:catalogo`
- **THEN** solo se actualiza la definición del `TipoProceso`; los procesos existentes se conservan

#### Scenario: Cambios de fondo van al seed
- **GIVEN** que se quiere cambiar el flujo de un tipo curado (campos, etapas, documentos, reglas)
- **THEN** el cambio se hace en `seed-tipos.json` y se aplica con `seed:catalogo` (no en el admin)
