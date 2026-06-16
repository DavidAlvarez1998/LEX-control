# Clientes & Prospectos Specification

> New capability introduced by change `foundations-roles-plans-clientes`. Adds the commercial CRM identity `Cliente` (single-row lifecycle PROSPECTO → CLIENTE → DESCARTADO), distinct from the procedural `Litigante`, and bridged to it by a nullable `litiganteId`. Foundations provides only the data layer; the contratos/comercial modules consume it.

## ADDED Requirements

### Requirement: Cliente as a single-row commercial identity per empresa
The system MUST store commercial CRM identities in `clientes`: `id` (cuid), `empresaId` FK→`Empresa` (Cascade), `estado` `EstadoCliente` (default `PROSPECTO`), `fechaIngreso` (default now), `tipoPersona` `TipoPersona` (default `NATURAL`), `nombre`, optional `tipoDocumento` `TipoDocumento` + `numeroDocumento`, optional `telefono`/`email`/`ciudad`, `canalIngreso` `CanalIngreso`, optional `tipoCaso` `TipoCaso`, optional `necesidadTipoProcesoId` FK→`TipoProceso` (SetNull), optional `resumenCaso` (Text), `viabilidad` `Viabilidad?` (default `EN_ESTUDIO`), optional `responsableComercialId` FK→`Usuario` (SetNull), optional `observaciones` (Text), optional `litiganteId` FK→`Litigante` (SetNull), optional `convertidoEn`, `createdAt`, `updatedAt`. It MUST index `@@index([empresaId])`, `@@index([estado])`, `@@index([responsableComercialId])`. A `Cliente` MUST be scoped to one empresa and a despacho MUST NOT see another's clientes.

#### Scenario: Create a pure lead
- GIVEN a user in despacho A
- WHEN they create a `Cliente` with a `nombre`, `canalIngreso = INSTAGRAM`, and no `litiganteId`
- THEN it is created with `estado = PROSPECTO`, `viabilidad = EN_ESTUDIO`, `litiganteId = null`, owned by despacho A

#### Scenario: Cross-tenant isolation
- GIVEN a `Cliente` of despacho B
- WHEN a user of despacho A lists clientes
- THEN despacho B's cliente is NOT returned

### Requirement: Only Empresa cascades into Cliente (errno-150 discipline)
Every outgoing FK from `Cliente` (`necesidadTipoProcesoId`→`TipoProceso`, `responsableComercialId`→`Usuario`, `litiganteId`→`Litigante`) MUST be `SetNull`; only `empresaId`→`Empresa` MUST be `Cascade`. This MUST avoid any MySQL multiple-cascade path (errno-150), matching the discipline used for `ParteProceso`.

#### Scenario: Deleting empresa removes its clientes
- GIVEN an empresa with clientes
- WHEN the empresa is deleted
- THEN its `clientes` rows are removed via Cascade

#### Scenario: Deleting a referenced TipoProceso nulls the link
- GIVEN a `Cliente` whose `necesidadTipoProcesoId` points at a `TipoProceso`
- WHEN that `TipoProceso` is deleted
- THEN the `Cliente` row survives with `necesidadTipoProcesoId = null`

#### Scenario: Deleting the responsable comercial nulls the link
- GIVEN a `Cliente` whose `responsableComercialId` points at a `Usuario`
- WHEN that `Usuario` is deleted
- THEN the `Cliente` survives with `responsableComercialId = null`

### Requirement: Outgoing FKs must reference the SAME empresa (B3)
On any write that sets `responsableComercialId`, `litiganteId`, or `necesidadTipoProcesoId`, the application MUST validate that the referenced `Usuario` / `Litigante` / `TipoProceso` belongs to the SAME empresa as the `Cliente` (and that `empresaId` itself is taken from the authenticated request, never client input). A cross-empresa reference MUST be rejected (no DB-level cross-tenant constraint exists; this is enforced in application code).

#### Scenario: Cross-empresa responsable is rejected
- GIVEN an empresa admin of despacho A creating/updating a `Cliente` in A
- WHEN the body sets `responsableComercialId` to a `Usuario` of despacho B
- THEN the write is rejected (cross-tenant reference) and no row is created/updated

#### Scenario: empresaId comes only from the token
- GIVEN an authenticated user of despacho A
- WHEN they POST a `Cliente` with `empresaId = B` in the body
- THEN the body `empresaId` is ignored and the `Cliente` is created in despacho A

