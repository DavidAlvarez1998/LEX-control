# client-modulos-conectados

Capability presentacional: conectar (surfacear) en el portal cliente las relaciones cruzadas que ya
existen en datos, de modo que Cliente y Proceso funcionen como vistas 360 y el dinero sea visible
desde donde se trabaja. Reusa endpoints existentes (o GET filtrados leves); sin cambios de schema.

## ADDED Requirements

### Requirement: Proceso 360 — vista financiera del caso
La ficha de un proceso (`procesos/[id]`) SHALL mostrar la información económica ya ligada al proceso
(ingresos, cartera, facturas y el contrato comercial de origen), de forma que el responsable
jurídico vea el estado de cobro de su caso sin salir de la ficha.

#### Scenario: El abogado ve el dinero de su caso
- **GIVEN** un proceso con `Ingreso`/`Cartera`/`Factura` que llevan su `procesoId`
- **WHEN** el usuario abre la ficha del proceso y entra a la pestaña "Financiero"
- **THEN** ve la lista de ingresos del proceso, su cartera (saldo/estado) y sus facturas
- **AND** ve el contrato comercial / términos de cobro de origen (vía la solicitud de asignación o el contrato vinculado)

#### Scenario: Proceso sin movimientos económicos
- **GIVEN** un proceso sin ingresos/facturas/cartera asociados
- **WHEN** abre la pestaña "Financiero"
- **THEN** ve un estado vacío claro (no un error), invitando a registrar cobro donde corresponda

### Requirement: Cliente 360 — facturas en la ficha del cliente
La ficha del cliente SHALL incluir sus facturas y un resumen de ingresos, completando el hub que ya
muestra procesos, cotizaciones, contrato, cartera y comisiones.

#### Scenario: Facturas del cliente
- **GIVEN** un cliente con facturas emitidas
- **WHEN** se abre su ficha
- **THEN** una sección "Facturas" lista sus facturas con estado y saldo
- **AND** el conjunto cliente/cartera/facturas/comisiones es coherente (mismos totales)

### Requirement: Facturación muestra su origen
El detalle de una factura SHALL mostrar (solo lectura) el contrato comercial y el plan de cobro
(`ConfiguracionCobro`) que la originan, cuando existan, sin alterar el flujo de emisión/pago.

#### Scenario: Trazabilidad de una factura
- **GIVEN** una factura con `contratoId` y `configuracionCobroId`
- **WHEN** se abre su detalle
- **THEN** se muestra el contrato comercial y el plan de cobro de origen
- **AND** los pagos siguen apareciendo como `Ingreso` vinculados (`facturaId`), sin cambios

### Requirement: Desambiguación de "Contratos" en la UI
La interfaz SHALL distinguir claramente los dos conceptos de "contrato": el **contrato del cliente**
(comercial) y el **contrato del personal** (RRHH), para evitar confusión. No cambia el modelo de datos.

#### Scenario: Etiquetas claras
- **GIVEN** el bloque comercial en la ficha del cliente y la pantalla `/contratos` (RRHH)
- **THEN** el primero se rotula como contrato del cliente y el segundo como contrato del personal
- **AND** ningún usuario confunde uno con otro por el nombre

### Requirement: Comisiones trazables a su contrato
La vista de comisiones (`ComisionDespacho`) SHALL mostrar el contrato comercial asociado cuando
`contratoId` esté presente.

#### Scenario: Origen de una comisión
- **GIVEN** una `ComisionDespacho` con `contratoId`
- **WHEN** se lista en la ficha del cliente o el hub comercial
- **THEN** se muestra de qué contrato comercial proviene
