# Contable — Nómina · delta (prefill desde Contrato HR)

> Change `contable-nomina-desde-contrato`. Extends the existing `contable-nomina` capability with a
> minimal read endpoint that surfaces the firm's staff-with-contract, and a create-time prefill
> source. It does NOT modify any existing Nomina requirement: the row stays a self-contained,
> snapshot, frozen-COP leaf with a no-FK scalar `empleadoId`.

## ADDED Requirements

### Requirement: empleables endpoint exposes minimal staff-with-contract for nómina prefill
The system MUST provide `GET /contable/nominas/empleables` returning the minimal projection of the
firm's HR `Contrato` rows needed to prefill a `Nomina`: each item MUST contain ONLY
`{ contratoId, usuarioId (nullable), nombre, cargo, honorarios, tipoContrato, fechaInicio, estado }`.
It MUST hard-filter by the token `empresaId` (`WHERE { empresaId }`), MUST be gated by `requireAuth` +
`requirePermiso('contable.nomina.crear')`, and the `contable` módulo gate applies. It MUST NOT expose
the full `Contrato` (no `clausulas`, `penalidades`, `documentos`, `numeroDocumento`, etc.). It MUST
NOT require granting `contrato.ver` to the CONTABLE role. It MUST return ALL contracts regardless of
`estado` (and include `estado` in the projection) so the UI can default to vigentes (`ACTIVO`) yet
still surface terminated/suspended contracts when a liquidación must be paid; the filtering by estado
is a UI concern, not an API restriction.

#### Scenario: Contable lists employables without seeing full contracts
- GIVEN a user holding `contable.nomina.crear` in despacho A (no `contrato.ver`)
- WHEN they GET `/contable/nominas/empleables`
- THEN they receive despacho A's staff with only `{contratoId, usuarioId, nombre, cargo, honorarios, tipoContrato, fechaInicio, estado}`
- AND no clause / document / legal field of any contrato is included (the Prisma `select` never names them)

#### Scenario: Scoped by token empresaId
- GIVEN despacho A has contratos and despacho B has contratos
- WHEN a user of despacho A calls the endpoint
- THEN only despacho A's contratos are returned (hard `WHERE { empresaId }`)

#### Scenario: Login-less staff are employable
- GIVEN a despacho-A contrato whose `usuarioId` is null (messenger with no login)
- WHEN the endpoint is called
- THEN that person appears with `usuarioId = null` and a non-empty `nombre`

#### Scenario: Terminated contract still payable for liquidación
- GIVEN a despacho-A contrato with `estado = FINALIZADO`
- WHEN the endpoint is called
- THEN it is included in the response with `estado = FINALIZADO`
- AND the UI hides it by default but reveals it under "incluir finalizados (liquidación)"

### Requirement: empleadoId is enforced same-empresa firm staff on write
On `POST`/`PATCH /contable/nominas`, when `empleadoId` is set the system MUST verify it references a
`Usuario` of the same `empresaId` (token) before writing; otherwise it MUST reject with `400`. A
platform `ADMIN` (`empresaId = null`) never matches and cannot be a payroll subject. This implements
the existing (previously unenforced) `contable-nomina` requirement, now active because the client
sends `empleadoId` when a nómina is prefilled from a contrato.

#### Scenario: empleadoId of another empresa rejected on create
- GIVEN a user of despacho A creating a `Nomina` with `empleadoId` of a despacho-B user
- WHEN the POST is processed
- THEN it is rejected `400` and no `nomina.create` runs

#### Scenario: Valid same-empresa empleadoId accepted
- GIVEN a user of despacho A creating a `Nomina` with `empleadoId` of a despacho-A user
- WHEN the POST is processed
- THEN the row is created with `empresaId` from the token and the given `empleadoId`

### Requirement: Creating a nómina MAY prefill from a Contrato, copying values (not referencing)
When a `Nomina` is created from a selected contrato, the client MUST prefill ONLY these fields by
**copying** the contrato's values at create time: `empleadoId` ← `Contrato.usuarioId`,
`nombreEmpleado` ← `Contrato.nombreCompleto`, `cargo` ← `Contrato.cargo`, `fechaIngreso` ←
`Contrato.fechaInicio`, `salarioHonorarios` ← `Contrato.honorarios`, and `tipoVinculacion` mapped
from the free-text `Contrato.tipoContrato`. The system MUST NOT prefill `bonificaciones`,
`descuentos` or `cuentaId` from the contrato (type/concept mismatch). All prefilled values MUST
remain editable before submit. The created `Nomina` MUST hold no live reference to the contrato (the
existing snapshot/no-FK requirements are unchanged); a later change to the contrato or deactivation of
the person MUST NOT alter an already-created `Nomina`.

#### Scenario: Prefill the five clean fields
- GIVEN a contrato `{nombreCompleto:"Ana Ruiz", cargo:"Abogada", tipoContrato:"Laboral", fechaInicio:2025-02-01, honorarios:4.500.000, usuarioId:"u1"}`
- WHEN the contable picks it in the nómina form
- THEN the form shows `empleadoId=u1`, `nombreEmpleado="Ana Ruiz"`, `cargo="Abogada"`, `tipoVinculacion=LABORAL`, `fechaIngreso=2025-02-01`, `salarioHonorarios=4.500.000`
- AND `bonificaciones`, `descuentos`, `cuentaId` stay empty for manual entry

#### Scenario: tipoContrato maps to the closed enum with OTRO fallback
- GIVEN a contrato with `tipoContrato = "Prestación de servicios"`
- WHEN it prefills the nómina
- THEN `tipoVinculacion = PRESTACION_SERVICIOS`
- AND a contrato with `tipoContrato = "Freelance"` (or any unrecognized value) maps to `OTRO`

#### Scenario: Free-text name still works without a contrato (fallback)
- GIVEN a person with no registered contrato
- WHEN the contable types `nombreEmpleado` directly (no selection)
- THEN the nómina is created normally with `empleadoId = null` (existing behavior preserved)

#### Scenario: Snapshot is independent of the source contrato
- GIVEN a `Nomina` created by prefill from a contrato
- WHEN the contrato's `honorarios` is later changed or the person is deactivated
- THEN the existing `Nomina.salarioHonorarios` / `nombreEmpleado` are unchanged (values were copied, not referenced)
