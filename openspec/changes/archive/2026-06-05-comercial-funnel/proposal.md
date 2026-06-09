> STATUS 2026-06-05: 6 open questions CONFIRMED (see `state.yaml` → `confirmed_questions`) and the 5
> HIGH adversarial-review fixes FOLDED into this proposal + the specs (see `REVIEW.md` → Resolution).
> Decisions: Q1 ContratoComercial · Q2 lazy fase init · Q3 codigoInterno = **COM-YYYY-NNNN** per empresa
> · Q4 admin MAY override tipoProceso at assign · Q5 lean concrete permisos (no wildcards) · Q6 reuse
> Cliente.responsableComercialId. Fixes: F1 concrete claves · F2 bridge sets all required Proceso fields
> (datos/etapaActual/jurisdiccion=tipo/rol default DEMANDANTE) · F3 extract codigoInterno+etapaEntrada+
> /convertir into shared helpers (clientes.router + procesos.router = Modified) · F4 errno-150: clienteId
> single cascade root, empresaId denormalized no-FK · F5 money Decimal(14,2). PROPOSAL — ready for apply.

# Proposal: Comercial — Sales Funnel, Cotización/Cobro, and the Proceso Bridge

## Intent
The `comercial` módulo (already a seeded non-baseline `Modulo`, contracted by the `independiente_pro`/`firma`/`bufete`/`bufete_pro` plans) needs its data layer: a per-empresa **sales funnel** over the existing `Cliente` — fase pipeline history, contact-touch seguimientos, cotizaciones (the offer), the contrato + poder + cobro plan (the agreement), derived alertas, and the **bridge** that turns a signed engagement into a real `Proceso` (with its `Litigante` + `ParteProceso`). This change introduces those layers **additively** on top of the foundations spine — `Cliente` is reused as the funnel anchor and is **never redefined** (no new columns, no enum changes; only virtual back-relations) — so comercial reps and despacho admins can run the pipeline end-to-end and hand confirmed cases to the legal módulo without losing traceability.

## Background / Current State
Foundations (`foundations-roles-plans-clientes`) already shipped: the `comercial` `Modulo`, the `cliente.*` permisos, the `RolEmpresa` axis (`ADMINISTRADOR`/`JURIDICO`/`CONTABLE`/`COMERCIAL`), `requirePermiso` (módulo gate + RBAC), and the `Cliente` CRM single-row lifecycle (`PROSPECTO → CLIENTE → DESCARTADO`) with its `/convertir` endpoint that find-or-creates a `Litigante` by `(empresaId, tipoDocumento, numeroDocumento)`. The legal módulo (`legal-tramites`) already owns `Proceso` (table `tramites`, `@@unique([empresaId, codigoInterno])`, `tipoEsquemaVersion` anti-drift snapshot), `TipoProceso` (global-or-despacho catalog), `EtapaProceso` (append-only bitácora), `ParteProceso` (`@@unique([procesoId, litiganteId, rol])`, `esNuestroCliente`), and the reusable `Litigante`. The `clientes.router.ts` establishes the exact tenancy idiom this change mirrors: `empresaId` always from the token via `empresaIdRequerido(req)`, a hard `WHERE { empresaId }` on every query, and an app-level `assertSameEmpresa` on every outgoing FK (because Prisma FKs do not prevent cross-tenant links).

What does NOT exist yet: any way to record where a lead is in the pipeline, log contact touches, quote a price/forma-de-pago, capture the signed contrato + poder + agreed cobro plan, surface the seven follow-up alerts the funnel needs, or materialize a `Proceso` from a closed deal. This change adds exactly those, reusing `Cliente` as the single anchor (no copy, no redefinition) and mirroring the established satellite-table idiom (denormalized `empresaId`, only `Empresa` cascades in, all cross-module FKs `SetNull`).

**DDL reality:** this repo manages MySQL with `prisma db push` — there is no `prisma/migrations/` directory. This change is applied additively with `prisma db push` + `pnpm generate`, NOT `prisma migrate dev` (which would try to baseline the entire push-managed schema and can prompt a destructive reset).

## Scope

