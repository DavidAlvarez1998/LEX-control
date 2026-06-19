# compliance-habeas-data

Colombian personal-data protection capability (Ley 1581/2012, Decreto 1377/2013) for the
multi-tenant platform. Covers versioned legal documents, terms acceptance, data-subject
authorization (with the platform-as-Responsable / despacho-as-Encargado split), and the exercise
of data-subject rights with statutory deadlines.

## ADDED Requirements

### Requirement: Versioned legal documents
The platform SHALL store legal documents (Política de Tratamiento de Datos, Aviso de Privacidad,
Términos y Condiciones, DPA) as **immutable, versioned** records, and SHALL expose the current
version publicly. A published version MUST NOT be edited in place; a change MUST create a new
version.

#### Scenario: Serving the current policy publicly
- **GIVEN** a published `DocumentoLegal` of tipo `POLITICA_TRATAMIENTO` version 2 with `vigenteDesde` in the past
- **WHEN** an unauthenticated client calls `GET /publico/legal/politica-tratamiento`
- **THEN** the API returns version 2 content with HTTP 200
- **AND** the response is rate-limited like other `/publico` routes

#### Scenario: Published versions are immutable
- **GIVEN** an ADMIN editing legal documents
- **WHEN** they attempt to modify the content of an already-published version
- **THEN** the API responds 409 and instructs to publish a new version
- **AND** publishing a new version increments `version` and keeps the prior version retrievable at `GET /publico/legal/:tipo/:version`

#### Scenario: Only ADMIN publishes
- **GIVEN** a non-ADMIN (or tenant) user
- **WHEN** they call `POST /legal/documentos`
- **THEN** the API responds 403

### Requirement: Terms acceptance gate
Every despacho user MUST accept the current Términos and Política before using the application, and
MUST be prompted to re-accept when a version flagged `requiereReaceptacion` is published. Each
acceptance MUST be stored as evidence (exact version, timestamp, IP).

#### Scenario: Accepting at activation
- **GIVEN** a user setting their password via the activation link
- **WHEN** they submit without checking "Acepto los Términos y la Política de Tratamiento de Datos" (a required field marked with `*`)
- **THEN** the client blocks the request and shows the missing acceptance
- **AND** when they accept and submit, an `AceptacionLegal` row is created for each current document version with `fecha` and `ip`

#### Scenario: Re-acceptance after a new version
- **GIVEN** a user who accepted Política version 1
- **AND** Política version 2 was published with `requiereReaceptacion = true`
- **WHEN** the user logs in and `GET /auth/me` is read
- **THEN** the response includes `aceptacionPendiente` listing the new version
- **AND** the portal shows a blocking prompt until the user accepts

### Requirement: Data-subject authorization
The platform MUST record the **previous, express and informed** authorization of a data subject
(Ley 1581 art. 9). For data where the platform is Responsable (`USUARIO`, `PROSPECTO`) the
platform records it; for tenant data (`CLIENTE`, `LITIGANTE`) the despacho records it through the
forms, with the platform acting as Encargado. Authorization over sensitive data MUST be marked and
captured explicitly.

#### Scenario: Despacho captures a client's authorization
- **GIVEN** a JURIDICO/COMERCIAL user creating a `Cliente`
- **WHEN** they save with "¿El titular autorizó el tratamiento de sus datos?" = Sí, a `canal` and a `fecha`
- **THEN** an `AutorizacionTratamiento` row is created with `titularTipo=CLIENTE`, the tenant `empresaId`, `otorgada=true`, `politicaVersion`, and `registradoPorId = current user`
- **AND** the `Cliente.autorizacionTratamiento` convenience field reflects it

#### Scenario: Sensitive data requires explicit consent
- **GIVEN** an authorization that `incluyeDatosSensibles = true` (e.g., judicial process data)
- **WHEN** it is recorded
- **THEN** `otorgada` MUST be explicitly true and the purposes (`finalidades`) MUST be non-empty
- **AND** authorizations without explicit consent for sensitive data are rejected with 400

#### Scenario: Revoking authorization
- **GIVEN** an existing `AutorizacionTratamiento` with `otorgada=true`
- **WHEN** the subject revokes it (via a `REVOCACION` request that is resolved)
- **THEN** `revocada=true` and `fechaRevocacion` are set
- **AND** the prior authorization remains in the record as historical evidence (not deleted)

### Requirement: Data-subject rights with statutory deadlines
The platform MUST let a data subject exercise consulta, reclamo, rectificación, actualización,
supresión and revocación, route each request to the correct Responsable (the tenant, or the
platform), and track the **legal deadline** in business days.

#### Scenario: Deadline for a consulta
- **GIVEN** a `SolicitudTitular` of tipo `CONSULTA` received on a given business day
- **WHEN** it is created
- **THEN** `fechaLimite` is 10 business days later (Colombian holidays via the existing días-hábiles engine)
- **AND** a `RECLAMO` instead yields 15 business days

#### Scenario: Routing and inbox
- **GIVEN** a request whose `empresaId` is a tenant
- **THEN** it appears in that despacho's Habeas-Data inbox and is invisible to other tenants
- **AND** a request with `empresaId = null` appears only in the platform ADMIN inbox

#### Scenario: Overdue tracking
- **GIVEN** open `SolicitudTitular` rows
- **WHEN** `GET /cumplimiento/solicitudes/vencimientos` is called
- **THEN** they are grouped vencido / por_vencer / al_dia using the shared semáforo

#### Scenario: Public intake by a non-user
- **GIVEN** a data subject who is not a platform user
- **WHEN** they submit `POST /publico/legal/solicitud` with their identity, the target Responsable and a description
- **THEN** a `SolicitudTitular` is created in `RECIBIDA` and the deadline starts
- **AND** the endpoint is rate-limited

### Requirement: Data export and deletion
A tenant MUST be able to export its personal data, and personal data MUST be deletable on request
or at end of service, unless a legal retention duty applies.

#### Scenario: Tenant data export
- **GIVEN** an empresa-admin user
- **WHEN** they call `GET /mi-empresa/exportar-datos`
- **THEN** the API returns a machine-readable dump of that tenant's personal data only (scoped by `empresaId`)

#### Scenario: Suppression honored unless retention applies
- **GIVEN** a resolved `SUPRESION` request for a subject
- **WHEN** there is no active legal duty to retain (e.g., no in-flight judicial process referencing them)
- **THEN** the subject's personal data is deleted and the action is logged
- **AND** if a retention duty applies, the request is answered explaining the legal basis instead of deleting
