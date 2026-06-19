# Admin Prospectos Specification (delta)

## ADDED Requirements

### Requirement: Prospectos sin asignar — bandeja y auto-toma
Un `Prospecto` con `comercialId = null` MUST ser visible como **"sin asignar"** y poder asignarse
de dos formas: (a) el **admin** lo asigna a **cualquier** usuario con rol COMERCIAL; (b) un usuario
con rol **COMERCIAL** lo **toma** para sí (auto-asignación). Tomar un prospecto que YA tiene
comercial MUST rechazarse.

#### Scenario: Filtrar los sin asignar
- **GIVEN** prospectos con y sin comercial
- **WHEN** se listan con el filtro "sin asignar"
- **THEN** se devuelven solo los de `comercialId = null`
- **AND** tanto el admin como los comerciales pueden ver esa bandeja

#### Scenario: Un comercial toma un prospecto sin dueño
- **GIVEN** un prospecto con `comercialId = null`
- **WHEN** un usuario COMERCIAL ejecuta "tomar"
- **THEN** el prospecto queda con `comercialId = ese usuario`

#### Scenario: No se puede tomar uno ya asignado
- **GIVEN** un prospecto con `comercialId` ya seteado
- **WHEN** otro comercial intenta "tomar"
- **THEN** se rechaza con 409 (ya tiene dueño)

#### Scenario: El admin asigna a cualquier comercial
- **GIVEN** un prospecto sin asignar
- **WHEN** el admin lo asigna a un usuario con rol COMERCIAL
- **THEN** el prospecto queda con ese `comercialId` (se valida que el destino sea COMERCIAL)

#### Scenario: Origen landing visible
- **GIVEN** un prospecto creado desde el contacto de la landing (`canalEntrada = WEB`)
- **WHEN** se ve en la lista del admin
- **THEN** su canal (WEB / contacto landing) es distinguible para priorizarlo
