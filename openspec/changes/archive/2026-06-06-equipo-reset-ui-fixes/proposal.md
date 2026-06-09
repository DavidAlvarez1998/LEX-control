# Proposal: Team password reset + UI fixes (frontend only)

## Intent
A handful of frontend-only fixes across the admin and client portals. No API, schema, or
backend behavior changes — every endpoint used here already existed.

## Scope

### In Scope
- **Client portal — Equipo screen**: an empresa admin can now **reset the password of an
  already-activated** teammate (not just resend the link to PENDIENTE users). It reuses the
  existing `POST /mi-empresa/usuarios/:id/activation` endpoint (which already regenerates the
  activation link and revokes the live session), mirroring the admin "Restablecer contraseña".
- **Client portal — Equipo screen**: replace the browser `window.confirm` dialogs with the
  in-app `ConfirmDialog` modal (consistent with the `clientes` screen).
- **Admin portal — Usuarios edit modal**: fix dark-mode contrast — the disabled **Correo** and
  **Empresa** fields rendered with a white background in dark theme.
- **Admin portal — Catálogo de procesos**: fix card layout so the **Editar / Eliminar** buttons
  stay aligned on the right even when a process-type name is long (they used to wrap below).

### Out of Scope
- Automatic delivery of the activation link (email / WhatsApp). The admin still copies the link
  from the modal and shares it manually — unchanged.
- Any backend / API / Prisma change.

## Approach
- **Reset password (equipo)**: the gap was purely UI — the table only offered "Reenviar enlace"
  for `PENDIENTE` members. Added a "Restablecer contraseña" action for activated members
  (excluding self, so an admin can't kill their own session), hitting the same `/activation`
  endpoint and opening the existing activation-link modal.
- **Modal confirmations**: introduced a `confirm` state + `ConfirmDialog` (same pattern as
  `clientes/page.tsx`); the action handlers now throw on error and a single executor catches it.
- **Dark-mode contrast**: added `dark:` variants for the disabled input/select background and text.
- **Catálogo layout**: removed `flex-wrap` from the card and added `shrink-0` to the button group.

## Affected Areas
| Area | Impact |
|------|--------|
| `lex-control-client/src/app/(dashboard)/equipo/page.tsx` | Reset-password action + `ConfirmDialog` modals |
| `lex-control-admin/src/app/(dashboard)/usuarios/page.tsx` | Dark-mode contrast on disabled fields |
| `lex-control-admin/src/app/(dashboard)/catalogo-procesos/page.tsx` | Card layout: buttons stay on the right |

## Rollback Plan
All additive/visual. Revert the three files. No data or endpoint touched.

## Success Criteria
- [x] Empresa admin sees "Restablecer contraseña" for activated teammates; it regenerates the link
      and revokes their session.
- [x] Equipo screen uses portal modals (no `window.confirm`).
- [x] Admin Usuarios edit modal: Correo/Empresa fields readable in dark mode.
- [x] Catálogo de procesos: Editar/Eliminar stay right-aligned with long names.
- [x] `tsc --noEmit` clean for the touched apps.