### Requirement: Lifecycle estados (PROSPECTO / CLIENTE / DESCARTADO)
`EstadoCliente` MUST be a closed enum `{ PROSPECTO, CLIENTE, DESCARTADO }` and a `Cliente` MUST move through these as a single row (no copy step). The transition `PROSPECTO → CLIENTE` MUST be stamped by `convertidoEn` and is written by the contratos module when contrato + poder are firmado; foundations only provides the `estado` and `convertidoEn` columns. A discarded lead MUST be representable as `DESCARTADO` without deletion.

#### Scenario: Lead identity preserved across conversion
- GIVEN a `Cliente` with `estado = PROSPECTO` and accumulated CRM fields
- WHEN it is converted to `estado = CLIENTE`
- THEN it is the SAME row (same `id`, same history) with `convertidoEn` set

#### Scenario: Discard without deletion
- GIVEN a `Cliente` with `estado = PROSPECTO`
- WHEN it is marked `DESCARTADO`
- THEN the row persists with `estado = DESCARTADO`

### Requirement: CRM enums
The system MUST define the marketing-facing enums: `CanalIngreso { REFERIDO, INSTAGRAM, FACEBOOK, WHATSAPP, WEB, LLAMADA, OTRO }`; `TipoCaso { CIVIL, LABORAL, PENAL, ADMINISTRATIVO, DISCIPLINARIO, CONSTITUCIONAL, FAMILIA, COMERCIAL, TRANSITO, AMBIENTAL, OTRO }` (broader than `Jurisdiccion`); `Viabilidad { VIABLE, NO_VIABLE, EN_ESTUDIO }`. These MUST be additive and MUST NOT modify existing enums.

#### Scenario: Enums available and additive
- GIVEN a migrated database
- WHEN the schema is inspected
- THEN `CanalIngreso`, `TipoCaso`, `Viabilidad` exist with the listed members AND `Jurisdiccion`/`TipoPersona`/`TipoDocumento` are unchanged

### Requirement: Bridge to the procedural Litigante on conversion
`Litigante` MUST remain the canonical procedural party (unchanged; it can be a counterparty/tercero and is NOT inherently "our client"). A `Cliente` WITHOUT a `litiganteId` MUST represent a pure lead. On conversion the application MUST link a `Litigante` matched on `(empresaId, tipoDocumento, numeroDocumento)` and set `Cliente.litiganteId`. DECISION B3 — match mechanism: an atomic Prisma `upsert` requires `@@unique([empresaId, tipoDocumento, numeroDocumento])` on `Litigante` (a change to an existing table); if that unique is NOT added, the link MUST be an application-level find-or-create (best-effort, may race; dedupe handled explicitly). Leads without a `numeroDocumento` cannot be matched and MUST create a fresh `Litigante` on conversion. A fully-materialized client MUST be derivable as a `Cliente` with a `litiganteId` whose `Litigante` appears in a `ParteProceso` with `esNuestroCliente = true` (the existing `esNuestroCliente` field is unchanged). The bridge MUST be FK-ready for a future "Solicitud de Asignación de Procesos" without further schema change here.

#### Scenario: Pure lead has no litigante
- GIVEN a `Cliente` that has never been converted
- WHEN its `litiganteId` is read
- THEN it is null

#### Scenario: Link litigante on conversion matched by document
- GIVEN a `Cliente` with `tipoDocumento = CC`, `numeroDocumento = 123` in despacho A being converted
- WHEN the application materializes the party
- THEN it upserts/links a `Litigante` in despacho A matched on `(empresaId, CC, 123)` and sets `Cliente.litiganteId` to it

#### Scenario: Litigante stays canonical and may be a counterparty
- GIVEN a `Litigante` that is the counterparty in a proceso (not our client)
- WHEN clientes are added to the model
- THEN that `Litigante` needs no `Cliente` row AND its `ParteProceso.esNuestroCliente` semantics are unchanged

#### Scenario: Deleting the linked litigante nulls the bridge
- GIVEN a converted `Cliente` whose `litiganteId` points at a `Litigante`
- WHEN that `Litigante` is deleted
- THEN the `Cliente` survives with `litiganteId = null`

### Requirement: Responsable comercial is the originator (relaxed role guidance)
> MODIFIED by change `cliente-convert-ownership`.

