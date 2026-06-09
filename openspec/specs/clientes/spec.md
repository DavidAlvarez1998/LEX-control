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

### Requirement: Responsable comercial should hold COMERCIAL
When `responsableComercialId` is set, the referenced `Usuario` SHOULD hold `RolEmpresa.COMERCIAL` (app-enforced, not a DB constraint). The field MUST remain nullable and `SetNull`.

#### Scenario: Assigning a comercial responsable
- GIVEN a user holding `RolEmpresa.COMERCIAL` in the despacho
- WHEN they are set as `responsableComercialId` of a `Cliente`
- THEN the assignment is accepted
