# Tasks: Empresa-Active Login Block

## Phase 1: Backend enforcement

- [x] 1.1 `auth.router.ts`: extend the login `include` to `empresa: { select: { nombre: true,
      activo: true } }`; after the existing account-state checks, `throw invalidas` when
      `usuario.empresa && !usuario.empresa.activo`.
- [x] 1.2 `middleware/auth.ts` `requireAuth`: add `empresa: { select: { activo: true } }` to the
      user `select`; add `(user.empresa && !user.empresa.activo)` to the 401 revoke condition.

## Phase 2: Admin form alert

- [x] 2.1 `empresas/page.tsx` `guardar()`: when editing and the original empresa was `activo` and
      the form sets it inactive, `await confirm({...danger})` warning that all users will be
      blocked; `return` (abort) if cancelled — before `setSaving(true)`.
- [x] 2.2 `empresas/page.tsx` form: inline amber warning under the "Activa" checkbox while it is
      unchecked.

## Phase 3: Tests / Verify

- [x] 3.1 `tests/auth.test.ts`: login 401 when `empresa.activo = false`; ADMIN (no empresa) still
      200; user of an active empresa still 200.
- [x] 3.2 `tests/session-revocation.test.ts`: middleware 401 when the authenticated user's
      `empresa.activo = false`.
- [x] 3.3 `pnpm --dir lex-control-api test` passes; `pnpm --dir lex-control-admin` tsc clean.
