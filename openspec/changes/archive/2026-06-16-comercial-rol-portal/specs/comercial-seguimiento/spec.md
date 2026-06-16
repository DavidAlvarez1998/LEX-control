# Comercial — Seguimientos · delta (agenda lifecycle)

> Change `comercial-rol-portal`. Extends `SeguimientoComercial` with the agenda fields and the
> activity lifecycle (completar / cancelar / reabrir) so the same row powers both the contact-touch
> log and the firm's agenda. `fechaProximaTarea` is the slot. (The later `client-agenda-universal`
> change made these endpoints baseline; this change introduced the agenda model itself.)

## ADDED Requirements

### Requirement: SeguimientoComercial carries agenda fields and an activity lifecycle
`SeguimientoComercial` MUST gain agenda columns (additive, `db push`, no existing column changed):
`comercialId` (scalar, NO FK — the OWNER of the activity; backfilled from `registradoPorId`),
`titulo`, `completada` `Boolean @default(false)`, `fechaCompletada?`, `canceladaEn?`,
`motivoCancelacion?` (Text), and the index `@@index([empresaId, comercialId, fechaProximaTarea])`.
The owner defaults to the caller; only an `esAdminEmpresa` caller may act on another `comercialId`.

#### Scenario: Owner defaults to the caller
- GIVEN a non-admin user creates an agenda activity
- WHEN it is stored
- THEN `comercialId` = that user (they cannot set another owner)

### Requirement: GET /comercial/agenda is a month-scoped, owner-aware calendar feed
`GET /comercial/agenda` MUST return the activities whose `fechaProximaTarea` falls in the requested
month window plus, optionally, the overdue `vencidas` (`fechaProximaTarea < desde`, still pending).
It MUST honor `incluirCompletadas` (default: only pending) and the owner rule: a non-admin caller is
scoped to their own `comercialId`; an `esAdminEmpresa` caller may pass `comercialId` to view a
member's agenda (or all). Tenant scope (`WHERE { empresaId }`) always applies. Each item MUST carry
its `registradoPor` (resolved in batch from the scalar `registradoPorId`, scoped by empresa).

#### Scenario: Comercial sees only their own slots
- GIVEN agenda activities of U1 and U2 in despacho A
- WHEN U1 (non-admin) GETs `/comercial/agenda` for a month
- THEN only U1's activities (and U1's vencidas) are returned

#### Scenario: Admin can view a member's agenda
- GIVEN a firm ADMINISTRADOR
- WHEN they GET `/comercial/agenda?comercialId=U1`
- THEN U1's activities are returned

### Requirement: Activities can be completed, cancelled, and reopened
The system MUST expose `POST /comercial/seguimientos/:id/{completar,cancelar,reabrir}` (each
`requireAuth`, tenant-scoped): `completar` sets `completada = true` + `fechaCompletada` (optionally a
`resultado`); `cancelar` sets `canceladaEn` + `motivoCancelacion` (the activity stays visible, NOT
deleted); `reabrir` clears the completion/cancellation marks. A cancelled or completed activity is
distinguishable from a deleted one (it is never hard-deleted).

#### Scenario: Cancel keeps the row visible
- GIVEN a pending agenda activity
- WHEN it is cancelled with a motivo
- THEN `canceladaEn`/`motivoCancelacion` are set, the row persists and is not returned among pending slots

#### Scenario: Reopen restores a completed activity
- GIVEN a completed activity
- WHEN `reabrir` is called
- THEN `completada = false` and `fechaCompletada` is cleared
