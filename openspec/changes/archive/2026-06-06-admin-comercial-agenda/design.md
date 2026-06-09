# Design — admin-comercial-agenda

## Architecture decisions

### One entity for both timeline and agenda
A single `SeguimientoProspecto` row models both a *logged* interaction and a *scheduled* one,
distinguished by two orthogonal fields:

- `fechaProgramada` — when the activity is due. Drives the **agenda**. Optional: an activity logged
  after the fact (no scheduling) leaves it null.
- `completada` (+ `fechaCompletada`) — whether it has happened. Drives the **timeline** vs the
  agenda's "pending" filter.

Rationale: the real flow is "I'll call them Thursday" (scheduled, pending) → "called, they want the
mid plan" (completed, with `resultado`). Forcing two tables would duplicate the type/links and make
"complete this scheduled call" a cross-table move. Mirrors the client-side `SeguimientoComercial`
pattern (which already bundles `proximaTarea`/`fechaProximaTarea`/`estadoSeguimiento`), but uses a
boolean + dates so the agenda math is trivial.

Derived states (computed, never stored):
- **pendiente**: `!completada`
- **vencida** (overdue): `!completada && fechaProgramada < startOfToday`
- **hoy**: `!completada && fechaProgramada` within today
- **completada**: `completada`

### Reuse `TipoGestionComercial`
The activity `tipo` reuses the existing global enum `TipoGestionComercial`
(LLAMADA/WHATSAPP/REUNION/VIDEOLLAMADA/CORREO/OTRO) instead of inventing a parallel one. It is a
generic, tenancy-free enum already used by the client funnel; the values fit the platform sales case
exactly. No schema enum churn.

### Scalar `comercialId`, no FK (follow Prospecto)
`comercialId` is a plain indexed column with **no Prisma relation**, exactly like `Prospecto.comercialId`
and the other `ventas` scalars. The agenda is "my activities" = `where comercialId = me`. On create,
the owner defaults to the parent prospecto's `comercialId` (fallback: the creating COMERCIAL's id).
A leadwith no assigned comercial yet produces activities with `comercialId = creator`.

### Authorization & scoping (identical to prospectos)
- Guard: `requireRole(Rol.ADMIN, Rol.COMERCIAL)`.
- A COMERCIAL is hard-scoped: every read/write filters by the **parent prospecto being in their
  scope** (reusing `cargarProspecto`, which already returns 404 for someone else's prospecto). The
  agenda additionally hard-scopes by `comercialId = self`.
- ADMIN sees all and may pass `comercialId` to filter the agenda or a prospecto's timeline.
- A COMERCIAL may not reassign `comercialId` on an activity (ignored, like prospecto reassignment).

### Endpoint placement
All routes live in the existing `lex-control-api/src/modules/ventas` module (this is platform sales).
Two new routers exported from `ventas.router.ts`:
- `seguimientoRoutes` — mounted at `/seguimientos` for `PATCH/DELETE/:id` and `:id/completar`.
- `agendaRoutes` — mounted at `/agenda` for `GET /`.
The per-prospecto list/create live on the existing `prospectoRoutes` as nested
`/:id/seguimientos`. Mounted in `app.ts` next to `/prospectos` and `/comisiones`.

### Agenda query
`GET /agenda?desde=YYYY-MM-DD&hasta=YYYY-MM-DD&comercialId=&incluirCompletadas=false`:
- Defaults: `desde` = today, `hasta` = today (single-day view); the UI widens to a week/month as
  needed by passing the range.
- Returns activities ordered by `fechaProgramada asc`, each enriched with a small prospecto summary
  (`{ id, nombreEmpresa, nombreContacto, estado, telefono }`) so the agenda is actionable without a
  second fetch. Overdue items (`fechaProgramada < desde`, still pending) are returned in a separate
  `vencidas[]` block when `desde` = today, so the comercial never loses a missed follow-up.

## Data model

```prisma
model SeguimientoProspecto {
  id              String               @id @default(cuid())
  prospectoId     String
  comercialId     String?              // escalar sin FK -> Usuario (dueño = agenda)
  tipo            TipoGestionComercial @default(LLAMADA)
  titulo          String?
  nota            String?              @db.Text
  resultado       String?              @db.Text
  fechaProgramada DateTime?
  completada      Boolean              @default(false)
  fechaCompletada DateTime?
  createdAt       DateTime             @default(now())
  updatedAt       DateTime             @updatedAt

  prospecto Prospecto @relation(fields: [prospectoId], references: [id], onDelete: Cascade)

  @@index([prospectoId, createdAt])
  @@index([comercialId, fechaProgramada])
  @@index([comercialId, completada])
  @@map("seguimientos_prospecto")
}
```
`Prospecto` gains `seguimientos SeguimientoProspecto[]`.

## UI

- **Prospecto detail** (`/prospectos`): below the funnel actions, a vertical **timeline** (newest
  first) showing each activity's tipo icon, fecha, titulo/nota and resultado; pending items show a
  "Completar" button; an inline form adds an activity with a *fecha programada* (optional) — leaving
  it empty logs it as done now.
- **Agenda** (`/agenda`, new nav, ADMIN+COMERCIAL): a date header with ‹ Hoy ›  navigation, a
  **Vencidas** section (overdue, red) and a **list for the selected day** grouped by time, each row
  linking to its prospecto with a one-click *Completar*. ADMIN sees a comercial `<select>`. A small
  month strip / week toggle is a nice-to-have; the day list is the MVP.

## Risks
- Timezone: `fechaProgramada` is a `DateTime`; day-bucketing uses the server's local day boundaries
  consistently on both query and display. Acceptable for a single-region (Colombia) deployment.
