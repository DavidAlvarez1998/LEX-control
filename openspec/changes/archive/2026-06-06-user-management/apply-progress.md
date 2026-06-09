# Apply Progress: User Management + Activation Link

**Mode**: Standard (no TDD; tests written alongside implementation)

## Batch 1 — Backend (API) — DONE
- `prisma/schema.prisma`: `Usuario.activationToken String? @unique` + `activationExpires DateTime?` (pushed + generated).
- `config/env.ts`: `clientUrl` from `CLIENT_URL` (default `http://localhost:3001`).
- `auth.service.ts`: `generateActivationToken()` (raw + sha256) + `hashActivationToken(raw)`.
- `modules/usuarios/{usuarios.router,usuarios.schemas}.ts`: GET list (`?empresaId`, derived estado, no token leak), POST create (→ activationUrl, P2002→409, P2003→400), PATCH (P2025→404), POST `/:id/reset-password`; all `requireRole(ADMIN)`.
- `auth.router.ts` + `auth.schemas.ts`: `POST /auth/set-password` (public) — sha256 lookup, expiry check, bcrypt password, clears token, sets `activo`.
- `app.ts`: mounts `/usuarios`.

## Batch 1 (cont.) — Tests (task 1.8) — DONE
- `tests/usuarios.test.ts` (13 tests): list guards + estado derivation + no `activationToken` leak; create 403/400/201(+link)/409/400; patch 200/404; reset 200(+link)/404/403.
- `tests/auth.test.ts` set-password block (5 tests): 400 missing token, 400 weak password, 400 invalid token, 400 expired, 200 happy (asserts `activationToken: null`, `activo: true`).

## Batch 2 — Admin UI — DONE
- `lex-control-admin/src/app/(dashboard)/usuarios/page.tsx`: wired to the HTTP API (mirrors the empresas page conventions).
  - List with empresa name, rol chip, estado badge (ACTIVO/PENDIENTE/INACTIVO).
  - Create modal: email, nombre, empresa `<select>` from `GET /empresas`, rol, esAdminEmpresa → `POST /usuarios`; on success opens the activation-link modal.
  - Edit modal: nombre, rol, esAdminEmpresa, activo → `PATCH /usuarios/:id` (email + empresa locked on edit).
  - Row actions: Restablecer (`POST reset-password` → link modal), Desactivar/Activar (`PATCH activo`).
  - Activation-link modal with copy-to-clipboard (reused for create + reset).

## Batch 3 — Client activation page — DONE
- `lex-control-client/src/lib/api.ts`: `setPassword(token, password)` with AbortController timeout + `ApiError`.
- `lex-control-client/src/app/activar/page.tsx` (public, outside `(dashboard)`): Suspense-wrapped `useSearchParams`, password + confirm (min 8, must match), `POST /auth/set-password`; success state → "Ir al portal"; missing/invalid/expired token → clear message.

## Verification
- `pnpm test` (API): **45 passing** across 4 suites.
- `tsc --noEmit`: admin clean, client clean.
- `pnpm build` (API): clean.

## Deviations from Design
- Client `Button` primitive lacks `onClick`/`disabled`, so the activation form uses native `<button>`/`<Link>` styled to match. No shared component modified.

## Remaining
- Manual e2e (user): `pnpm seed:admin` → log in to admin → create user → open the link in the client `/activar` → set password → confirm login. Needs the full stack running and a real ADMIN row.
- Optional: automatic email delivery of the link (explicitly out of scope for this change).
