# Tasks: Rename role CLIENTE → USUARIO

## Batch 1 — Schema + DB
- [x] 1.1 `schema.prisma`: `enum Rol { ADMIN USUARIO }` + `Usuario.rol @default(USUARIO)`
- [x] 1.2 `prisma db push --accept-data-loss` (0 rows used CLIENTE) + `prisma generate`

## Batch 2 — Backend
- [x] 2.1 `usuarios.router.ts`: default `rol: "USUARIO"`
- [x] 2.2 `usuarios.schemas.ts`: `z.enum(["ADMIN","USUARIO"])` (create + update)
- [x] 2.3 `mi-empresa.router.ts`: `requireRole(Rol.USUARIO)` (+ comments)
- [x] 2.4 `auth.schemas.ts`: comment updated (audience uses `z.nativeEnum(Rol)` — auto)

## Batch 3 — Tests
- [x] 3.1 5 test suites: role/audience literals `CLIENTE → USUARIO`
- [x] 3.2 `pnpm test` → 51 passing; `tsc --noEmit` clean

## Batch 4 — Frontend
- [x] 4.1 Admin `usuarios/page.tsx`: form rework — "Acceso" select Usuario/Administrador → `esAdminEmpresa`; drop ADMIN option + checkbox; "Acceso" column
- [x] 4.2 Client `login/page.tsx`: `audience: "USUARIO"`
- [x] 4.3 Admin + client `tsc --noEmit` clean

## Batch 5 — Verify + Docs
- [x] 5.1 Live smoke vs running API: create→USUARIO, login USUARIO→200/ADMIN→401, /mi-empresa→200
- [x] 5.2 OpenSpec (non-archived) swept CLIENTE → USUARIO; archived changes left as history
