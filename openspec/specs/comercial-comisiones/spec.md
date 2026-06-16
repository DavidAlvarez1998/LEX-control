# Comercial — Comisiones del Despacho Specification

> New capability introduced by change `comercial-rol-portal`. Adds `ComisionDespacho`, the firm's
> INTERNAL, MANUAL commission to its comercial for a closed client — distinct from the platform-level
> `Comision` (capability `admin-comisiones`, the COMERCIAL platform rol selling Planes). The
> ADMINISTRADOR registers/edits; the COMERCIAL only sees their own.

## ADDED Requirements

### Requirement: ComisionDespacho as a manual tenant-scoped commission row
The system MUST store internal commissions in `comisiones_despacho`: `id` (cuid), `empresaId`
(denormalized, NO FK), `clienteId` FK→`Cliente` (Cascade), `comercialId` (scalar, NO FK → the
`Usuario` who closed), optional `contratoId` (scalar, NO FK → originating `ContratoComercial`),
`baseCalculo` `Decimal(14,2)`, optional `porcentaje` `Decimal(5,2)` (null = fixed amount), `monto`
`Decimal(14,2)`, `estado` `EstadoComisionDespacho @default(PENDIENTE)`, optional `fechaPago`, optional
`notas` (Text), optional `registradoPorId` (scalar, NO FK — the ADMIN who registered it, audit),
`createdAt`, `updatedAt`. Only `Cliente` cascades in. The enum `EstadoComisionDespacho { PENDIENTE,
PAGADA, ANULADA }` MUST exist (additive). It MUST index `@@index([empresaId, estado])`,
`@@index([comercialId, estado])`, `@@index([clienteId])`. Commissions are MANUAL — there is NO
automatic trigger on contract close.

#### Scenario: Admin registers a commission
- GIVEN a firm ADMINISTRADOR in despacho A
- WHEN they register a `ComisionDespacho` for a cliente of A with `baseCalculo`, `monto`, `comercialId`
- THEN it is created `estado = PENDIENTE` with `empresaId` from the token and `registradoPorId` = the admin

#### Scenario: No automatic commission on close
- GIVEN a `ContratoComercial` reaches FIRMADO
- WHEN the close happens
- THEN NO `ComisionDespacho` is created automatically (the row exists only when an admin registers it)

### Requirement: RBAC — admin manages, comercial reads own
`comercial.comision.ver` MUST be granted to `ADMINISTRADOR` + `COMERCIAL`; `comercial.comision.crear`
and `comercial.comision.editar` MUST be granted to `ADMINISTRADOR` ONLY (soloAdmin). On
`GET /comercial/comisiones`, an `esAdminEmpresa` caller sees all rows of the empresa (optional
`clienteId`/`comercialId`/`estado` filters); a non-admin caller is hard-scoped by row to
`comercialId = req.user.sub` (sees ONLY their own), since RBAC cannot express row ownership.
Endpoints: `GET/POST/PATCH /comercial/comisiones`, all under `requireAuth` + the concrete clave and
hard `WHERE { empresaId }`. `POST` MUST validate `clienteId` and `comercialId` belong to the empresa.

#### Scenario: Comercial sees only their own
- GIVEN comisiones of despacho A for comercial U1 and comercial U2
- WHEN U1 (COMERCIAL, not admin) GETs `/comercial/comisiones`
- THEN only U1's comisiones are returned (`comercialId = U1`), ignoring any `comercialId` query

#### Scenario: Comercial cannot create or edit
- GIVEN a user holding only `RolEmpresa.COMERCIAL`
- WHEN they POST or PATCH `/comercial/comisiones`
- THEN it is rejected 403 (only ADMINISTRADOR holds `.crear`/`.editar`)

#### Scenario: Admin sees all and can register
- GIVEN a firm ADMINISTRADOR
- WHEN they GET `/comercial/comisiones` and POST a new one
- THEN they see every comisión of the empresa and the POST succeeds (201)
