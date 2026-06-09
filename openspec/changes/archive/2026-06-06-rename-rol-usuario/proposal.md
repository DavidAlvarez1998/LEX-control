# Proposal: Rename role CLIENTE → USUARIO

## Intent
The `Rol` enum value `CLIENTE` actually means "a person who belongs to a company", not a
business client. The name collides with the future concept of an empresa's own clients.
Rename `Rol.CLIENTE → Rol.USUARIO` while the cost is near zero (0 rows in the DB use it),
freeing the word "Cliente" for a future business entity.

## Scope

### In Scope
- `schema.prisma`: `enum Rol { ADMIN USUARIO }` + `Usuario.rol @default(USUARIO)`; `prisma db push`.
- Backend: all `Rol.CLIENTE` / `"CLIENTE"` literals → `USUARIO` (router defaults, zod enums, requireRole, comments).
- Admin UI: rework the "Nuevo usuario" form — within a company a person is **Usuario** or
  **Administrador** (maps to `esAdminEmpresa`); drop the platform `ADMIN` option and the
  separate checkbox. List shows an "Acceso" column.
- Client UI: login `audience: "USUARIO"`.
- Tests + OpenSpec artifacts (non-archived) updated.

### Out of Scope
- Introducing the future `Cliente` business entity (the empresa's own customers).

## Capabilities
### Modified Capabilities
- `authentication`: role value `CLIENTE` becomes `USUARIO` (token, audience, guards).
- `client-portal-data` / `user-management`: same rename across contracts.

## Approach
Mechanical rename, smallest-blast-radius timing. `esAdminEmpresa` is unchanged and now
carries the "admin of their own company" meaning in the UI (the old role dropdown +
checkbox are merged into one "Acceso" selector). Platform `ADMIN` users are created via
`seed:admin`, not this form, so `ADMIN` is removed from the company-user form.

## Affected Areas
| Area | Impact |
|------|--------|
| `lex-control-api/prisma/schema.prisma` | enum + default + db push |
| `lex-control-api/src/modules/{usuarios,auth,mi-empresa}/*` | literals/guards → USUARIO |
| `lex-control-api/tests/*` | role/audience literals → USUARIO |
| `lex-control-admin/.../usuarios/page.tsx` | form rework (Usuario/Administrador), Acceso column |
| `lex-control-client/.../login/page.tsx` | `audience: "USUARIO"` |
| `openspec/**` (non-archived) | CLIENTE → USUARIO |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Enum alter on a live column | Low | 0 rows used `CLIENTE`; only the ADMIN row exists, cast ADMIN→ADMIN is a no-op |
| Stale JWTs holding `CLIENTE` | Low | Tokens are short-lived (1d), dev only |

## Rollback Plan
Revert the enum + literals and `db push` back. No data depends on the value.

## Success Criteria
- [x] New users get `rol = USUARIO`; login `audience: "USUARIO"` works, `ADMIN` mismatch → 401.
- [x] `GET /mi-empresa` (USUARIO) → 200. 51 tests pass; API + both fronts tsc clean.
- [x] Admin form shows **Usuario / Administrador**; no `CLIENTE` left outside `/archive/`.