The previous guidance that `responsableComercialId` SHOULD hold `RolEmpresa.COMERCIAL` is RELAXED: the responsable is the **originator** and MAY hold `COMERCIAL` or `JURIDICO` (the abogado who brought the client). This was never enforced in code; the field MUST remain a nullable `SetNull` FK validated same-empresa.

#### Scenario: Assigning a comercial responsable
- GIVEN a user holding `RolEmpresa.COMERCIAL` in the despacho
- WHEN they are set as `responsableComercialId` of a `Cliente`
- THEN the assignment is accepted

#### Scenario: A JURIDICO is a valid responsable
- GIVEN a prospecto created by a user holding only JURIDICO
- WHEN it is stored
- THEN `responsableComercialId` = that abogado is valid (no role rejection)

### Requirement: The CRM list surfaces derived seguimiento signals
> MODIFIED by change `comercial-seguimiento-accionable`.

The clientes list MUST be readable as a pipeline at a glance: the derived seguimiento signals (`ultimaGestionEn`/`diasSinGestion`, `proximaTareaEn`/`tareaVencida`, `faseActual`/`diasEnFase`, `ultimaDisposicion`) are supplied by `GET /comercial/pipeline` (see capability `comercial-pipeline`) and consumed by the CRM list with quick filters (`?mios`, frío, vencidas, fase). These signals MUST remain computed on read and MUST NOT add stored columns to `Cliente`.

#### Scenario: List shows signals without new stored fields
- GIVEN the CRM list of a despacho
- WHEN it renders a cliente row
- THEN it shows the cliente's derived signals sourced from the pipeline endpoint AND no signal is persisted on the `Cliente` row

### Requirement: No ownership wall on cliente edit/convert
> ADDED by change `cliente-convert-ownership`.

The system MUST NOT block editing or converting a `Cliente` based on who its `responsableComercialId` is. Any user of the despacho holding the relevant permiso (`cliente.editar` / `cliente.convertir`) MAY act on ANY `Cliente` of the same `empresa`. Ownership is informational (attribution + the "Míos" filter), NOT an authorization gate. The UI SHOULD surface the responsable (e.g. "Responsable: X") and MAY warn when acting on another user's cliente, but MUST NOT prevent the action.

#### Scenario: A user converts another user's prospecto
- GIVEN a PROSPECTO whose `responsableComercialId` is user A, and user B holds `cliente.convertir`
- WHEN user B converts it
- THEN it succeeds (no ownership block); the UI had shown a soft notice that it belongs to A

### Requirement: Responsable comercial defaults to the creator on create
> ADDED by change `cliente-convert-ownership`.

On `POST /clientes`, when the body does not set `responsableComercialId`, the system MUST set it to the authenticated creator (`req.user.sub`). When the body sets it, that value is used (and still validated same-empresa). This makes every prospecto have an owner for attribution and the "Míos" filter.

#### Scenario: Auto-assign creator
- GIVEN a user creates a prospecto without `responsableComercialId`
- THEN the created `Cliente` has `responsableComercialId = ` the creator's id

### Requirement: Reads expose the responsable identity
> ADDED by change `cliente-convert-ownership`.

`GET /clientes` and `GET /clientes/:id` MUST include `responsableComercial { id, nombre }` (nullable) so the UI can show who owns each cliente.

#### Scenario: List carries the responsable name
- GIVEN a cliente with a responsable
- WHEN the list is fetched
- THEN each row carries `responsableComercial: { id, nombre }`

### Requirement: RBAC — cliente.convertir includes JURIDICO
> ADDED by change `cliente-convert-ownership`.

`cliente.convertir` MUST be granted to `ADMINISTRADOR`, `COMERCIAL` AND `JURIDICO` (was ADMINISTRADOR + COMERCIAL). The abogado who does intake can activate his own prospecto without a comercial. `cliente.ver` stays the four roles; `cliente.crear`/`cliente.editar` stay ADMINISTRADOR + COMERCIAL + JURIDICO.

#### Scenario: Abogado converts
- GIVEN a user holding only `RolEmpresa.JURIDICO` (not esAdminEmpresa)
- WHEN they POST `/clientes/:id/convertir` on a same-empresa PROSPECTO
- THEN it succeeds (200), the cliente becomes CLIENTE
