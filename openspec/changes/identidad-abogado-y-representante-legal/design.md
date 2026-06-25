# Design: lawyer identity + legal representative

## Domain model (the distinction that drove this)

```
   REPRESENTANTE LEGAL                         ABOGADO RESPONSABLE (apoderado)
   = rep of the CLIENT company                 = the lawyer who litigates
   • only a C.C. (not a lawyer)                • C.C. + tarjeta profesional
   • OTORGA (grants) the poder  ───────────────►  RECIBE (receives) it
   → per-proceso `datos`: repLegalNombre,       → entity `Usuario`: cedula,
     repLegalDocumento                            tarjetaProfesional
                                                  (exposed as proceso.responsable.*)
```

They are **different people on opposite sides of the poder**. The earlier confusion
("representante legal = abogado responsable") is wrong and is the reason this is
modelled in two different places.

## Part 1 — Lawyer identity (Usuario.cedula / tarjetaProfesional)

Columns already exist (`schema.prisma`). What's missing is plumbing them end-to-end.

| Layer | File | Change |
|---|---|---|
| Select | `usuarios/usuarios.shared.ts` | add `cedula`, `tarjetaProfesional` to `PUBLIC_SELECT` (so the API returns them for edit-prefill/display) |
| Validation (admin) | `usuarios/usuarios.schemas.ts` | add both as `z.string().trim().optional()` to create + update |
| Service (admin) | `usuarios/usuarios.service.ts` | `createUsuario` destructures fields explicitly → add both to `data`. `updateUsuario` already passes `input` through → no change beyond the schema |
| Validation (client) | `mi-empresa/mi-empresa.schemas.ts` | add both optional to `createMiembroSchema` |
| Service (client) | `mi-empresa/mi-empresa.service.ts` | `createMiembro` → add both to the create payload |
| UI client | `client …/equipo/page.tsx` | FormState + EMPTY_FORM + 2 inputs after "Nombre" + POST payload (create) |
| UI admin | `admin …/usuarios/page.tsx` | FormState + EMPTY_FORM + `abrirEditar` prefill + 2 inputs + create POST & edit PATCH payload; Usuario DTO type gains the two fields |

Both services build their create `data` by explicit fields (no `...input` spread), so the
two new fields must be added to each `data` object — not just the schema.

## Part 2 — Representante legal in the creation form

Pure metadata change in `seed-tipos.json` for "Proceso ejecutivo de mínima cuantía":

- `repLegalNombre` ("Representante legal del otorgante (si es sociedad)") and
  `repLegalDocumento` ("C.C. del representante legal"): set `soloFicha: false`.
- **Move** both fields to sit right after `fechaPoder` (the poder block), so in the
  creation form they read together with "Ciudad de firma del poder" / "Fecha del poder".
- The creation form auto-includes them: `procesos/nuevo` filters `!c.soloFicha`, and the
  ficha shows all fields regardless — so flipping the flag is enough (no client code).
- Apply with `pnpm seed:catalogo` (merge; updates the tipo definition, touches no
  procesos). Reminder: dev points at the **real DB** now — this is a prod write.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Rep legal = name + C.C. only | All the poder needs; "solo lo necesario". Correo/teléfono deferred. |
| D2 | Rep legal stays a per-proceso `datos` field | Already wired to the template; an entity/relation is a bigger change, out of scope. |
| D3 | Lawyer cédula/tarjeta editable in admin, create-only in client | admin update passes `input` through cheaply; client `mi-empresa` update only handles activo/roles — extending it is out of scope. |
| D4 | Add fields to `PUBLIC_SELECT` | Needed so the admin edit form can prefill existing values. |
