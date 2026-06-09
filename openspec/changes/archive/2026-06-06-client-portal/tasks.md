# Tasks: Client Portal

## Review Workload Forecast
| Field | Value |
|-------|-------|
| Estimated changed lines | 250–350 |
| 400-line budget risk | Low |
| Suggested split | Single batch (additive, two small backend changes + client wiring) |
| Delivery strategy | single-pr (local repos, no PR flow) |

## Batch 1 — Backend
- [x] 1.1 `auth.schemas.ts`: add optional `audience: z.nativeEnum(Rol)` to `loginSchema`
- [x] 1.2 `auth.router.ts`: after password check, `if (audience && usuario.rol !== audience) throw 401` (generic)
- [x] 1.3 `modules/mi-empresa/mi-empresa.router.ts`: `GET /mi-empresa` — `requireRole(USUARIO)`, resolve empresa by token `sub`, include active `servicios` (+ nested `servicio`), 404 if none
- [x] 1.4 `app.ts`: mount `/mi-empresa`

## Batch 2 — Client UI
- [x] 2.1 `/login` page + `lib/auth.ts` (session, JWT expiry helpers) + `components/auth-guard.tsx` — sends `audience: "USUARIO"`
- [x] 2.2 `lib/api.ts`: shared client (get/post/patch/del) with Bearer + 401→/login + timeout
- [x] 2.3 `cuenta/page.tsx`: real profile (from session) + empresa + contracted-services table (GET /mi-empresa)
- [x] 2.4 `servicios/page.tsx`: real "Mis Servicios" table from `GET /mi-empresa`.servicios

## Batch 3 — Tests / Verify
- [x] 3.1 `tests/auth.test.ts`: audience match→200, mismatch→401
- [x] 3.2 `tests/mi-empresa.test.ts`: 401 (no token), 403 (ADMIN), 404 (no empresa), 200 (+ asserts lookup by token `sub`)
- [x] 3.3 Verify: `pnpm test` 51 passing; API + client `tsc --noEmit` clean
- [x] 3.4 Live smoke vs running API: ADMIN/USUARIO × ADMIN/USUARIO portals (200/401), `/mi-empresa` 200/403/401

## Batch 4 — Profile access level (added during testing)
- [x] 4.1 `auth.router.ts`: login response `user` now includes `esAdminEmpresa`
- [x] 4.2 `AuthUser` type (client + admin): add `esAdminEmpresa?: boolean`
- [x] 4.3 `cuenta/page.tsx`: show derived **Acceso** (Administrador / Usuario / Administrador de plataforma) instead of the raw `rol`
- [x] 4.4 Verify: API + client `tsc` clean; live login returns `esAdminEmpresa: true` for a company admin
- Note: existing sessions must re-login to pick up the new field (it is stored at login time).

## Out of scope
- [ ] **Assign services to a company** (so "Mis Servicios" shows data) — being handled in a separate/parallel workstream
- [ ] `facturacion` page: compute billing (precioBase + per-unit usage above `incluidos`)
- [ ] USUARIO self-administration of its company's users (`esAdminEmpresa` managing others)
- [ ] Password change/reset from inside the portal
