# Tasks

## Phase 1 — API (lawyer identity)

- [x] 1.1 `usuarios/usuarios.shared.ts`: add `cedula`, `tarjetaProfesional` to `PUBLIC_SELECT`.
- [x] 1.2 `usuarios/usuarios.schemas.ts`: add both (optional, trimmed) to create + update schemas.
- [x] 1.3 `usuarios/usuarios.service.ts` `createUsuario`: destructure + add both to `data`.
- [x] 1.4 `mi-empresa/mi-empresa.schemas.ts`: add both optional to `createMiembroSchema`.
- [x] 1.5 `mi-empresa/mi-empresa.service.ts` `createMiembro`: add both to the create payload.
- [x] 1.6 `pnpm build` (tsc) green.

## Phase 2 — Frontends (lawyer identity)

- [x] 2.1 Client `…/equipo/page.tsx`: FormState + EMPTY_FORM + 2 inputs after "Nombre" + create POST payload.
- [x] 2.2 Admin `…/usuarios/page.tsx`: FormState + EMPTY_FORM + `abrirEditar` prefill + 2 inputs (USUARIO branch) + create/edit payload + Usuario DTO type. Both fronts `tsc --noEmit` green.
- [ ] 2.3 Smoke (manual): create a lawyer with C.C. + tarjeta; confirm a generated poder shows them.

## Phase 3 — Representante legal in creation form

- [x] 3.1 `seed-tipos.json`: moved `repLegalNombre` + `repLegalDocumento` next to `fechaPoder`; removed `soloFicha`.
- [x] 3.2 Validated JSON; `pnpm seed:catalogo` applied (31 tipos; verified non-soloFicha, idx 11-12 after fechaPoder).
- [ ] 3.3 Smoke (manual): new mínima-cuantía proceso shows the two rep-legal fields in creation (near the poder) and in the ficha.

## Phase 4 — Close-out

- [ ] 4.1 Commit per repo (api + both fronts + root seed); bump submodule pointers.
- [ ] 4.2 Archive change into `openspec/specs/` once verified.