### In Scope
- **Funnel fase pipeline (`comercial-fases`)**
  - New enum `FaseComercial { LEAD, CONTACTO, EVALUACION, PROPUESTA, NEGOCIACION, CONTRATO, PODERES, FIRMADO, PERDIDO }`.
  - New append-only table `FaseComercialHistorial` (`@@map("fases_comerciales")`): the CURRENT fase is the single row per `cliente` with `fechaCierreFase IS NULL`. No fase columns are added to `Cliente` (that would redefine it). `días-en-fase` is computed at query time, never stored.
  - `POST /comercial/clientes/:id/fase` validates the target against an allowed-edges map, then **closes-then-opens** in one `$transaction`. `PERDIDO` requires `motivoPerdida`. Terminal-fase coupling to `Cliente.estado` happens in the SAME transaction: `FIRMADO` drives the existing `/convertir` machinery (`estado → CLIENTE`, find-or-create `Litigante`, set `convertidoEn`); `PERDIDO` drives `estado → DESCARTADO`.
- **Contact-touch seguimientos (`comercial-seguimiento`)**
  - New enums `TipoGestionComercial { LLAMADA, WHATSAPP, REUNION, VIDEOLLAMADA, CORREO, OTRO }` and `EstadoSeguimiento { PENDIENTE, EN_GESTION, CERRADO }`.
  - New append-only table `SeguimientoComercial` (`@@map("seguimientos_comerciales")`): the source for `sin-seguimiento` / `tarea-vencida` / `cita-hoy` alerts and `diasSinSeguimiento`.
- **Cotización / offer (`comercial-cotizacion`)**
  - New enums `FormaPago { CONTADO, CUOTAS, CUOTALITIS, CUOTA_MIXTA, PRIMA_EXITO }` (the OFFER vocabulary) and `EstadoPropuesta { PENDIENTE, ENVIADA, ACEPTADA, RECHAZADA }`.
  - New table `Cotizacion` (`@@map("cotizaciones")`): multiple per `cliente` (re-quotes), `valorCotizado Decimal(14,2)`, optional `porcentajeExito Decimal(5,2)` (app-required for `CUOTALITIS`/`CUOTA_MIXTA`/`PRIMA_EXITO`), `numeroCuotas` (for `CUOTAS`/`CUOTA_MIXTA`), optional `tipoProcesoId` FK→`TipoProceso` (SetNull). `tipoServicio` is free text now (no `Servicio` FK — avoids coupling).
- **Contrato + poder + cobro (`comercial-contrato-cobro`)**
  - New enums `TipoContrato { PRESTACION_SERVICIOS, MANDATO, OTRO }`, `EstadoDocFirma { PENDIENTE, ENVIADO, FIRMADO }` (shared by `estadoContrato` and `estadoPoder`), and `ModalidadCobro { CUOTALITIS, CUOTA_MIXTA, PRIMA_EXITO, FIJO, OTRO }` (the AGREED/binding vocabulary, a closed enum to be **shared with the future contable módulo**).
  - New table `ContratoComercial` (`@@map("contratos_comerciales")`): two parallel doc tracks (`estadoContrato`/`estadoPoder`) + a denormalized self-describing cobro headline (`tipoCobroAcordado`/`valorAcordado`/`porcentajeAcordado`) + optional `documentoContratoUrl`/`documentoPoderUrl` (path/url only; upload infra out of scope). Named `ContratoComercial` to avoid colliding with a future contable `Contrato`.
  - New table `ConfiguracionCobro` (`@@map("configuraciones_cobro")`): the authoritative 1:1 structured cobro PLAN that contable will read (`contratoId @unique`, Cascade from `ContratoComercial`). `fechaPrimerPago` is a DUE date only (feeds the `cuota-inicial` alert as a date-passed heuristic). **Storage of a plan, not a billing engine**: no `Pago`/`Cuota`/`Recibo`/`Cartera`/`saldo` rows. The spec declares `ConfiguracionCobro` authoritative over the contract headline on conflict.
- **Derived alertas (`comercial-alertas`)**
  - `GET /comercial/alertas` returns a typed bucketed list from **seven indexed derived queries** — no stored alert rows, no scheduler (none exists): `prospecto-sin-seguimiento-3d`, `propuesta-sin-respuesta-3d`, `contrato-enviado-sin-firmar-3d`, `poder-pendiente`, `cuota-inicial-no-pagada` (date-passed heuristic, provisional until contable supplies payment truth), `cita-hoy`, `tarea-vencida`. The 3-día thresholds are service constants.
