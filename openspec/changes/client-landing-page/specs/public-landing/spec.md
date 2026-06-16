# Public Landing · spec (new capability)

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

### Requirement: Demo request form
The landing MUST include a "Solicitar demo" form (nombre del despacho, nombre de contacto, email,
teléfono opcional, mensaje opcional) that POSTs to `/publico/solicitar-demo`, including a hidden
honeypot field. On success it MUST show a confirmation ("Gracias, te contactaremos"); on validation
error it MUST show the field message; it MUST NOT block the page on failure.

#### Scenario: Successful demo request
- GIVEN a visitor fills the demo form with valid data
- WHEN they submit
- THEN they see a success confirmation and the lead is captured (a `Prospecto` canal WEB)

#### Scenario: Validation feedback
- GIVEN the email is malformed
- WHEN the form is submitted
- THEN the form shows the validation message and does not clear the inputs
