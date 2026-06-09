# Proposal: Assign Services + Per-Company Prices when Creating/Editing an Empresa (Admin)

## Intent
The admin console can create and edit `Empresa`s, and the service catalog (`Servicio`) carries
reference prices (`precioBase`, `precioPorUnidad`, `incluidos`). But there is no way to assign
services to a company or set the **negotiated price for that company**. The `EmpresaServicio`
join already exists in the schema for exactly this — it is just not exposed by the API or the
admin UI. This change wires the empresa create/edit flow so an ADMIN can pick which services a
company contracts and adjust each price, pre-filled from the catalog reference values.

## Scope

### In Scope
- Extend `POST /empresas` and `PATCH /empresas/:id` (ADMIN-only) to accept an optional
  `servicios` array describing the company's contracted services with per-company prices.
- Replace-set (reconcile) semantics on update: the provided list becomes the company's full set
  of assignments — new ones are created, existing ones updated, omitted ones removed.
- Per-assignment prices default to the catalog `Servicio`'s reference values when a price field
  is omitted, and may be overridden per company.
- Return the empresa with its `servicios` (each including the catalog `servicio`) from create and
  update so the UI can render immediately.
- Admin empresa form: a "Servicios contratados" section listing catalog services with a
  checkbox each; selecting one reveals editable price fields pre-filled from the catalog. On
  edit, the section is pre-populated from the company's existing assignments.

### Out of Scope
- Standalone `EmpresaServicio` CRUD endpoints (`/empresa-servicios`); assignments are managed
  through the empresa resource only.
- Editing the catalog `Servicio` itself (already covered by `service-management`).
- The client (tenant) portal view of contracted services.
- Billing/invoice generation from these assignments.

## Capabilities

### New Capabilities
- `empresa-servicios`: assigning services and per-company prices through the empresa create/edit
  endpoints, with catalog-reference defaults and replace-set reconciliation.

### Modified Capabilities
- None. (`service-management` and the empresa endpoints described in `api-foundation` are
  extended, but the existing requirements there are unchanged.)

## Approach
Manage assignments through the empresa resource so the admin form keeps its single "Guardar"
action. `createEmpresaSchema`/`updateEmpresaSchema` gain an optional `servicios[]`. The empresa
POST/PATCH handlers run a Prisma transaction: validate the referenced `servicioId`s against the
catalog, fill missing price fields from the catalog `Servicio`, then create (POST) or reconcile
(PATCH) the `empresa_servicios` rows. The admin form fetches `/servicios` for the catalog and,
on edit, the full empresa (`GET /empresas/:id`) for existing assignments.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/src/modules/empresas/empresas.schemas.ts` | Modified | Add `servicioAsignadoSchema`; add optional `servicios[]` to create/update |
| `lex-control-api/src/modules/empresas/empresas.router.ts` | Modified | Transactional create-with-assignments and reconcile-on-update; return empresa with `servicios` |
| `lex-control-admin/src/app/(dashboard)/empresas/page.tsx` | Modified | Services section in the form; load catalog + existing assignments; send `servicios[]` |
| `lex-control-api/tests/empresas.test.ts` | Modified | Cover assignment create/reconcile/defaults/validation |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Partial write (empresa created, assignments fail) | Med | Wrap create + assignments in a single `prisma.$transaction` |
| Invalid `servicioId` causes opaque FK error | Med | Validate ids against catalog up front → 400 with a clear message |
| Reconcile accidentally deletes assignments when field omitted | Med | Only reconcile when `servicios` is present in the body; absence = leave untouched |
| Decimal precision drift (string vs number) | Low | Accept numbers, let Prisma store `Decimal(10,2)`; UI parses the serialized strings |

## Rollback Plan
Purely additive. The `servicios` field is optional on both endpoints — omitting it preserves the
prior behavior exactly. Revert by removing the field from the schemas, the assignment logic from
the router, and the services section from the form. No DB schema change (the `EmpresaServicio`
model already exists and is pushed).

## Dependencies
- Existing `EmpresaServicio` model (already in `schema.prisma`, pushed to MySQL).
- `service-management` (`GET /servicios`) and the empresa CRUD from `api-foundation`.

## Success Criteria
- [ ] `POST /empresas` with a `servicios[]` creates the empresa and its assignments atomically.
- [ ] `PATCH /empresas/:id` with a `servicios[]` reconciles assignments (add/update/remove).
- [ ] Omitted price fields default to the catalog `Servicio` values; provided values override.
- [ ] An unknown `servicioId` yields 400 and no partial write.
- [ ] The admin form assigns services with editable, catalog-pre-filled prices on create and edit.
