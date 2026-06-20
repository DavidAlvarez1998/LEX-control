# admin-facturacion-suscripciones

Capability de PLATAFORMA: facturar a cada despacho (`Empresa`) su suscripción al `Plan`, de forma
recurrente por periodo, con cobro y corte por impago. Gestionada por ADMIN. Independiente de la
facturación tenant-scoped del portal cliente.

## ADDED Requirements

### Requirement: Generación recurrente idempotente por periodo
La plataforma SHALL poder generar, para un periodo `YYYY-MM`, una factura por cada suscripción
`ACTIVA`, sin duplicar (única por `(suscripcionId, periodo)`). El valor SHALL ser el
`Plan.precioMensual` de la suscripción al momento de generar.

#### Scenario: Generar el periodo
- **GIVEN** 3 suscripciones ACTIVA y 1 CANCELADA
- **WHEN** un ADMIN genera la facturación del periodo `2026-07`
- **THEN** se crean 3 `FacturaSuscripcion` (una por activa) con `valor = Plan.precioMensual`, estado PENDIENTE y fecha de vencimiento
- **AND** la suscripción CANCELADA no genera factura

#### Scenario: Re-generar no duplica
- **GIVEN** ya existen facturas del periodo `2026-07`
- **WHEN** el ADMIN vuelve a generar ese periodo
- **THEN** no se crean duplicados (idempotente por `suscripcionId+periodo`)
- **AND** la respuesta informa cuántas se crearon y cuántas ya existían

### Requirement: Estado de pago y vencimiento derivados
El estado de cobro de una `FacturaSuscripcion` SHALL reflejar PAGADA, VENCIDA (PENDIENTE + vencida)
o PENDIENTE, de forma derivada de fechas/pagos, sin requerir un job que mueva estados.

#### Scenario: Vencida derivada
- **GIVEN** una factura PENDIENTE con `fechaVencimiento` en el pasado y sin pago
- **WHEN** se lista
- **THEN** aparece como VENCIDA con semáforo rojo

### Requirement: Registro de pago idempotente
Un ADMIN SHALL poder registrar el pago de una factura de suscripción; un reintento con el mismo
comprobante NO SHALL duplicar el pago (mismo criterio que el pago del portal cliente).

#### Scenario: Pago marca la factura
- **GIVEN** una factura PENDIENTE
- **WHEN** el ADMIN registra su pago
- **THEN** la factura pasa a PAGADA con `fechaPago` y `metodoPago`
- **AND** reintentar con el mismo `numeroComprobante` no crea un segundo pago

### Requirement: Corte de servicio por impago
La plataforma SHALL poder suspender el servicio de un despacho con facturas de suscripción vencidas,
reusando el bloqueo existente (`Empresa.activo=false` corta el login de todos sus usuarios).

#### Scenario: Suspender por mora
- **GIVEN** un despacho con una factura de suscripción vencida hace mucho
- **WHEN** la plataforma lo suspende
- **THEN** `Empresa.activo=false` y sus usuarios no pueden iniciar sesión
- **AND** al pagar y reactivar, el acceso se restablece

### Requirement: Vista admin de facturación de plataforma
La pantalla `/facturacion` del admin SHALL mostrar el estado de cobro de las suscripciones: KPIs
(facturado del mes, pendiente, vencido, MRR, morosos), la acción de generar el periodo, y la lista
de facturas con filtros y semáforo. Reemplaza el placeholder actual.

#### Scenario: Tablero de cobros
- **GIVEN** un ADMIN en `/facturacion`
- **THEN** ve los KPIs, el botón "Generar facturación del periodo" y la tabla (despacho, plan, periodo, valor, vence, estado)
- **AND** puede filtrar por periodo, estado y despacho

#### Scenario: Aislamiento del tenant
- **GIVEN** la facturación de plataforma (cross-tenant)
- **THEN** usa el modelo `FacturaSuscripcion`, separado de la `Factura` tenant-scoped del portal cliente
- **AND** los despachos NO ven ni gestionan estas facturas (solo ADMIN de plataforma)
