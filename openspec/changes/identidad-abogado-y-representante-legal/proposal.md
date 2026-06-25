# Proposal: Capture lawyer identity (cédula + tarjeta) and the legal representative

## Why

The poder (power-of-attorney) template — and other generated writs — already reference
two identities that the UI does **not** let anyone fill, so they render empty:

- **The responsible lawyer (apoderado).** `Usuario.cedula` and
  `Usuario.tarjetaProfesional` exist in the DB and the templates use them as
  `proceso.responsable.cedula` / `.tarjetaProfesional` ("…confiero PODER a {{nombre}},
  C.C. {{cedula}} y Tarjeta Profesional {{tarjetaProfesional}}"). But **no user form
  exposes these columns**, so every lawyer's C.C./tarjeta is blank in the documents.

- **The legal representative (representante legal).** When the otorgante (the client)
  is a company, the poder is granted by its **representante legal** — a *third party*,
  distinct from the responsible lawyer: the rep grants the poder, the lawyer receives
  it. The minimum-amount executive type already defines `repLegalNombre` and
  `repLegalDocumento`, **but they are `soloFicha`** — only visible in the ficha, not in
  the creation form, so they can't be captured up front when drafting the poder.

Net effect: the poder cannot be produced complete from the creation flow.

## What changes

Two small, additive changes — no schema migration (all columns/fields already exist):

1. **Lawyer identity UI.** Expose **Cédula** and **Tarjeta profesional** inputs in the
   create/edit user forms (client `/equipo` — where the despacho's lawyers/JURIDICO
   users live — and admin `/usuarios`), wired to the existing `Usuario.cedula` /
   `tarjetaProfesional` columns. Accept them in the user create/update validation
   (both the `usuarios` and `mi-empresa` modules) and return them in `PUBLIC_SELECT`.

2. **Representante legal in the creation form.** Flip `repLegalNombre` and
   `repLegalDocumento` from `soloFicha: true` to `false` so they show in **both** the
   creation form and the ficha, and reposition them next to the poder block
   (`ciudadFirmaPoder` / `fechaPoder`) for a natural read.

## Scope decisions

- **Legal representative fields = name + C.C. only** ("solo lo necesario"): that is all
  the poder requires. No correo/teléfono for now (the company's notification data lives
  on the `Litigante`/`Cliente` already; can be added later if a real need appears).
- The representante legal stays a **per-proceso field** (`datos`), as it already is —
  not a new entity/relation. Reusing it across procesos would be a larger change, out
  of scope.

## Non-goals

- No new Prisma model or migration.
- No editing of cédula/tarjeta from the client `/equipo` *edit* path (create only there);
  admin `/usuarios` supports create + edit. (Client edit can be added later.)

## Impact

- Affected: `lex-control-api` (usuarios + mi-empresa schemas/services, PUBLIC_SELECT),
  both frontends' user forms, and `seed-tipos.json` (re-seed via `pnpm seed:catalogo`).
- Risk: low, additive. Rollback = revert the edits; the DB columns/fields were already
  there.
