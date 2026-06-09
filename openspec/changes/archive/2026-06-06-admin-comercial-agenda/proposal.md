# Proposal — admin-comercial-agenda

## Why

The platform sales pipeline (`admin-comercial-ventas`) tracks a prospecto's **funnel state**
(`NUEVO → … → GANADO/PERDIDO`) and a single free-text `notas` field — but a COMERCIAL has no way to
record the **history of touchpoints** with a lead, nor to **schedule the next one**. Selling a Plan
takes many follow-ups ("called, will call back Thursday to insist", "sent the quote on WhatsApp",
"demo booked for Monday 3pm"). Today none of that is captured, so a comercial cannot see what they
already did with a prospecto, and has no daily agenda of who to chase.

This change adds, on the **admin** side only, the two missing pieces:

1. **Seguimiento timeline** — a chronological log of interactions per prospecto.
2. **Agenda per comercial** — a per-day calendar of pending activities the comercial schedules for
   themselves (the future, not-yet-done activities), with overdue surfaced.

These are one concept: an **activity** that is born *scheduled* (pending → shows in the agenda) and,
once done, becomes part of the *timeline*.

## What changes

- **`SeguimientoProspecto`** — one activity attached to a `Prospecto`: `tipo` (reuses
  `TipoGestionComercial`: LLAMADA/WHATSAPP/REUNION/VIDEOLLAMADA/CORREO/OTRO), short `titulo`, `nota`
  (context/why), `resultado` (outcome once done), `fechaProgramada` (when it is due — drives the
  agenda; null = logged immediately), `completada` + `fechaCompletada`, and a `comercialId` owner
  (the agenda is per person). Cascade-deleted with its prospecto.
- **Endpoints** (mounted in the existing `ventas` module, guarded by `requireRole(ADMIN, COMERCIAL)`):
  - `GET /prospectos/:id/seguimientos` — timeline for one prospecto
  - `POST /prospectos/:id/seguimientos` — add/schedule an activity
  - `PATCH /seguimientos/:id` — edit / reschedule
  - `POST /seguimientos/:id/completar` — mark done (records `resultado`, `fechaCompletada`)
  - `DELETE /seguimientos/:id` — remove
  - `GET /agenda` — the caller's pending activities in a date range (with prospecto summary);
    ADMIN may filter by `comercialId`, COMERCIAL is hard-scoped to their own.
- **Access**: same model as prospectos — a COMERCIAL only sees/touches activities of **their own**
  prospectos and **their own** agenda; ADMIN sees everything and may filter by comercial.
- **Admin UI**:
  - Prospecto detail panel gains a **Seguimiento** timeline + an "add activity" form (log now, or
    schedule for a future date).
  - New nav item **Agenda** (`/agenda`): a day view (date navigation) of the comercial's pending
    activities, with **vencidas** (overdue) called out and a one-click "completar"; ADMIN gets a
    comercial selector.

## Out of scope

- Real calendar integrations (Google/Outlook), email/push reminders, recurring activities.
- Activities on already-won `Empresa`s (post-sale account management) — this is the **pre-sale**
  pipeline only; can be a later change.
- Editing the existing funnel/win/lose behaviour.

## Rollback plan

Additive only. The new model is a leaf table (`onDelete: Cascade` from `Prospecto`, no other model
references it) and all new endpoints are new routes. Rollback = drop the `seguimientos_prospecto`
table, remove the routes/UI; nothing existing depends on it.
