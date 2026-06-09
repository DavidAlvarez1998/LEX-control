# Plans & Entitlements Specification

> New capability introduced by change `foundations-roles-plans-clientes`. Adds a packaging layer ABOVE `Servicio`/`EmpresaServicio` (complementary, never gating billing): a `Plan` catalog, a per-empresa `Suscripcion` with módulo/seat overrides, and the `resolveEntitlements(empresaId)` engine that the module gate and seat gate of `empresa-roles` consume. Mirrors the codebase's catalog-default + per-empresa-override idiom.

## ADDED Requirements

### Requirement: Plan catalog created by ADMIN
The system MUST store platform plans in `planes`: `id` (cuid), unique `clave` (`independiente`, `independiente_pro`, `firma`, `bufete`, `bufete_pro`), `nombre`, optional `descripcion`, `precioMensual` Decimal(10,2) **stored as a frozen COP amount for every plan** (DECISION Q5=B — no SMMLV indexing). `bufete_pro` stores the current COP value of 1 SMMLV (e.g. $1.423.500 for 2025) and the platform ADMIN updates it manually when the minimum wage changes; there is NO `precioEnSmmlv` column. `activo`, `orden`, `createdAt`, `updatedAt`. Plans MUST be ADMIN-created, mirroring `Servicio`'s role. A `Plan` MUST NOT be deletable while a `Suscripcion` references it (Restrict).

#### Scenario: Five seeded plans
- GIVEN the seed has run
- WHEN the `planes` table is read
- THEN exactly the claves `independiente`, `independiente_pro`, `firma`, `bufete`, `bufete_pro` exist

#### Scenario: All plan prices are frozen COP amounts
- GIVEN the seeded plans
- WHEN `precioMensual` is inspected
- THEN every plan (including `bufete_pro`) has a non-NULL COP amount and there is no `precioEnSmmlv` column
- AND `bufete_pro.precioMensual` equals the current COP value of 1 SMMLV (manually maintained)

#### Scenario: Plan in use cannot be deleted
- GIVEN a plan referenced by an active `Suscripcion`
- WHEN the plan is deleted
- THEN the Restrict rule rejects the deletion

### Requirement: Plan composition (módulos, cuotas, flags)
A `Plan` MUST compose its entitlements via `plan_modulos` (`planId` Cascade, `moduloId` Restrict, `@@unique([planId, moduloId])`) and `plan_cuotas` (`planId` Cascade, `rolEmpresa`, `limite` Int? where NULL = ilimitado, `@@unique([planId, rolEmpresa])`). DECISION B3: there is NO `plan_flags` table — the feature toggles `logo_personalizado`, `ia_redaccion`, and `automatizacion_contratos` are modeled as **non-baseline `Modulo` rows** and granted via `plan_modulos` like any other módulo (single source of truth; `resolveEntitlements` returns them in `modulosHabilitados`). Baseline módulos MUST NOT be listed as `plan_modulos` rows (they are always-on via `Modulo.esBaseline`). The seeded composition MUST match the price card.

#### Scenario: Independiente composition
- GIVEN the seeded `independiente` plan ($200.000)
- WHEN its composition is read
- THEN non-baseline `plan_modulos` are empty (only baseline judicial/extrajudicial/reportes/export_excel/calendario/notificaciones apply)
- AND `plan_cuotas` = { ADMINISTRADOR: 1, JURIDICO: 1 }

#### Scenario: Independiente PRO composition
- GIVEN the seeded `independiente_pro` plan ($300.000)
- WHEN its composition is read
- THEN `plan_modulos` adds `contable` and `comercial`
- AND `plan_cuotas` = { ADMINISTRADOR: 1, JURIDICO: 2, CONTABLE: 1, COMERCIAL: 1 }

#### Scenario: Firma composition
- GIVEN the seeded `firma` plan ($500.000)
- WHEN its composition is read
- THEN `plan_modulos` adds `contratos` (on top of contable, comercial)
- AND `plan_cuotas` = { ADMINISTRADOR: 1, JURIDICO: 5, CONTABLE: 1, COMERCIAL: 1 }

#### Scenario: Bufete composition
- GIVEN the seeded `bufete` plan ($1.000.000)
- WHEN its composition is read
- THEN `plan_modulos` includes the non-baseline módulo `logo_personalizado`
- AND `plan_cuotas` = { ADMINISTRADOR: 1, JURIDICO: 10, CONTABLE: 1, COMERCIAL: 1 }

#### Scenario: Bufete PRO unlimited seats and flags
- GIVEN the seeded `bufete_pro` plan (priced at the COP value of 1 SMMLV)
- WHEN its composition is read
- THEN `plan_modulos` includes the non-baseline módulos `ia_redaccion`, `automatizacion_contratos`, and `logo_personalizado`
- AND `plan_cuotas` = { ADMINISTRADOR: 2, JURIDICO: NULL, CONTABLE: NULL, COMERCIAL: NULL } (ilimitado)

