# Public Landing Specification

> New capability introduced by change `client-landing-page`. The public marketing homepage of the
> client portal at `/`, replacing login-as-first-screen. Presentation + routing only; consumes the
> `public-marketing-api`. Tono: SaaS legal moderno (índigo de marca, Geist, claro/oscuro).

## ADDED Requirements

### Requirement: Public landing at the root, dashboard home moved to /inicio
The route `/` MUST render the PUBLIC landing (no sidebar, no auth required), using the root layout.
The dashboard home that lived at `/` MUST move to `/inicio`; all other dashboard routes (`/procesos`,
`/clientes`, `/contable`, …) are UNCHANGED. Login success and the sidebar "Inicio" link MUST point to
`/inicio`; the dashboard session guard MUST redirect unauthenticated users to `/login` (not loop on
`/`). `/login` and `/activar` are unchanged.

#### Scenario: Anonymous visitor sees the landing
- GIVEN a visitor with no session
- WHEN they open `/`
- THEN the public landing renders (no sidebar) and no redirect to `/login` happens

#### Scenario: Login lands in the portal home
- GIVEN a user logs in at `/login`
- WHEN authentication succeeds
- THEN they are redirected to `/inicio` (the dashboard home), with the sidebar shell

#### Scenario: Authenticated visitor on the landing can jump to the portal
- GIVEN a user WITH a session opens `/`
- WHEN the landing renders
- THEN it offers a clear "Ir a mi portal" action to `/inicio`

### Requirement: Landing sections
The landing MUST present, in order: (1) a public header (LEX Control logo + "Ingresar"); (2) a hero
with the value proposition and two CTAs — "Ingresar" → `/login` and "Solicitar demo" → the demo form;
(3) a modules grid (Procesos & Derecho de Petición, CRM Comercial, Contable, Contratos, Facturación,
Agenda, Consulta judicial); (4) a "Cómo funciona / Beneficios" block (deadline-first, multi-rol por
despacho, todo en un lugar, datos del juzgado al día); (5) a Planes section fed by `GET /publico/planes`;
(6) a final CTA + footer. It MUST be responsive (mobile-first) and honor the existing light/dark theme.

#### Scenario: Modules are shown
- GIVEN the landing renders
- WHEN the modules section is read
- THEN it lists the platform modules as cards with a short description each

#### Scenario: Plans come from the API
- GIVEN active plans exist
- WHEN the Planes section renders
- THEN it shows one card per active plan (nombre, precioMensual, módulos/cupos) sourced from `GET /publico/planes`

#### Scenario: Plans section degrades gracefully
- GIVEN `GET /publico/planes` fails or returns empty
- WHEN the Planes section renders
- THEN it shows a neutral fallback (e.g. "Escríbenos por un plan a tu medida") instead of a broken UI

### Requirement: Create-account form (despacho + admin + plan)
The landing MUST include a "Crea tu cuenta" form (section `#cuenta`) grouped in two fieldsets —
**Datos del despacho** (nombre del despacho [req], NIT, correo de la empresa, teléfono de la empresa)
and **Usuario administrador** (nombre [req], correo [req, será su login], celular) — plus a **Plan de
interés** selector populated from `GET /publico/planes`, and a hidden honeypot. It POSTs to
`/publico/solicitud-cuenta`. The plan cards' "Quiero este plan" button MUST pre-select that plan and
scroll to the form. On success it MUST show a confirmation explaining the request will be reviewed and
the account activated (pending approval); on validation error it MUST show the message without
clearing inputs; it MUST NOT block the page on failure. The hero/header CTAs point to `#cuenta`
("Crear cuenta") and `/login` ("Ingresar"); a "¿Ya tienes cuenta? Ingresar" link sits under the form.

#### Scenario: Successful account request
- GIVEN a visitor fills the form with despacho + admin data and picks a plan
- WHEN they submit
- THEN they see a "solicitud recibida, la revisaremos y activaremos tu cuenta" confirmation and a pending `Prospecto` (canal WEB) is captured with the chosen plan

#### Scenario: Picking a plan from a card pre-fills the form
- GIVEN the Planes section is rendered
- WHEN the visitor clicks "Quiero este plan" on a plan card
- THEN the page scrolls to the form and the Plan selector is pre-set to that plan

#### Scenario: Validation feedback
- GIVEN the admin email is malformed
- WHEN the form is submitted
- THEN the form shows the validation message and does not clear the inputs
