# Empresa Roles & Permissions Specification

> New capability introduced by change `foundations-roles-plans-clientes`. Adds a second, orthogonal authorization axis inside a despacho — `RolEmpresa` (closed enum), seeded `Modulo`/`Permiso`/`RolEmpresaPermiso` catalogs, per-user `UsuarioRolEmpresa` assignments, and the `requirePermiso` (module + RBAC) and seat-gate enforcement. The existing axis (`Usuario.rol`, `esAdminEmpresa`, JWT, tokenVersion) is unchanged.

## ADDED Requirements

### Requirement: Canonical company roles as a closed enum
The system MUST define `RolEmpresa` as a closed enum with exactly four members: `ADMINISTRADOR`, `JURIDICO`, `CONTABLE`, `COMERCIAL`. These four are the seat slots that plans quote (`planes-entitlements`) and the join key for the default RBAC matrix. The existing `Usuario.rol` (`ADMIN` | `USUARIO`) and `esAdminEmpresa` flag MUST remain unchanged and orthogonal.

#### Scenario: The four roles exist and are stable
- GIVEN a freshly migrated database
- WHEN the schema is inspected
- THEN `RolEmpresa` has exactly the members `ADMINISTRADOR`, `JURIDICO`, `CONTABLE`, `COMERCIAL`
- AND `Usuario.rol` and `Usuario.esAdminEmpresa` are unchanged

#### Scenario: Roles are orthogonal to the platform role
- GIVEN a `USUARIO` whose `esAdminEmpresa` is true
- WHEN they are assigned `RolEmpresa.JURIDICO`
- THEN they hold both the platform-level `USUARIO` role and the company-level `JURIDICO` role independently

### Requirement: Seeded Modulo catalog with baseline flag
The system MUST store feature módulos in a seeded `modulos` table (not an enum), each with a unique `clave`, `nombre`, optional `descripcion`, a boolean `esBaseline`, `activo`, and `orden`. The baseline módulos (`judicial`, `extrajudicial`, `reportes`, `calendario`, `notificaciones`, `export_excel`) MUST be seeded with `esBaseline = true` and are treated as always-on in code; non-baseline módulos (`contable`, `comercial`, `contratos`, `ia_redaccion`, `logo_personalizado`, `automatizacion_contratos`) MUST be seeded with `esBaseline = false`. The last three are the former "plan flags" — modeled as módulos so there is one source of truth (B3). Baseline módulos MUST NOT be seeded as explicit `PlanModulo` rows (single source of truth via `esBaseline`).

#### Scenario: Baseline módulos seeded
- GIVEN the seed has run
- WHEN the `modulos` table is read
- THEN `judicial`, `extrajudicial`, `reportes`, `calendario`, `notificaciones`, `export_excel` exist with `esBaseline = true`
- AND `contable`, `comercial`, `contratos`, `ia_redaccion`, `logo_personalizado` exist with `esBaseline = false`

#### Scenario: Clave is unique
- GIVEN the `modulos` table already has `contable`
- WHEN a second `contable` row is inserted
- THEN the unique constraint on `clave` rejects it

### Requirement: Seeded Permiso catalog namespaced under a Modulo
The system MUST store permissions in a seeded `permisos` table, each with a unique `clave` (dotted, e.g. `comercial.prospecto.crear`, `judicial.tramite.asignar`, `contable.factura.ver`), a required `moduloId` FK→`Modulo` (Cascade), `nombre`, and optional `descripcion`, indexed by `moduloId`. Namespacing each permiso under its módulo MUST let the module gate short-circuit every permiso of a disabled módulo at once.

#### Scenario: Permiso belongs to a módulo
- GIVEN the seeded permiso `comercial.prospecto.crear`
- WHEN its `moduloId` is resolved
- THEN it points at the `comercial` módulo

#### Scenario: Deleting a módulo cascades its permisos
- GIVEN a módulo with seeded permisos
- WHEN the módulo row is deleted
- THEN its `permisos` rows are deleted via Cascade

