# Tasks: Team password reset + UI fixes

## Batch 1 — Client portal: Equipo
- [x] 1.1 Add "Restablecer contraseña" action for activated members (calls `POST /mi-empresa/usuarios/:id/activation`); show "Reenviar enlace" only for PENDIENTE; exclude self
- [x] 1.2 Replace all `window.confirm` with `ConfirmDialog`: add `confirm` state + `ejecutarConfirm` executor; deactivate is the only destructive (red) confirm; activate stays immediate

## Batch 2 — Admin portal: Usuarios edit modal
- [x] 2.1 Add `bg-white dark:bg-slate-900` + `text-slate-800 dark:text-slate-100` and `dark:disabled:*` variants to the disabled Correo input and Empresa select

## Batch 3 — Admin portal: Catálogo de procesos
- [x] 3.1 Remove `flex-wrap` from the type card; add `shrink-0` to the action button group so Editar/Eliminar stay right-aligned with long names

## Verify
- [x] `tsc --noEmit` clean for client + admin; no new lint errors from touched code
- [ ] Manual smoke in dark mode + with a long process-type name (pending user check in the browser)
