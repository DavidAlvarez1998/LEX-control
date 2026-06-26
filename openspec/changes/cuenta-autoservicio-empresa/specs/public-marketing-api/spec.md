# Public Marketing API Specification (delta)

> El change `cuenta-autoservicio-empresa` **reemplaza el comportamiento** de
> `POST /publico/solicitud-cuenta`: de "crear un Prospecto pendiente de aprobación" pasa a
> **aprovisionar el tenant completo** (Empresa + Suscripción trial + Usuario administrador) y
> enviar el correo de activación. El catálogo público de planes (`GET /publico/planes`) no cambia.

## MODIFIED Requirements

### Requirement: Public account-request capture (hybrid, pending approval)

**Reemplazada por →**

### Requirement: Public self-service account provisioning
El sistema MUST exponer `POST /publico/solicitud-cuenta` SIN autenticación que, a partir de un body
validado `{ nombreEmpresa, nit, tarjeta?, email, telefono, nombreContacto, website? }` (zod:
requeridos `nombreEmpresa`, `nit`, `email` válido, `telefono`, `nombreContacto`; `tarjeta` opcional;
longitudes acotadas), **aprovisiona el tenant completo en una transacción**:

- una **Empresa** `activo = true` con `nombre = nombreEmpresa`, `rfc = nit`, `email = email`;
- una **Suscripción** `estado = ACTIVA` al **plan trial por defecto** (resuelto server-side por la
  clave de configuración `PLAN_AUTOSERVICIO_CLAVE`); si la clave no resuelve a un Plan activo, la
  empresa se crea **sin** suscripción y el caso se loggea (degradación, no se bloquea el alta);
- un **Usuario** administrador de esa empresa: `rol = USUARIO`, `esAdminEmpresa = true`,
  `empresaId = empresa.id`, `nombre = nombreContacto`, `email`, `telefono`,
  `tarjetaProfesional = tarjeta`, contraseña placeholder, **`activo = false`** y un token de
  activación (hash SHA-256 almacenado, expira en 48 h), más un `UsuarioRolEmpresa` `ADMINISTRADOR`;
- un **Prospecto** `canalEntrada = WEB`, `estado = GANADO`, `comercialId = null`,
  `empresaId = empresa.id`, `planVendidoId = plan?.id`, `fechaCierre = now`, con los datos del alta
  (sin crear Comisión) — solo para métricas/funnel del alta web.

Tras la transacción (best-effort, fuera de ella) MUST enviar el **correo de invitación** vía SES con
el `activationUrl` al portal cliente (`/activar?token=…`); el fallo del correo NO revierte el alta ni
se filtra al visitante. MUST incluir el honeypot `website` (no vacío → 200 no-op, no crea nada). MUST
rechazar con **409** si el `email` ya pertenece a un Usuario o el `nit` ya pertenece a una Empresa
(`rfc @unique`), con mensaje claro. MUST NOT aceptar del cliente `estado`, `empresaId`, `rol`,
`activo` ni `planId` (el plan lo decide el servidor). MUST NOT exponer errores internos.

#### Scenario: Un visitante crea su despacho (alta feliz)
- **GIVEN** un body válido (`nombreEmpresa`, `nit`, `email`, `telefono`, `nombreContacto`) y honeypot vacío
- **WHEN** se llama `POST /publico/solicitud-cuenta`
- **THEN** se crea una Empresa `activo=true`, una Suscripción ACTIVA al plan trial, un Usuario
  `esAdminEmpresa=true` con `activo=false` y token de activación + rol `ADMINISTRADOR`, y un
  Prospecto `estado=GANADO` ligado a la empresa
- **AND** se intenta enviar el correo de activación al `email`
- **AND** la respuesta es 201 `{ ok: true }`

#### Scenario: Activación posterior habilita la cuenta
- **GIVEN** un alta recién creada con el usuario `activo=false`
- **WHEN** el usuario abre el `activationUrl` y completa `setPassword`
- **THEN** su contraseña queda en bcrypt, `activo=true`, el token se limpia y `tokenVersion` se
  incrementa, y puede entrar como ADMINISTRADOR de su empresa

#### Scenario: Correo ya registrado
- **GIVEN** un `email` que ya pertenece a un Usuario
- **WHEN** se llama el endpoint
- **THEN** se rechaza con 409 ("ya existe una cuenta con ese correo") y no se crea Empresa ni Usuario

#### Scenario: NIT ya registrado
- **GIVEN** un `nit` que ya pertenece a una Empresa (`rfc`)
- **WHEN** se llama el endpoint
- **THEN** se rechaza con 409 ("ya existe una empresa con ese NIT/CC") y no se crea nada

#### Scenario: Plan trial inexistente (degradación)
- **GIVEN** `PLAN_AUTOSERVICIO_CLAVE` no resuelve a ningún Plan activo
- **WHEN** se procesa un alta válida
- **THEN** la Empresa y el Usuario se crean igual, **sin** Suscripción, y el caso se loggea (201)

#### Scenario: Honeypot deflecta bots
- **GIVEN** un body con el honeypot `website` no vacío
- **WHEN** se llama el endpoint
- **THEN** no se crea nada y la respuesta es un 200 benigno

#### Scenario: Payload inválido
- **GIVEN** un body con `email` malformado o sin `nombreContacto`/`nit`/`telefono`
- **WHEN** se llama el endpoint
- **THEN** se rechaza 400 (zod) y no se crea nada

#### Scenario: El cliente no puede inyectar estado/rol/empresa/plan
- **GIVEN** un body que además trae `estado`, `empresaId`, `rol`, `activo` o `planId`
- **WHEN** se procesa el alta
- **THEN** esos campos se ignoran; el plan es el trial server-side, el usuario nace `USUARIO`
  `activo=false`, y el Prospecto nace `GANADO` ligado a la empresa creada