- **The Proceso bridge (`comercial-asignacion-procesos`)** — CRITICAL
  - New enum `EstadoSolicitud { PENDIENTE, EN_REVISION, ASIGNADA, RECHAZADA, CANCELADA }`.
  - New table `SolicitudAsignacionProceso` (`@@map("solicitudes_asignacion_proceso")`): the request entity Cliente(comercial) → Proceso(legal), with `contratoId @unique` (one solicitud per signed contract), `procesoId @unique` FK→`Proceso` (SetNull, bidirectional traceability), `abogadoAsignadoId` (must hold `RolEmpresa.JURIDICO`, app-asserted), and immutable snapshots (`resumenCaso`, `cobroSnapshot Json`, `notaComercial`) that survive later `Cliente` edits.
  - A NEW additive virtual back-relation `solicitudComercial` on `Proceso` (no column change on `tramites`).
  - `POST /comercial/solicitudes/:id/asignar` (ADMINISTRADOR-only) runs ONE `$transaction` that compare-and-sets `estado`, reuses the foundations `/convertir` Litigante upsert, and materializes `Proceso` + `ParteProceso` — this is the one place comercial writes into the legal módulo (generates `codigoInterno`, snapshots `TipoProceso.esquemaVersion` into `tipoEsquemaVersion`).
- **Permisos** — seeded idempotently in `seed-foundations.ts` (existing MODULOS/PERMISOS/RBAC loops) under `modulo = "comercial"` (already seeded): `comercial.seguimiento.{ver,crear,editar}`, `comercial.fase.{ver,mover}`, `comercial.cotizacion.{ver,crear,editar}`, `comercial.contrato.{ver,crear,editar}`, `comercial.cobro.{ver,configurar}`, `comercial.alertas.ver`, `comercial.solicitud.{ver,crear,asignar,rechazar}`. RBAC: ALL → `[ADMINISTRADOR, COMERCIAL]`, EXCEPT `comercial.solicitud.asignar` and `comercial.solicitud.rechazar` → `[ADMINISTRADOR]` ONLY (a COMERCIAL rep must not self-assign cases to abogados). Mirrors the existing `cliente.*` matrix.
- **Schema apply** — single `prisma db push` + `pnpm generate`: 9 new enums, 6 new tables, virtual back-relations on `Empresa`, `Cliente`, `Usuario`, `TipoProceso`, `Proceso`. No backfill needed (all new tables start empty; first fase row is created lazily).

### Out of Scope
- Admin/client UI screens for the funnel, kanban, cotización builder, or alert inbox (later UI changes consume this data layer).
- A real billing/cartera engine: `Pago`/`Cuota`/`Recibo`/`saldoPendiente`/`mora` are the future **contable** módulo's domain. Comercial stores the cobro PLAN only; `saldoPendiente` is a serializer-layer placeholder, not persisted.
- Document upload/storage infrastructure for contrato/poder PDFs (only `*Url` path/string columns are added).
- A scheduler/cron for alerts — alerts are derived queries on read; the same query functions become the future scheduler's source.
- Any change to the BEHAVIOR or columns of `Cliente`, `Proceso`, `TipoProceso`, `Litigante`, `ParteProceso`, or the existing auth gates (only additive virtual back-relations are added).
- A future contable `Contrato` model (this change only reserves the name by suffixing `ContratoComercial` and shares the `ModalidadCobro` enum).

## Capabilities

### New Capabilities
- `comercial-seguimiento`: append-only `SeguimientoComercial` contact-touch log feeding `diasSinSeguimiento` and the tarea/cita alerts.
- `comercial-fases`: the `FaseComercial` pipeline as an append-only `FaseComercialHistorial` (current = open row), with the allowed-edges transition endpoint and the FIRMADO/PERDIDO coupling to `Cliente.estado`.
- `comercial-cotizacion`: `Cotizacion` offers (re-quotable) with `FormaPago` + success-percentage / cuotas rules.
- `comercial-contrato-cobro`: `ContratoComercial` (contrato + poder doc tracks + cobro headline) and the authoritative 1:1 `ConfiguracionCobro` plan, sharing `ModalidadCobro` with future contable.
- `comercial-alertas`: the seven derived alert queries exposed as `GET /comercial/alertas` (no stored rows, no scheduler).
- `comercial-asignacion-procesos`: the `SolicitudAsignacionProceso` bridge and the assign transaction that materializes `Proceso` + `Litigante` + `ParteProceso` in the legal módulo.

