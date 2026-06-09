# Tasks: Assign Services + Per-Company Prices on Empresa

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 250–350 |
| 400-line budget risk | Low |
| Delivery strategy | single batch (interactive verify) |

### Suggested Work Units

| Unit | Goal | Notes |
|------|------|-------|
| 1 | Backend: schema + transactional create/reconcile | Independent; verify with build + tests |
| 2 | Admin form: services section wired to the API | Depends on Unit 1 contract |

## Phase 1: Backend — empresa assignments

- [x] 1.1 `empresas.schemas.ts`: add `servicioAsignadoSchema` (`servicioId` required; `precioBase`/`precioPorUnidad` non-negative numbers, `incluidos` non-negative int, `activo` boolean — all optional). Add optional `servicios` array to `createEmpresaSchema` (so `updateEmpresaSchema.partial()` inherits it). Reject duplicate `servicioId`s.
- [x] 1.2 `empresas.router.ts`: helper to load referenced catalog services, validate ids (400 on unknown), and build `EmpresaServicio` rows with catalog defaults for omitted fields.
- [x] 1.3 `empresas.router.ts` POST: when `servicios` present, create empresa + `createMany` assignments in one `$transaction`; return empresa including `servicios.servicio`.
- [x] 1.4 `empresas.router.ts` PATCH: when `servicios` present, reconcile in one `$transaction` (upsert listed by `(empresaId, servicioId)`, delete omitted); when absent, leave untouched. Return empresa including `servicios.servicio`.

## Phase 2: Admin form — services section

- [x] 2.1 Empresa page: on modal open, fetch `/servicios` (catalog). On edit, fetch `GET /empresas/:id` to load existing assignments.
- [x] 2.2 Form state: track selected services + per-service overrides (`precioBase`, `precioPorUnidad`, `incluidos`), pre-filled from catalog (or existing assignment when editing).
- [x] 2.3 Render a "Servicios contratados" section: checkbox per active catalog service; selecting reveals editable price inputs (hide `precioPorUnidad` when the service has no `unidad`).
- [x] 2.4 `guardar()`: build `servicios[]` from selected rows (numbers, not strings) and include it in the POST/PATCH payload. Keep existing required-field validation.

## Phase 3: Tests / Verify

- [x] 3.1 `tests/empresas.test.ts`: create with services → 201 + assignments; create with unknown id → 400 + not created; PATCH reconcile (add/update/remove); PATCH without field leaves assignments; defaults from catalog.
- [x] 3.2 `pnpm --dir lex-control-api build` compiles clean; `pnpm --dir lex-control-api test` passes.
- [ ] 3.3 Manual: admin create + edit empresa with services, verify prices persist and pre-fill.

## Phase 4: Empresas list — assigned services display (added)

- [x] 4.1 `empresas.router.ts` GET `/`: include ALL assigned services' names (`servicio.nombre`, ordered alphabetically) alongside `_count`.
- [x] 4.2 Admin empresas table: **removed the "Servicios" column**; under each empresa row a dashed divider + a small "Servicios" heading listing every assigned service as a chip (`Sin servicios asignados` when none). Defensive `(servicios ?? [])`; `servicios?` optional in the type.
- [x] 4.3 Verify: admin `tsc` clean; 56 tests pass; live `GET /empresas` returns all names (e.g. "Bufete Goodman" → 5 services).