### Requirement: Default RBAC matrix
The system MUST store the default role→permiso grants in a seeded `rol_empresa_permisos` table keyed by `@@id([rolEmpresa, permisoId])`, where `rolEmpresa` is a `RolEmpresa` value and `permisoId` is an FK→`Permiso` (Cascade). This matrix MUST express which canonical role gets which permiso by default.

#### Scenario: Matrix grants resolve
- GIVEN the seeded RBAC matrix grants `comercial.prospecto.crear` to `COMERCIAL`
- WHEN the grants for `COMERCIAL` are read
- THEN `comercial.prospecto.crear` is present

#### Scenario: Composite key prevents duplicate grants
- GIVEN `(COMERCIAL, comercial.prospecto.crear)` already exists
- WHEN the same pair is inserted again
- THEN the composite primary key rejects it

### Requirement: Per-user role assignment is the seat unit
The system MUST assign company roles to users via `usuario_roles_empresa`: `id` (cuid), `usuarioId` FK→`Usuario` (Cascade), `rolEmpresa`, `empresaId` FK→`Empresa` (Cascade, denormalized for O(1) seat counting and tenant scope), optional `asignadoPorId` FK→`Usuario` (SetNull), and `createdAt`. It MUST enforce `@@unique([usuarioId, rolEmpresa])` (a user may hold several roles but not the same twice) and index `@@index([empresaId, rolEmpresa])`. The two Cascade FKs (`Usuario`, `Empresa`) MUST NOT create a multiple-cascade path to one table (errno-150 safe).

#### Scenario: A user holds multiple distinct roles
- GIVEN a user already assigned `JURIDICO`
- WHEN they are assigned `COMERCIAL`
- THEN both assignments exist for that user

#### Scenario: A user cannot hold the same role twice
- GIVEN a user already assigned `JURIDICO`
- WHEN `JURIDICO` is assigned to them again
- THEN the `@@unique([usuarioId, rolEmpresa])` constraint rejects it

#### Scenario: Empresa cascade removes assignments
- GIVEN an empresa with role assignments
- WHEN the empresa is deleted
- THEN its `usuario_roles_empresa` rows are removed via Cascade

### Requirement: requireAuth resolves company roles per request
`requireAuth` MUST, after validating the JWT and resolving `empresaId`/`esAdminEmpresa` as today, also resolve the caller's `RolEmpresa[]` from `usuario_roles_empresa` into `req.rolesEmpresa` (same per-request DB-resolution philosophy as the existing empresaId/esAdminEmpresa resolution). The existing JWT shape, `tokenVersion` check, and `requireRole`/`requireEmpresaAdmin` behavior MUST be unchanged.

#### Scenario: Roles attached to the request
- GIVEN an authenticated user assigned `JURIDICO` and `COMERCIAL`
- WHEN a request passes `requireAuth`
- THEN `req.rolesEmpresa` contains `JURIDICO` and `COMERCIAL`

#### Scenario: User with no company roles
- GIVEN an authenticated user with zero `usuario_roles_empresa` rows
- WHEN a request passes `requireAuth`
- THEN `req.rolesEmpresa` is an empty array AND the request is NOT rejected by `requireAuth` itself

### Requirement: requirePermiso enforces a module gate then an RBAC gate
The system MUST provide `requirePermiso(clave)` middleware that runs AFTER `requireAuth`. It MUST (1) MODULE GATE: resolve the permiso's `moduloId` and verify that módulo's `clave` is in `resolveEntitlements(empresaId).modulosHabilitados`, returning 403 `Módulo no contratado` otherwise; then (2) RBAC GATE: verify the caller holds some `RolEmpresa` that grants `clave` in `rol_empresa_permisos`, returning 403 otherwise. `esAdminEmpresa` MUST short-circuit the RBAC gate ONLY — it MUST still pass the module gate (a company superadmin cannot use an uncontracted módulo).