### Modified Capabilities
- `clientes`: *extended* — `Cliente` gains virtual back-relations (`faseHistorial`, `seguimientos`, `cotizaciones`, `contratos`, `solicitudes`); no column or enum change. The funnel reuses `Cliente.estado` (coarse identity axis) and `Cliente.necesidadTipoProcesoId` (default for the bridge's `tipoProcesoId`); the FIRMADO transition reuses the existing `/convertir` Litigante logic.
- `tramite-management` (legal `Proceso`): *extended* — a new virtual back-relation `solicitudComercial` on `Proceso`; the assign transaction creates `Proceso`/`ParteProceso` using the existing legal-write rules (`codigoInterno` per-empresa uniqueness, `tipoEsquemaVersion` snapshot). No column change to `tramites`/`partes_tramite`.

## Approach
Reuse `Cliente` as the single funnel anchor and never redefine it: every funnel artifact is a **satellite table** keyed on `clienteId` with a denormalized `empresaId` (only `Empresa` cascades in — the single inbound cascade root — and every cross-module FK is `SetNull`), exactly mirroring the foundations `Cliente`/`Litigante` discipline. The fase axis is a **pure append-only history table** (mirroring the `EtapaProceso` bitácora idiom) rather than columns on `Cliente`; the current fase is the single open row, found via an `(clienteId, fechaCierreFase)` index, so we keep Design-1's "current fase" cheapness without redefining `Cliente`. Cobro is **two write-once layers** (offer on `Cotizacion`, agreed headline + authoritative 1:1 `ConfiguracionCobro`), with `ModalidadCobro` a closed enum that the future contable módulo joins on — comercial stores the PLAN, contable owns payment truth. Alerts are **derived queries**, never stored, so there is no alert table to migrate and the same functions seed a future scheduler. The bridge is a single `SolicitudAsignacionProceso` with `@unique` FKs both ways (`contratoId`, `procesoId`) for walkable traceability; its assign transaction is the one place comercial reaches into the legal módulo, and that coupling (codigoInterno + esquemaVersion snapshot) is flagged explicitly. Tenancy is enforced exactly like `clientes.router.ts`: `empresaId` from the token, hard `WHERE { empresaId }`, app-level `assertSameEmpresa` on every FK, `requirePermiso("comercial.*")` on every endpoint. Everything is additive via `prisma db push`; new gates fail closed only on the new `/comercial/*` endpoints.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `lex-control-api/prisma/schema.prisma` | Modified | 9 new enums; 6 new models (`FaseComercialHistorial`, `SeguimientoComercial`, `Cotizacion`, `ContratoComercial`, `ConfiguracionCobro`, `SolicitudAsignacionProceso`); virtual back-relations on `Empresa`/`Cliente`/`Usuario`/`TipoProceso`/`Proceso` (no column changes) |
| `lex-control-api` schema apply | Run | Single `prisma db push` + `pnpm generate` (NO `prisma migrate dev` — repo has no migrations dir). No backfill |
| `lex-control-api/src/seed-foundations.ts` | Modified | Add ~18 `comercial.*` permisos + RBAC rows to the existing idempotent MODULOS/PERMISOS/RBAC loops (módulo `comercial` already seeded) |
| `lex-control-api/src/modules/comercial/comercial.router.ts` | New | Tenant-scoped routers: seguimientos, fases, cotizaciones, contratos, cobro, alertas, solicitudes; `requireAuth` + `requirePermiso("comercial.*")` + `empresaIdRequerido` + hard WHERE + `assertSameEmpresa` |
| `lex-control-api/src/modules/comercial/comercial.schemas.ts` | New | Zod schemas; `empresaId`/`clienteId`-from-path discipline; forma-pago conditional validation |
| `lex-control-api/src/modules/comercial/comercial.service.ts` | New | Fase close-then-open tx; alert derived queries (7 functions + constants); the assign bridge tx (reuses `/convertir` Litigante upsert + legal `codigoInterno`/`esquemaVersion` write) |
| `lex-control-api/src/app.ts` | Modified | Mount `/comercial` router |
| `lex-control-api/src/index.ts` | Regen | Re-exports stay correct after `prisma generate` |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Two concurrent fase transitions both close-then-open, leaving two open rows | Med | The transition runs in one `$transaction` that `SELECT ... FOR UPDATE`s the `clientes` row (stable parent) before closing the prior open row and inserting the new one; the `(clienteId, fechaCierreFase)` invariant is app-enforced (MySQL/Prisma cannot do a partial unique) |
| Bridge writes into the legal módulo drift from legal write rules (`codigoInterno` format, `esquemaVersion` snapshot) | High | The assign tx reuses the EXACT legal-write helpers (per-empresa `codigoInterno` generation, `tipoEsquemaVersion = TipoProceso.esquemaVersion` snapshot); this single coupling point is flagged in code + spec ("MIRAR CON MARITZA") and pinned by an open question on the codigoInterno policy |
| Cross-tenant FK via a satellite-table body (`tipoProcesoId`, `abogadoAsignadoId`, `contratoId`) | Med | `empresaId` only from `req`; `assertSameEmpresa` on every outgoing FK (TipoProceso may be global `empresaId=null`); `abogadoAsignadoId` additionally asserted to hold `RolEmpresa.JURIDICO` |
| MySQL errno-150 (multiple cascade paths to one table) | Med | Only `Empresa` and `Cliente` cascade into satellites; `ConfiguracionCobro` cascades from `ContratoComercial` only; every cross-module FK (`Usuario`/`TipoProceso`/`Proceso`/`Cotizacion`/`ContratoComercial`) is `SetNull`; `procesoId` is SetNull so deleting a `Proceso` never cascade-deletes the audit |
| Cobro headline vs `ConfiguracionCobro` disagree | Low | Spec declares `ConfiguracionCobro` authoritative; the `ContratoComercial.{tipoCobroAcordado,valorAcordado,porcentajeAcordado}` fields are an explicit denormalized self-describing summary |
| COMERCIAL rep self-assigns a case to an abogado | Med | `comercial.solicitud.asignar`/`.rechazar` RBAC restricted to `[ADMINISTRADOR]` ONLY; reps can only `.crear` and (comercial-side) cancel |
| `cuota-inicial` alert fires on an already-paid first cuota | Low (provisional) | Documented as a date-passed heuristic ONLY (`fechaPrimerPago < now`); paid/unpaid truth belongs to the future contable módulo; the alert query is the durable contract that contable later refines |
| Snapshots drift from live `Cliente` after edits | Low (intended) | `resumenCaso`/`cobroSnapshot`/`notaComercial` are intentionally frozen at request time for traceability; the live chain `Cliente→ContratoComercial→Solicitud→Proceso` is walkable via `@unique` FKs for current data |

## Rollback Plan
The schema change is additive and applied with `prisma db push` (no migration history). Rollback is manual and safe because no existing table's columns are altered (the back-relation fields are virtual in Prisma and produce no column changes): `DROP TABLE` the 6 new tables (`solicitudes_asignacion_proceso`, `configuraciones_cobro`, `contratos_comerciales`, `cotizaciones`, `seguimientos_comerciales`, `fases_comerciales` — in FK-dependency order) and `DROP TYPE` the 9 new enums (or `git revert` the schema and re-run `prisma db push`, which drops the now-absent tables — verify on a non-prod copy first, as `db push` can warn about data loss). Remove the `comercial` module/service/router, unmount `/comercial` from `app.ts`, and revert the `comercial.*` permiso/RBAC rows added to `seed-foundations.ts` (idempotent upserts; re-seeding is safe). Because every new gate is mounted on new `/comercial/*` endpoints only, removal leaves all current behavior intact. Re-run `pnpm generate`.

## Dependencies
- `foundations-roles-plans-clientes` (APPLIED): the `comercial` `Modulo`, `cliente.*` permisos + RBAC loops, `requirePermiso`, `RolEmpresa`, the `Cliente` model, and the `/convertir` Litigante upsert this change reuses.
- `legal-tramites` (APPLIED): `Proceso` (`tramites`), `TipoProceso` (+ `esquemaVersion`), `EtapaProceso`, `ParteProceso` (+ `@@unique([procesoId,litiganteId,rol])`, `esNuestroCliente`), `Litigante` (+ `@@unique([empresaId,tipoDocumento,numeroDocumento])`) and the legal-write rules (`codigoInterno`, `tipoEsquemaVersion`) the bridge calls.
- The tenancy idiom in `clientes.router.ts` (`empresaIdRequerido`, hard WHERE, `assertSameEmpresa`).

## Success Criteria
- [ ] A single `prisma db push` + `pnpm generate` adds the 9 enums and 6 tables with no errno-150 and no change to any existing table's columns. (No `prisma migrate dev`; no backfill.)
- [ ] `seed-foundations.ts` (re-run, idempotent) adds the ~18 `comercial.*` permisos under the existing `comercial` módulo with RBAC `[ADMINISTRADOR, COMERCIAL]` except `solicitud.asignar`/`.rechazar` = `[ADMINISTRADOR]`.
- [ ] `POST /comercial/clientes/:id/fase` validates allowed edges, closes-then-opens in one tx (exactly one open row per cliente), requires `motivoPerdida` for PERDIDO, and the FIRMADO/PERDIDO transitions move `Cliente.estado` (CLIENTE via existing `/convertir`, DESCARTADO) in the same tx.
- [ ] `GET /comercial/alertas` returns the seven derived buckets scoped by token `empresaId`, with no stored alert rows and no scheduler.
- [ ] `POST /comercial/solicitudes` requires the cliente's `ContratoComercial` with `estadoContrato = FIRMADO AND estadoPoder = FIRMADO`, snapshots `resumenCaso`/`cobroSnapshot`, and defaults `tipoProcesoId` from `Cliente.necesidadTipoProcesoId`.
- [ ] `POST /comercial/solicitudes/:id/asignar` (ADMINISTRADOR only) in one tx compare-and-sets `PENDIENTE/EN_REVISION → ASIGNADA`, asserts `abogadoAsignadoId` holds `JURIDICO`, find-or-creates the `Litigante`, creates `Proceso` (`codigoInterno`, `tipoEsquemaVersion` snapshot, `estado = ABIERTO`, `responsableId = abogadoAsignadoId`) + `ParteProceso` (`esNuestroCliente = true`), and stamps `solicitud.procesoId`.
- [ ] Every `/comercial/*` endpoint enforces `requireAuth` + `requirePermiso("comercial.*")` + `empresaId` from token + hard WHERE + `assertSameEmpresa`; cross-empresa FKs are rejected; `Cliente`/`Proceso`/auth behavior is unchanged and all existing tests still pass.

## Open Questions
- **Q1 — Contrato naming:** ship `ContratoComercial`/`contratos_comerciales` now (recommended — verified no `Contrato` model exists today, but cobro is explicitly shared with a future contable módulo that will plausibly own its own `Contrato`, so the suffix is a cheap collision hedge), or keep bare `Contrato` and rename later? Confirm contable will indeed have its own contract concept.
- **Q2 — Fase initialization:** does `POST /clientes` auto-seed an initial `LEAD` fase row, or is the first row created lazily on the first `POST /comercial/clientes/:id/fase`? Recommend **lazy** so the foundations `clientes` router stays untouched (no comercial coupling leaks into the create path).
- **Q3 — Bridge `codigoInterno` policy (THE doc flags this whole bridge "MIRAR CON MARITZA"):** the assign tx must generate a per-empresa-unique `Proceso.codigoInterno` and snapshot `TipoProceso.esquemaVersion`. Confirm the format/sequence policy (e.g. `YYYY-NNNN` per empresa) — currently undefined and the one place comercial writes into the legal módulo.
- **Q4 — Assign authority / tipoProceso override:** confirm ASIGNADA should also advance/confirm the funnel, and whether the admin MAY override the comercial-proposed `tipoProcesoId` at assign time. Recommend **admin MAY override**; the override is what materializes the `Proceso`.
- **Q5 — Permiso granularity:** are `comercial.contrato.firmar` / `comercial.solicitud.cancelar` needed as distinct permisos, or do `.editar` (state transitions incl. FIRMADO) and the ADMINISTRADOR-gated rejection cover them? Recommend **folding** firmar into `.editar` and cancelar into `.crear`-owner scope, matching the lean `cliente.*` set.
- **Q6 — Per-fase/per-cotización responsable:** does comercial need a responsable distinct from `Cliente.responsableComercialId`, or is reusing it + per-row `registradoPorId` sufficient? Recommend **reuse** (no extra table) unless reps split work mid-funnel.