# Proposal: Nómina prellenada desde Contrato (HR)

## Intent
Hoy crear una `Nomina` exige teclear `nombreEmpleado`, `cargo`, `tipoVinculacion`,
`salarioHonorarios` y `fechaIngreso` a mano, aunque esos datos ya viven en el módulo de
**Contratos (HR)** de la misma persona. Este change conecta ambos: al crear una nómina el contable
puede **elegir un colaborador con contrato** y el formulario se **prellena** desde su contrato. La
nómina sigue siendo una hoja autocontenida con snapshot congelado — el contrato es solo la **fuente
de prellenado al crear**, no un join vivo.

## Por qué es coherente con el diseño (validación SDD)
El vínculo estaba anticipado por ambos lados:
- La capability `contable-nomina` declara que **deliberadamente NO hay entidad `Empleado`** porque
  *"the future HR módulo owns that"* y que `empleadoId` *"MAY point at `Usuario.id` today, future
  `Empleado.id` later"*. Ese módulo HR es **Contratos**.
- El schema de `Contrato` rotula su bloque económico: *"C. Información económica (luego conecta con
  el módulo Contable)"*.

Decisivo para SDD: este change **NO modifica** ningún requisito existente de Nómina (snapshot,
frozen COP, `empleadoId` sin FK, validación same-empresa). Solo **AÑADE** una fuente de prellenado y
un endpoint de lectura mínimo. El requisito *"Snapshot survives deactivation"* se respeta porque se
**copian valores**, no se referencia el contrato.

## Alcance único: solo Nómina
Auditadas las 8 hojas de Contable contra el `Contrato` HR, **la única relación de campo real es
Nómina**. Egresos / Servicios fijos / Caja menor / Ingresos / Cuentas / Cartera **no** tienen
vínculo de campo con el contrato HR (cartera/ingresos cuelgan de `ContratoComercial`, que es
despacho↔cliente — otro eje). No se tocan.

## Mapeo de prellenado (parcial y honesto)
| Campo Nómina | Origen Contrato | Regla |
|---|---|---|
| `empleadoId` | `usuarioId` | directo; `null` si el contrato es login-less |
| `nombreEmpleado` | `nombreCompleto` | directo (snapshot) |
| `cargo` | `cargo` | directo |
| `fechaIngreso` | `fechaInicio` | directo |
| `salarioHonorarios` | `honorarios` | directo |
| `tipoVinculacion` (enum) | `tipoContrato` (texto libre) | mapeo best-effort: "Laboral"→`LABORAL`, "Prestación de servicios"→`PRESTACION_SERVICIOS`, resto→`OTRO` |
| `bonificaciones` (Decimal) | — | **NO se prellena**: en contrato es texto descriptivo, no un monto |
| `descuentos` (Decimal) | — | **NO se prellena**: idem |
| `cuentaId` (bolsa pagadora) | — | **NO se prellena**: `Contrato.cuentaBancaria` es la cuenta del empleado (texto), no la bolsa pagadora del despacho |

El prellenado es siempre **editable** antes de guardar (un mes puede tener bonos/descuentos
distintos a lo pactado).

## Scope técnico
- **Schema**: **sin cambios** (Nómina ya tiene todos los campos; `empleadoId` ya existe).
- **API** (módulo `contable`, reusa permisos `contable.nomina.ver/.crear/.editar`):
  - `GET /contable/nominas/empleables` — lista mínima de colaboradores con contrato del despacho del
    token, para alimentar el selector y el prellenado. Devuelve **solo** lo necesario:
    `{ contratoId, usuarioId, nombre, cargo, honorarios, tipoContrato, fechaInicio, estado }`. NO
    expone el contrato completo (cláusulas, documentos, datos legales). Gated por `contable.nomina.crear`.
  - `POST/PATCH /contable/nominas` ahora **valida `empleadoId` same-empresa** (era un requisito de la
    spec de nómina sin implementar; se activa porque el front ya envía `empleadoId` al prellenar).
- **Frontend** (cliente): en el form de Nómina, un selector "Elegir de contratos ▾" que prellena los
  5 campos limpios + mapea `tipoVinculacion`; el campo "Empleado" sigue aceptando **nombre libre**
  como fallback (personas sin contrato registrado).

## Refinamientos de la vida real (aplicados)
Aterrizado en cómo opera una nómina en Colombia, con tres ajustes sobre las decisiones iniciales:
- **El contrato es la fuente de verdad; el nombre libre es la excepción señalada.** El salario de la
  nómina debe coincidir con el del contrato (hallazgo de revisoría si no). El selector encabeza el
  form; la opción "Otro — sin contrato registrado" queda marcada como **excepción** (aviso ámbar).
- **No se restringe a `ACTIVO`.** Un contrato `FINALIZADO`/`SUSPENDIDO` aún recibe **liquidación**
  (cesantías, vacaciones, indemnización). Por defecto se ven vigentes; un check "incluir finalizados
  (liquidación)" revela el resto.
- **`LABORAL` ≠ `PRESTACION_SERVICIOS`** importa (prestaciones, seguridad social, retención): el mapeo
  del enum lo preserva con fallback `OTRO`.

> **Caveat de alcance (vida real):** hoy `Nomina` es un *registro de pagos*
> (`salario + auxilio + bonif − descuentos = neto`), **no un liquidador**: no calcula seguridad
> social, parafiscales, prestaciones ni retención (PILA). Suficiente para que un despacho lleve registro
> de lo que paga; el cumplimiento pleno sería un módulo aparte. La **generación recurrente por periodo**
> (donde realmente vive la nómina) queda para **Fase 2** — este change es su cimiento.

## Decisiones
- **Selector + nombre libre (fallback)** — no se obliga a tener contrato; no rompe el flujo actual.
- **Endpoint mínimo `empleables`** — superficie RBAC mínima; CONTABLE NO recibe `contrato.ver`, no ve
  el contrato completo. Cero re-seed (reusa `contable.nomina.*`).
- **Prefill parcial** — solo los 5 campos compatibles + el mapeo de enum; bonif/descuentos/cuenta se
  dejan al contable por incompatibilidad de tipo/concepto.
- **Snapshot intacto** — al guardar se copian valores; si el contrato cambia o la persona se
  desactiva luego, la nómina ya emitida no se altera.

## Out of scope
- **Generación recurrente** de nómina por periodo (usar `diaPago`/`formaPago` del contrato, estilo
  `servicios-fijos-recurrentes`) → Fase 2, change aparte.
- Pagar colaboradores "por caso" como **Egreso** en vez de Nómina (decisión de flujo, no de campo).
- Cualquier cambio a las otras 7 hojas de Contable.

## Rollback
Aditivo y sin schema: revertir = quitar el endpoint `empleables` y el selector del form. Las nóminas
ya creadas son snapshots independientes, no quedan referencias colgando.
