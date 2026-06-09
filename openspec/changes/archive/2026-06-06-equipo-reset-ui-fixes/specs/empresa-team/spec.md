# Empresa Team Management — delta (change `equipo-reset-ui-fixes`)

> Frontend-only delta. The API requirement "Resend Activation Link" is unchanged; this adds the
> client-portal UI expectation that the same capability is exposed as a password reset for
> already-activated members, and that confirmations use an in-app modal.

## ADDED Requirements

### Requirement: Reset Member Password from the Portal
The Equipo screen MUST let an empresa admin reset the password of an **already-activated**
teammate by regenerating their activation link (reusing `POST /mi-empresa/usuarios/:id/activation`),
in addition to resending the link to a `PENDIENTE` member. The admin MUST NOT be offered this
action on their own account.

#### Scenario: Reset shown for an activated teammate
- GIVEN an empresa admin viewing the Equipo list
- AND a teammate whose `estado` is ACTIVO or INACTIVO (already set a password)
- WHEN the admin opens the row actions
- THEN a "Restablecer contraseña" action is available
- AND confirming it regenerates the activation link and revokes the teammate's live session
- AND the fresh link is shown for the admin to share manually

#### Scenario: Pending member still shows resend, not reset
- GIVEN a teammate whose `estado` is PENDIENTE (never activated)
- WHEN the admin opens the row actions
- THEN the action shown is "Reenviar enlace" (not "Restablecer contraseña")

#### Scenario: No reset on self
- GIVEN an empresa admin viewing their own row in the list
- WHEN they open the row actions
- THEN no "Restablecer contraseña" action is offered for their own account

### Requirement: In-App Confirmation Modals
Destructive or session-revoking actions on the Equipo screen (deactivate, resend link, reset
password) MUST be confirmed with the portal's in-app `ConfirmDialog` modal rather than the
browser's native `window.confirm`. Activating a member (non-destructive) MAY proceed without a
confirmation.

#### Scenario: Deactivate asks via modal
- GIVEN an empresa admin
- WHEN they click "Desactivar" on a teammate
- THEN an in-app modal asks for confirmation (styled as destructive)
- AND the action runs only after confirming
