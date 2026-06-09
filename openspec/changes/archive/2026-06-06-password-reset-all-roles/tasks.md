# Tasks: Password reset for all roles

## Batch 1 — API
- [x] 1.1 `config/env.ts`: add `adminUrl` from `ADMIN_URL` (default `http://localhost:3000`)
- [x] 1.2 `usuarios.router.ts`: `activationUrl(raw, rol)` → `ADMIN → adminUrl`, else `clientUrl`
- [x] 1.3 `usuarios.router.ts` create: build link with `user.rol`
- [x] 1.4 `usuarios.router.ts` reset-password: `update(... select: { rol })` then build link with the target's rol

## Batch 2 — Admin UI
- [x] 2.1 `lex-control-admin/src/app/activar/page.tsx` (public): Suspense-wrapped `useSearchParams`, password + confirm, `POST /auth/set-password`, success → "Ir al panel" (`/login`), invalid/missing token handled

## Batch 3 — Tests / Verify
- [x] 3.1 `tests/usuarios.test.ts`: reset → USUARIO link host `:3001`, ADMIN link host `:3000`
- [x] 3.2 `pnpm test` 57 passing; API + admin `tsc --noEmit` clean
- [x] 3.3 Live smoke: reset of a USUARIO returns a `localhost:3001/activar?token=…` link

## Out of scope (future)
- [ ] Automatic link delivery by **email** (recommended next), then WhatsApp/SMS (needs a phone field + provider)
- [ ] `.env`/`.env.example`: add `ADMIN_URL` (user action — `.env*` write-denied to the assistant)
