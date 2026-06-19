# Design — compliance-habeas-data

Architecture decisions for Colombian data-protection compliance (Ley 1581/2012, Decreto
1377/2013). Artifact language English; legal text placeholders to be lawyer-reviewed.

## D1 — Two controller roles (the decision that shapes everything)

LEX Control operates at two distinct legal capacities and the data model MUST reflect both:

| Data | Responsable (controller) | LEX Control role | What we build |
|---|---|---|---|
| `Usuario` (despacho staff), `Empresa` contact, sales `Prospecto` | **LEX Control** | Responsable | Policy + privacy notice + ToS + acceptance + authorization captured by us |
| `Cliente`, `Litigante`, parties in a `Proceso` | **The despacho (Empresa)** | **Encargado** (processor) | DPA in the contract + **tooling** so the despacho records its titulares' authorization and answers their rights |

Rationale: a law firm's clients did not give *us* their consent — they gave it to their lawyer.
Treating all data as "ours" would be legally wrong and would expose us. So consent for tenant
data is **captured by the despacho** through our forms, and we act on its behalf.

## D2 — Data model (Prisma)

New models (cuid IDs, snake_case `@@map`, `empresaId` scoping where tenant-bound):

- **`DocumentoLegal`** — versioned legal text.
  `tipo` (`POLITICA_TRATAMIENTO|AVISO_PRIVACIDAD|TERMINOS|DPA`), `version` (int, monotonic per
  tipo), `titulo`, `contenido` (markdown/HTML) or `url`, `vigenteDesde` (Date), `publicadoPorId`,
  `activo`. Unique `(tipo, version)`. The "current" doc per `tipo` = highest `version` with
  `vigenteDesde <= now` and `activo`. **Append-only**: a correction is a new version, never an
  in-place edit (evidence integrity).

- **`AceptacionLegal`** — a user accepting current ToS+Policy.
  `usuarioId`, `documentoLegalId` (the exact version accepted), `fecha`, `ip`, `userAgent`.
  One row per (usuario, documento version). Drives the "must re-accept" gate when a new version
  ships.

- **`AutorizacionTratamiento`** — a data subject's authorization (Ley 1581 art. 9: previa,
  expresa, informada). Polymorphic titular to cover the 4 populations:
  `titularTipo` (`USUARIO|CLIENTE|LITIGANTE|PROSPECTO`), `titularId`, `empresaId` (null =
  platform-level), `finalidades` (string[]/JSON — purposes), `canal`
  (`WEB|DOCUMENTO_FISICO|VERBAL|CORREO|OTRO`), `politicaVersion` (DocumentoLegal id),
  `otorgada` (bool), `fechaOtorgamiento`, `revocada` (bool), `fechaRevocacion`, `evidenciaUrl`
  (scanned paper / signed doc), `ip`, `userAgent`, `registradoPorId`. Sensitive-data flag
  `incluyeDatosSensibles` (judicial/financial → needs explicit, reinforced consent).

- **`SolicitudTitular`** — data subject request (PQR de Habeas Data).
  `tipo` (`CONSULTA|RECLAMO|RECTIFICACION|ACTUALIZACION|SUPRESION|REVOCACION`), `empresaId`
  (the responsible tenant; null = against the platform), `titularNombre`, `titularDocumento`,
  `titularCorreo`, `descripcion`, `estado` (`RECIBIDA|EN_TRAMITE|RESUELTA|RECHAZADA`),
  `fechaRecepcion`, `fechaLimite` (derived), `fechaRespuesta`, `respuesta`, `canalRespuesta`,
  `atendidoPorId`. Legal deadlines drive `fechaLimite` (see D5).

Optional consent fields added to **`Cliente`** and **`Litigante`** as a convenience denormalization
for the most common case (despacho capturing client consent inline), backed by an
`AutorizacionTratamiento` row: `autorizacionTratamiento` (bool), `autorizacionFecha`,
`autorizacionCanal`. Optional → backward compatible.

## D3 — Public legal documents

- API: `GET /publico/legal/:tipo` → current active `DocumentoLegal` of that tipo (no auth,
  rate-limited like the rest of `/publico`). `GET /publico/legal/:tipo/:version` for a specific
  historical version (auditability / linking from an acceptance record).
- Admin: `POST/PATCH /legal/documentos` (ADMIN only) to publish a new version. Editing a published
  version is forbidden (409) — publish a new one.
- Frontend: public routes in both portals (or the marketing site) `/legal/politica-tratamiento`,
  `/legal/aviso-privacidad`, `/legal/terminos`; footer links; rendered from the API content.

## D4 — Acceptance gate

- At **set-password / first login**, the activation screen shows the current ToS + Policy with a
  required checkbox (red `*`, validated on submit per repo form rule). On submit → create
  `AceptacionLegal` rows for the current versions.
- `GET /auth/me` (and the login payload) returns `aceptacionPendiente: { documentos: [...] }` when
  the user has not accepted the **current** versions (e.g., after we publish a new policy). The
  client shows a blocking modal until accepted. Rationale: consent must be re-collected when the
  policy materially changes.
- Platform `Usuario` authorization (we are Responsable) is recorded as an
  `AutorizacionTratamiento` (titularTipo=USUARIO, empresaId=null) at the same moment.

## D5 — Data subject rights (deadlines)

Legal terms (business days, Colombian holidays — reuse `diasHabiles.ts`):
- **Consulta**: 10 días hábiles; if not possible, inform + max **+5** días hábiles.
- **Reclamo**: 15 días hábiles from day after receipt; if not possible, inform + max **+8**.

`fechaLimite = addDiasHabiles(fechaRecepcion, tipo === CONSULTA ? 10 : 15)`. A `GET
/cumplimiento/solicitudes/vencimientos` returns overdue / due-soon with the same semáforo pattern
as `proceso-vencimientos`. Routing: a request against a tenant goes to that despacho's inbox;
against the platform, to the ADMIN inbox. Intake can be public (a titular who is not a user):
`POST /publico/legal/solicitud` (rate-limited, captcha later).

## D6 — Retention, export, deletion

- **Export**: `GET /mi-empresa/exportar-datos` (empresa admin) → machine-readable dump of the
  tenant's personal data (clientes/litigantes/procesos minimal PII) — supports the titular's right
  and portability.
- **Deletion / end of service**: deleting an `Empresa` already cascades to its `Usuario`/
  `EmpresaServicio`; extend the documented retention policy: on contract termination, tenant data
  is deleted after a defined grace period. `SUPRESION` requests are honored unless a legal duty to
  retain applies (e.g., active judicial process) — the response records the reason.
- Security measures (TLS in transit, access control via RBAC — already present; encryption at rest
  depends on the managed DB chosen at deploy) documented in the Política.

## D7 — Scope boundaries

- This change does **not** ship the final legal wording (lawyer) nor the RNBD registration
  (operational, done by the company at the SIC).
- Electronic invoicing (DIAN) and cookie-consent banners are **out of scope** (separate changes).
- No new third-party dependency required; reuses `diasHabiles`, `documental-storage` (for scanned
  authorization evidence), and the public router.

## Open questions (resolve before/at implementation)

1. Where do public legal pages live — inside both Next portals, or only on the marketing site
   (`public-landing`)? (Leaning: marketing site + a footer link from the portals.)
2. Granularity of `finalidades` (purposes) — a fixed catalog vs free text. (Leaning: small fixed
   catalog + "otra".)
3. Do we require re-acceptance for **minor** policy versions or only **major**? (Leaning: a
   `requiereReaceptacion` flag on `DocumentoLegal` so the publisher decides.)
