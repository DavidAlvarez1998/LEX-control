# Public Marketing API · spec (new capability)

> New capability introduced by change `client-landing-page`. Two UNAUTHENTICATED endpoints under
> `/publico` that feed the public landing: a read-only plan catalog and a demo-request lead capture.
> Everything else in the API stays authenticated; these are the only public surfaces.

## ADDED Requirements

### Requirement: Public read-only plan catalog
The system MUST expose `GET /publico/planes` WITHOUT authentication, returning only `activo = true`
plans ordered by `orden` asc, each as a MINIMAL projection: `{ clave, nombre, descripcion,
precioMensual, modulos: string[] (claves), cuotas: [{ rol, cantidad }] }`. It MUST NOT expose internal
ids, suscripciones, empresa data, or any field beyond the projection. It is read-only and has no
tenant scope (the plan catalog is global).

#### Scenario: Anonymous visitor reads the plans
- GIVEN no auth token
- WHEN `GET /publico/planes` is called
- THEN it returns 200 with the active plans (ordered by `orden`), each carrying only the minimal projection

#### Scenario: Inactive plans are hidden
- GIVEN a plan with `activo = false`
- WHEN the public catalog is read
- THEN that plan is NOT in the response

#### Scenario: No internal fields leak
- GIVEN the public catalog response
- WHEN a plan object is inspected
- THEN it has no `id`, no `suscripciones`, and no field outside `{clave, nombre, descripcion, precioMensual, modulos, cuotas}`

### Requirement: Public demo-request lead capture
The system MUST expose `POST /publico/solicitar-demo` WITHOUT authentication that creates a `Prospecto`
with `canalEntrada = WEB` and `estado = NUEVO` from a validated body `{ nombreEmpresa, nombreContacto,
email, telefono?, mensaje? }` (zod: required nombres, valid email, lengths bounded). The lead lands in
the platform's comercial funnel (`/prospectos`). The endpoint MUST include a honeypot field (e.g.
`website`) that, when filled, makes the request a silent no-op (200, no row) to deflect bots. It MUST
NOT echo internal errors and MUST NOT require or accept an `empresaId`/`estado` from the client.

#### Scenario: A visitor requests a demo
- GIVEN a valid body with `nombreEmpresa`, `nombreContacto`, `email`
- WHEN `POST /publico/solicitar-demo` is called (honeypot empty)
- THEN a `Prospecto` is created with `canalEntrada = WEB`, `estado = NUEVO`, and 201 is returned

#### Scenario: Honeypot deflects bots
- GIVEN a body whose honeypot field `website` is non-empty
- WHEN the endpoint is called
- THEN no `Prospecto` is created and the response is a benign 200 (bot sees success)

#### Scenario: Invalid payload rejected
- GIVEN a body with a malformed `email` or missing `nombreContacto`
- WHEN the endpoint is called
- THEN it is rejected 400 (zod) and no `Prospecto` is created

#### Scenario: Client cannot inject estado/empresa
- GIVEN a body that also sets `estado = GANADO` and `empresaId`
- WHEN the prospecto is created
- THEN those are ignored; the row is `estado = NUEVO` with no empresa link