#### Scenario: Module not contracted
- GIVEN a user whose empresa has not contracted the `contable` módulo
- WHEN they call an endpoint guarded by `requirePermiso('contable.factura.ver')`
- THEN the response status is 403 with message `Módulo no contratado`

#### Scenario: Module contracted but role lacks the permiso
- GIVEN a user in an empresa that contracted `comercial`, holding only `JURIDICO` (not granted `comercial.prospecto.crear`), with `esAdminEmpresa = false`
- WHEN they call an endpoint guarded by `requirePermiso('comercial.prospecto.crear')`
- THEN the response status is 403

#### Scenario: Permiso granted by role
- GIVEN a user holding `COMERCIAL` (granted `comercial.prospecto.crear`) in an empresa that contracted `comercial`
- WHEN they call an endpoint guarded by `requirePermiso('comercial.prospecto.crear')`
- THEN the request proceeds

#### Scenario: esAdminEmpresa short-circuits RBAC only
- GIVEN a user with `esAdminEmpresa = true` whose empresa contracted `comercial` but who holds no role granting `comercial.prospecto.crear`
- WHEN they call an endpoint guarded by `requirePermiso('comercial.prospecto.crear')`
- THEN the request proceeds (RBAC short-circuited)

#### Scenario: esAdminEmpresa cannot bypass the module gate
- GIVEN a user with `esAdminEmpresa = true` whose empresa has NOT contracted `contable`
- WHEN they call an endpoint guarded by `requirePermiso('contable.factura.ver')`
- THEN the response status is 403 `Módulo no contratado`

### Requirement: Transactional seat gate at role assignment
When assigning a `RolEmpresa R` to a user, the system MUST, inside a row-locking transaction that locks a STABLE parent row (`SELECT ... FOR UPDATE` on the empresa's `Suscripcion` row — NOT the `usuario_roles_empresa` rows, which may be empty for the first holder of a role and would lock nothing), COUNT existing assignments for `(empresaId, rolEmpresa = R)` **joined to `Usuario` and filtered to `Usuario.activo = true`**, and reject the assignment if that count is not strictly less than `resolveEntitlements(empresaId).cuotas[R]`. A `NULL` cap (ilimitado) MUST always be allowed. DECISION Q3: a seat is freed both by removing the role row AND by deactivating the user (`activo = false`) — only ACTIVE holders count against the cap. On assigning `ADMINISTRADOR`, the system MUST keep `esAdminEmpresa` in sync (mirror), with `esAdminEmpresa` remaining AUTHORITATIVE for team management.

#### Scenario: Seat available
- GIVEN an empresa whose `JURIDICO` cap is 2 with 1 assignment used
- WHEN a second user is assigned `JURIDICO`
- THEN the assignment succeeds

#### Scenario: Seat cap exceeded
- GIVEN an empresa whose `JURIDICO` cap is 2 with 2 assignments used
- WHEN a third user is assigned `JURIDICO`
- THEN the assignment is rejected

#### Scenario: Unlimited cap always allows
- GIVEN an empresa whose `JURIDICO` cap is NULL (ilimitado)
- WHEN any number of users are assigned `JURIDICO`
- THEN every assignment succeeds

#### Scenario: Concurrent assignments do not both pass
- GIVEN an empresa with exactly one `CONTABLE` seat remaining
- WHEN two assignment requests for `CONTABLE` run concurrently
- THEN the row lock serializes them so exactly one succeeds and the other is rejected

#### Scenario: Deactivation frees a seat (DECISION Q3)
- GIVEN a user assigned `JURIDICO` against the last available seat
- WHEN the user is deactivated (`activo = false`)
- THEN the seat is freed (only active holders count) AND a new `JURIDICO` assignment now succeeds
- AND reactivating the original user re-consumes a seat (rejected if the cap is now full)

#### Scenario: ADMINISTRADOR mirrors esAdminEmpresa
- GIVEN a user being assigned `ADMINISTRADOR`
- WHEN the assignment is created
- THEN `esAdminEmpresa` is kept in sync, and `requireEmpresaAdmin` continues to use `esAdminEmpresa` as authoritative
