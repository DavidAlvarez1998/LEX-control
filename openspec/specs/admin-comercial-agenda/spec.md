# Admin — Comercial Agenda & Seguimiento Specification

> New capability introduced by change `admin-comercial-agenda`. Adds an activity log per `Prospecto`
> (the seguimiento timeline) and a per-salesperson daily agenda of pending activities, on the
> platform sales side (`ventas` module). Platform-level data (no `empresaId` tenancy); scoped by the
> owning COMERCIAL, with ADMIN seeing all.

## ADDED Requirements

### Requirement: SeguimientoProspecto activity entity
The system MUST store sales activities in `seguimientos_prospecto`: `id` (cuid), `prospectoId`
FK→`Prospecto` (`onDelete: Cascade`), optional scalar `comercialId` (NO FK — the owning salesperson,
drives the agenda), `tipo` `TipoGestionComercial` (default `LLAMADA`), optional `titulo`, optional
`nota` (Text, context/why), optional `resultado` (Text, outcome once done), optional `fechaProgramada`
(when it is due), `completada` Boolean (default `false`), optional `fechaCompletada`, `createdAt`,
`updatedAt`. It MUST index `@@index([prospectoId, createdAt])`, `@@index([comercialId, fechaProgramada])`,
`@@index([comercialId, completada])`. `prospecto` is the ONLY relation FK; `comercialId` is a scalar.

#### Scenario: Activity belongs to a prospecto
- GIVEN a prospecto P
- WHEN an activity is created for P
- THEN it is stored with `prospectoId = P` and is removed if P is deleted (cascade)

#### Scenario: Reuses the existing tipo enum
- WHEN an activity is created with `tipo = WHATSAPP`
- THEN it is accepted using the existing `TipoGestionComercial` enum (no new enum is introduced)

### Requirement: Log or schedule an activity on a prospecto
`POST /prospectos/:id/seguimientos` MUST create an activity for the prospecto. If `fechaProgramada`
is omitted the activity MUST be stored as already done (`completada = true`, `fechaCompletada = now`);
if `fechaProgramada` is present it MUST be stored pending (`completada = false`). The `comercialId`
owner MUST default to the prospecto's `comercialId`, falling back to the caller's id when the
prospecto is unassigned. `GET /prospectos/:id/seguimientos` MUST return the prospecto's activities
newest-first.

#### Scenario: Log an interaction now
- GIVEN a comercial on their prospecto
- WHEN they POST `{ tipo: LLAMADA, nota: "Interesado", resultado: "Pide cotización" }` with no `fechaProgramada`
- THEN the activity is created `completada = true` with `fechaCompletada = now` and appears in the timeline

#### Scenario: Schedule a future follow-up
- WHEN they POST `{ tipo: LLAMADA, titulo: "Insistir oferta", fechaProgramada: <Thursday> }`
- THEN the activity is created `completada = false` due on Thursday (it will appear in the agenda)

#### Scenario: Owner defaults from the prospecto
- GIVEN prospecto P assigned to comercial B
- WHEN ADMIN adds an activity to P without specifying an owner
- THEN the activity's `comercialId` is B

### Requirement: Per-salesperson scope for activities
A COMERCIAL MUST only list/create/edit/complete/delete activities of prospectos assigned to them; the
API MUST reject access to another comercial's prospecto activities with 404. ADMIN MUST be able to
read and manage any activity and MAY filter a timeline or the agenda by `comercialId`.

#### Scenario: COMERCIAL cannot touch another's activity
- GIVEN an activity on a prospecto assigned to comercial B
- WHEN comercial A lists, edits, completes or deletes it
- THEN the API responds 404 for A

### Requirement: Edit, reschedule, complete and delete an activity
`PATCH /seguimientos/:id` MUST allow editing `tipo`/`titulo`/`nota`/`resultado` and rescheduling
`fechaProgramada`. `POST /seguimientos/:id/completar` MUST set `completada = true`, set
`fechaCompletada` (now unless provided) and store an optional `resultado`. `DELETE /seguimientos/:id`
MUST remove it. A COMERCIAL MUST NOT change an activity's `comercialId` (the field is ignored for
them); ADMIN MAY reassign it.

#### Scenario: Complete a scheduled activity
- GIVEN a pending activity due today
- WHEN the comercial POSTs `/seguimientos/:id/completar { resultado: "Cerró, agenda demo" }`
- THEN it becomes `completada = true` with `fechaCompletada = now` and that resultado

#### Scenario: Reschedule a follow-up
- WHEN the comercial PATCHes `fechaProgramada` to next Monday on a pending activity
- THEN the due date is updated and it remains pending

### Requirement: Per-comercial daily agenda
`GET /agenda` MUST return the caller's **pending** activities (`completada = false`) whose
`fechaProgramada` falls within the requested range (`desde`/`hasta`, both defaulting to today),
ordered by `fechaProgramada` ascending, each enriched with a prospecto summary (`id`, `nombreEmpresa`,
`nombreContacto`, `estado`, `telefono`). When `desde` is today, still-pending activities due **before**
today MUST be returned separately as overdue (`vencidas`). A COMERCIAL MUST be hard-scoped to
`comercialId = self`; ADMIN MAY pass `comercialId` to view a specific salesperson's agenda.

#### Scenario: See today's pending activities
- GIVEN a comercial with two activities due today and one due last week (all pending)
- WHEN they GET `/agenda` with no range
- THEN the two due today are returned for the day and the last-week one appears under `vencidas`

#### Scenario: Completed activities are not in the agenda
- GIVEN an activity due today that is already completed
- WHEN the comercial GETs `/agenda`
- THEN that activity is NOT returned (it lives in the timeline, not the agenda)

#### Scenario: ADMIN views a comercial's agenda
- WHEN ADMIN GETs `/agenda?comercialId=B`
- THEN only comercial B's pending activities are returned

### Requirement: Admin oversight of the sales team
The system MUST expose `GET /equipo-comercial` (ADMIN only) returning every `COMERCIAL` user with
their summary counters: total `prospectos`, `ganados`, and `pendientesAgenda` (pending activities).
A non-ADMIN MUST receive 403. The admin app MUST provide a "Equipo comercial" view listing
comerciales (searchable) and, on selecting one, that salesperson's prospectos (filterable by estado
and canal, each openable with its seguimiento timeline) and their agenda. The `/prospectos` admin
screen MUST additionally allow filtering by `comercialId`.

#### Scenario: Team summary with counters
- GIVEN comercial B with 5 prospectos (2 GANADO) and 4 pending activities
- WHEN ADMIN GETs `/equipo-comercial`
- THEN B appears with `prospectos = 5`, `ganados = 2`, `pendientesAgenda = 4`

#### Scenario: Only ADMIN may see the team summary
- WHEN a COMERCIAL GETs `/equipo-comercial`
- THEN the API responds 403

#### Scenario: Filter prospectos by salesperson
- WHEN ADMIN GETs `/prospectos?comercialId=B`
- THEN only B's prospectos are returned
