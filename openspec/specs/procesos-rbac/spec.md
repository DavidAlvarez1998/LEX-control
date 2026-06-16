# Procesos — RBAC & COMERCIAL scoping Specification

> New capability introduced by change `comercial-rol-portal`. Closes a security gap: the procesos
> router moved from bare `requireAuth` to concrete `requirePermiso`, and a COMERCIAL (without
> JURIDICO) gets read-only access scoped to their own clients. The stage state machine, dynamic form,
> and vencimiento math are UNCHANGED — this is purely the authorization layer over `/procesos`.

## ADDED Requirements

### Requirement: Procesos endpoints are gated by concrete proceso permisos
Every `/procesos` endpoint MUST be gated by `requireAuth` + a concrete `requirePermiso`: all READS
(`GET /procesos`, `GET /procesos/:id`, `GET /procesos/:id/caso`, `GET /procesos/vencimientos`, etc.)
require `proceso.ver`; all WRITES (`POST /procesos`, `PATCH /procesos/:id`, `PATCH
/procesos/:id/etapa`, `POST /procesos/:id/derivar`, document mutations, etc.) require `proceso.editar`.
`proceso.ver` MUST be granted to `JURIDICO` + `COMERCIAL` + `ADMINISTRADOR`; `proceso.editar` MUST be
granted to `JURIDICO` + `ADMINISTRADOR` ONLY. The judicial módulo stays baseline (gating procesos does
NOT add a módulo-contratado door). No request reaches a proceso handler on `requireAuth` alone.

#### Scenario: Unauthenticated is rejected
- GIVEN no token
- WHEN `GET /procesos` is called
- THEN it is rejected 401

#### Scenario: COMERCIAL reads but cannot write
- GIVEN a user holding only `RolEmpresa.COMERCIAL`
- WHEN they `GET /procesos` (200) and then `POST /procesos` or `PATCH /procesos/:id/etapa`
- THEN the read succeeds and every write is rejected 403 (`proceso.editar` not held)

#### Scenario: JURIDICO reads and writes
- GIVEN a user holding `RolEmpresa.JURIDICO`
- WHEN they read and write procesos
- THEN both are authorized (not 403); writes may still 400 on invalid bodies

### Requirement: A COMERCIAL-only user sees only their own clients' procesos
On `GET /procesos`, a caller who is NOT `esAdminEmpresa`, holds `COMERCIAL`, and does NOT hold
`JURIDICO` MUST have the list hard-restricted to procesos of their own clients: `responsableId =
self` OR `cliente.responsableComercialId = self` (the same criterion as `/clientes?mios`). Any other
authorized caller (JURIDICO, ADMINISTRADOR, or a COMERCIAL who also holds JURIDICO) sees the full
despacho scope. The restriction composes with the existing `area`/`estado`/`q`/`responsableId`
filters and never widens cross-tenant (`WHERE { empresaId }` always applies).

#### Scenario: COMERCIAL list is scoped to own clients
- GIVEN despacho A has a proceso P1 whose cliente's responsableComercial is U1 and a proceso P2 of another comercial
- WHEN U1 (COMERCIAL, not JURIDICO, not admin) GETs `/procesos`
- THEN P1 is returned and P2 is NOT

#### Scenario: A COMERCIAL who is also JURIDICO sees all
- GIVEN a user holding both COMERCIAL and JURIDICO
- WHEN they GET `/procesos`
- THEN the full despacho scope is returned (the COMERCIAL-only restriction does not apply)