### Requirement: One current Suscripcion per empresa
The system MUST bind an empresa to one current plan via `suscripciones`: `id` (cuid), `empresaId` FK→`Empresa` (Cascade), `planId` FK→`Plan` (Restrict), `estado` `EstadoSuscripcion` (`ACTIVA` | `TRIAL` | `SUSPENDIDA` | `CANCELADA`), `inicioEn`, optional `finEn`, `createdAt`, `updatedAt`, with `@@unique([empresaId])` and `@@index([empresaId])`. Deleting an empresa MUST cascade its suscripción; a plan MUST NOT be deletable while referenced.

#### Scenario: One plan per empresa enforced
- GIVEN an empresa already with a suscripción
- WHEN a second suscripción is created for the same empresa
- THEN the `@@unique([empresaId])` constraint rejects it

#### Scenario: Empresa cascade removes suscripción
- GIVEN an empresa with a suscripción
- WHEN the empresa is deleted
- THEN its `suscripciones` row is removed via Cascade

### Requirement: Per-empresa módulo and seat overrides
The system MUST support per-empresa overrides that parallel the `EmpresaServicio` negotiated-price pattern: `suscripcion_modulos` (`suscripcionId` Cascade, `moduloId` Restrict, `habilitado` Boolean, `@@unique([suscripcionId, moduloId])`) toggles a single módulo on/off for that empresa; `suscripcion_cuotas` (`suscripcionId` Cascade, `rolEmpresa`, `limite` Int?, `@@unique([suscripcionId, rolEmpresa])`) overrides a single role's seat cap. Overrides MUST take precedence over plan defaults.

#### Scenario: Override enables an extra módulo
- GIVEN an empresa on `independiente` (no `contable`) with a `suscripcion_modulos` row { contable, habilitado: true }
- WHEN entitlements are resolved
- THEN `contable` is in `modulosHabilitados`

#### Scenario: Override raises a seat cap
- GIVEN an empresa on `firma` (JURIDICO cap 5) with a `suscripcion_cuotas` row { JURIDICO, limite: 8 }
- WHEN entitlements are resolved
- THEN the JURIDICO cap is 8

#### Scenario: Override disables a plan módulo
- GIVEN an empresa on `independiente_pro` (has `comercial`) with a `suscripcion_modulos` row { comercial, habilitado: false }
- WHEN entitlements are resolved
- THEN `comercial` is NOT in `modulosHabilitados`

### Requirement: resolveEntitlements engine
The system MUST provide `resolveEntitlements(empresaId)` returning `{ modulosHabilitados: Set<clave>, cuotas: Map<RolEmpresa, number|Infinity> }`, with `empresaId` taken only from the authenticated request (never client input). It MUST start from the empresa's `Suscripcion(estado = ACTIVA)` → its plan's `PlanModulo` + `PlanCuota`, apply `SuscripcionModulo`/`SuscripcionCuota` overrides, and ALWAYS include every `esBaseline` módulo. A `limite` of NULL MUST resolve to Infinity (typed helper). DECISION B3 — non-active suscripción: when the empresa has no `ACTIVA` suscripción (e.g. `SUSPENDIDA`/`CANCELADA`/none), `modulosHabilitados` MUST contain ONLY baseline módulos and EVERY role cap in `cuotas` MUST be 0 (blocks NEW seat assignments; already-active members keep working until reactivation). Correctness MUST re-read the DB (cacheable, but mirrors the existing per-request DB resolution).

#### Scenario: Baseline always included
- GIVEN any empresa with an ACTIVA suscripción on any plan
- WHEN entitlements are resolved
- THEN every `esBaseline` módulo (judicial, extrajudicial, reportes, calendario, notificaciones, export_excel) is in `modulosHabilitados`

#### Scenario: Plan defaults then overrides
- GIVEN an empresa on `firma` with one override raising JURIDICO to 8
- WHEN entitlements are resolved
- THEN módulos come from the plan (plus baseline) and JURIDICO cap is the overridden 8 while the other caps come from the plan

#### Scenario: NULL limite is Infinity
- GIVEN an empresa on `bufete_pro` (JURIDICO cap NULL)
- WHEN entitlements are resolved
- THEN `cuotas[JURIDICO]` is Infinity

#### Scenario: Non-active suscripción grants baseline only with zero caps
- GIVEN an empresa whose only suscripción has estado `SUSPENDIDA`
- WHEN entitlements are resolved
- THEN `modulosHabilitados` contains ONLY baseline módulos (no non-baseline)
- AND every role cap in `cuotas` is 0, so a new seat assignment is rejected while existing active members keep working

### Requirement: Entitlements never gate billing
The `Plan`/`Suscripcion` layer MUST be complementary to `Servicio`/`EmpresaServicio` and MUST NOT alter, gate, or replace the existing negotiated-price billing flow. The existing `Servicio`/`EmpresaServicio` models and endpoints MUST be unchanged.

#### Scenario: Existing billing untouched
- GIVEN the existing `EmpresaServicio` negotiated-price assignments
- WHEN the entitlements layer is added
- THEN `Servicio`/`EmpresaServicio` schema and behavior are unchanged AND entitlements resolution does not read or modify them
