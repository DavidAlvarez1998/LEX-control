# Design: Assign Services + Per-Company Prices on Empresa

## Decision 1 — Manage assignments through the empresa resource (not a separate endpoint)
**Choice:** Accept an optional `servicios[]` on `POST /empresas` and `PATCH /empresas/:id` rather
than adding `/empresa-servicios` sub-routes.
**Rationale:** The admin form is a single modal with one "Guardar" action covering the company
and its services. A nested array maps 1:1 to that UX and avoids the client orchestrating multiple
calls (and partial-failure handling) from the browser. The trade-off — empresa endpoints do a bit
more — is contained because the work is wrapped in a transaction and validated up front.
**Reversible:** Dedicated sub-routes can be added later without removing this; the field is
additive and optional.

## Decision 2 — Replace-set semantics on update, only when the field is present
**Choice:** When `servicios` is present in a PATCH body it is the company's *complete* desired set
(create/update listed, delete omitted). When the field is absent, assignments are untouched.
**Rationale:** The form always knows the full intended set, so replace-set is the simplest mental
model and matches "save the form". Gating on presence keeps `PATCH` usable for plain field edits
(e.g. just renaming) without wiping assignments. PATCH semantics stay intact: absent = no change.

## Decision 3 — Defaults resolved server-side from the catalog
**Choice:** Each price field omitted from an assignment is filled from the catalog `Servicio`
inside the handler (after fetching the referenced services); `activo` defaults to `true`.
**Rationale:** Makes the API robust regardless of client, and centralizes the "catalog is the
reference" rule. The frontend still pre-fills the inputs for good UX, but the server is the source
of truth and validates the `servicioId`s in the same query it uses for defaults.

## Decision 4 — Atomicity via `prisma.$transaction`
**Choice:** Create-with-assignments and reconcile-on-update run in a single interactive
transaction; validation of ids happens first so an invalid `servicioId` aborts before any write.
**Rationale:** Avoids the "empresa created but services failed" state. The unique constraint
`@@unique([empresaId, servicioId])` makes upsert-by-pair safe.

## Validation & error mapping
- Unknown / duplicate `servicioId` → `400` (`HttpError(400, …)`), mapped before writes.
- Existing empresa P2002 (RFC/NIT) / P2025 (not found) handling is unchanged.
- Zod validates the array shape (non-negative numbers, integer `incluidos`).

## Data flow (admin form)
1. Modal opens → `GET /servicios` (catalog) for the selectable list + reference prices.
2. Editing → `GET /empresas/:id` for existing `servicios` to pre-check and pre-fill overrides.
3. Save → build `servicios[]` from selected rows → single `POST`/`PATCH /empresas`.
4. Response returns the empresa with `servicios`; list view refreshes (`_count.servicios`).

## API contract (assignment item)
```jsonc
{
  "servicioId": "ckxx…",        // required, must exist in catalog
  "precioBase": 80,              // optional → catalog Servicio.precioBase
  "precioPorUnidad": 4.5,        // optional → catalog Servicio.precioPorUnidad
  "incluidos": 5,                // optional int → catalog Servicio.incluidos
  "activo": true                 // optional → true
}
```
Decimals are accepted as numbers and serialized back as strings by Prisma (existing convention).
