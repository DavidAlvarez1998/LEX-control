# Tasks: comercial-funnel

> PROPOSAL — not applied. Builds on the APPLIED `foundations-roles-plans-clientes` (Cliente, comercial
> Modulo, requirePermiso, /convertir Litigante upsert) and `legal-tramites` (Proceso, TipoProceso,
> ParteProceso, Litigante). `Cliente` is the funnel anchor and is NOT redefined (only virtual
> back-relations). DDL via `prisma db push` (repo has NO migrations dir) — never `prisma migrate dev`
> against the live DB. No backfill (all new tables start empty; first fase row is lazy).

## Review Workload Forecast
- **Changed-lines budget: High** (~700–1000 lines: 9 enums + 6 models in `schema.prisma`, ~18 permisos + RBAC in `seed-foundations.ts`, the comercial router/schemas/service, the fase close-then-open tx, the 7 alert queries, and the assign bridge tx that reaches into the legal módulo).
- **Chained PRs recommended: Yes** — split along the six capabilities plus the cross-cutting schema/seed.
- **Suggested split:** Phase 1 (schema + push + permiso seed) → Phase 2 (seguimientos + fases) → Phase 3 (cotizacion + contrato/cobro) → Phase 4 (alertas) → Phase 5 (the bridge) → Phase 6 (verify). The bridge (Phase 5) depends on fases (FIRMADO coupling) and contrato/cobro (signed-engagement guard), so keep it last and chained.

## Phase 0 — Confirm scope
- [ ] 0.1 Q1 contrato naming — confirm `ContratoComercial`/`contratos_comerciales` now (recommend YES; cheap collision hedge vs a future contable `Contrato`).
- [ ] 0.2 Q2 fase init — confirm LAZY first-fase creation (recommend YES; keeps the foundations `clientes` router untouched).
- [ ] 0.3 Q3 bridge `codigoInterno` policy — confirm per-empresa format/sequence (e.g. `YYYY-NNNN`). THE doc flags the whole bridge "MIRAR CON MARITZA". Blocks Phase 5.
- [ ] 0.4 Q4 assign authority — confirm ASIGNADA advances the funnel and admin MAY override `tipoProcesoId` (recommend YES).
- [ ] 0.5 Q5 permiso granularity — confirm folding `firmar` into `.editar` and `cancelar` into `.crear`-owner scope (recommend YES; lean set).
- [ ] 0.6 Q6 responsable — confirm reusing `Cliente.responsableComercialId` + per-row `registradoPorId` (recommend YES; no extra table).

## Phase 1 — Backend: schema, db push, permiso seed
- [ ] 1.1 `schema.prisma`: 9 enums — `FaseComercial`, `TipoGestionComercial`, `EstadoSeguimiento`, `FormaPago`, `EstadoPropuesta`, `TipoContrato`, `EstadoDocFirma`, `ModalidadCobro`, `EstadoSolicitud`. Reuse existing `Prioridad`/`Jurisdiccion`/`RolParte`/`EstadoProceso` for the bridge (do NOT duplicate).
- [ ] 1.2 `schema.prisma`: `FaseComercialHistorial` (`@@map("fases_comerciales")`) — only `empresaId`/`clienteId` Cascade, `responsableComercialId`/`registradoPorId` SetNull; indexes `[empresaId]`, `[clienteId, fechaCierreFase]`, `[fase]`.
- [ ] 1.3 `schema.prisma`: `SeguimientoComercial` (`@@map("seguimientos_comerciales")`) — Cascade `empresaId`/`clienteId`, SetNull `registradoPorId`; indexes `[clienteId, fechaContacto]`, `[empresaId, fechaProximaTarea]`, `[empresaId, estadoSeguimiento]`.
- [ ] 1.4 `schema.prisma`: `Cotizacion` (`@@map("cotizaciones")`) — `valorCotizado Decimal(10,2)`, `porcentajeExito Decimal(5,2)`; SetNull `tipoProcesoId`/`creadoPorId`; indexes `[clienteId]`, `[empresaId, estadoPropuesta]`, `[empresaId, fechaEnvio]`.
- [ ] 1.5 `schema.prisma`: `ContratoComercial` (`@@map("contratos_comerciales")`) — headline `Decimal(10,2)`/`Decimal(5,2)`; SetNull `cotizacionId`/`registradoPorId`; indexes `[clienteId]`, `[empresaId, estadoContrato, fechaEnvio]`, `[empresaId, estadoPoder]`.
- [ ] 1.6 `schema.prisma`: `ConfiguracionCobro` (`@@map("configuraciones_cobro")`) — `contratoId @unique` Cascade from `ContratoComercial`, `clienteId` Cascade; indexes `[empresaId, fechaPrimerPago]`, `[clienteId]`. Schema comment: NO Pago/Cuota/Recibo/Cartera/saldo (contable's domain).
- [ ] 1.7 `schema.prisma`: `SolicitudAsignacionProceso` (`@@map("solicitudes_asignacion_proceso")`) — `contratoId @unique` SetNull, `procesoId @unique` SetNull, three named `Usuario?` SetNull relations, `cobroSnapshot Json?`; indexes `[empresaId, estado]`, `[clienteId]`, `[abogadoAsignadoId, estado]`. Add virtual back-relation `solicitudComercial` on `Proceso` (no `tramites` column change).
- [ ] 1.8 Add virtual back-relations on `Empresa`/`Cliente`/`Usuario`/`TipoProceso` (relation fields only, no column changes). `prisma format` + `prisma validate` clean.
- [ ] 1.9 `prisma db push` + `prisma generate`. Verify 6 tables created, no errno-150, no existing column changed, existing tests still green. (NO `prisma migrate dev`, NO backfill.)
- [ ] 1.10 `seed-foundations.ts`: add ~18 `comercial.*` permisos to the existing idempotent MODULOS/PERMISOS/RBAC loops under `modulo = "comercial"`: `seguimiento.{ver,crear,editar}`, `fase.{ver,mover}`, `cotizacion.{ver,crear,editar}`, `contrato.{ver,crear,editar}`, `cobro.{ver,configurar}`, `alertas.ver`, `solicitud.{ver,crear,asignar,rechazar}`. RBAC `[ADMINISTRADOR, COMERCIAL]` EXCEPT `solicitud.asignar`/`.rechazar` → `[ADMINISTRADOR]` ONLY. Idempotent upserts; re-run safe.

## Phase 2 — comercial-seguimiento + comercial-fases
- [ ] 2.1 `src/modules/comercial/comercial.schemas.ts` + `comercial.router.ts` (mounted `/comercial` in `app.ts`): seguimientos list/read/create/update — `empresaId` from `req`, hard WHERE, `assertSameEmpresa` on `clienteId`/`registradoPorId`. Gated by `requirePermiso("comercial.seguimiento.*")`.
- [ ] 2.2 Fase reads (`GET /comercial/clientes/:id/fase`, history) — `comercial.fase.ver`; `diasEnFase` computed in serializer, never stored.
- [ ] 2.3 `comercial.service.ts` fase transition: allowed-edges map, `PERDIDO` requires `motivoPerdida`, one `$transaction` `SELECT FOR UPDATE` on `clientes` → close prior open row → insert new open row. `POST /comercial/clientes/:id/fase` gated by `comercial.fase.mover`.
- [ ] 2.4 Terminal coupling in the SAME tx: `FIRMADO` → reuse `/convertir` machinery (`estado → CLIENTE`, Litigante upsert, `convertidoEn`); `PERDIDO` → `estado → DESCARTADO`. `Cliente.estado` never edited independently for these.

## Phase 3 — comercial-cotizacion + comercial-contrato-cobro
- [ ] 3.1 Cotizacion CRUD — `comercial.cotizacion.*`; forma-pago conditional validation (`porcentajeExito` for CUOTALITIS/CUOTA_MIXTA/PRIMA_EXITO; `numeroCuotas` for CUOTAS/CUOTA_MIXTA); `assertSameEmpresa` on `clienteId`/`tipoProcesoId` (global allowed)/`creadoPorId`.
- [ ] 3.2 ContratoComercial CRUD — `comercial.contrato.*`; two doc tracks (`estadoContrato`/`estadoPoder` `EstadoDocFirma`); cobro headline; `documento*Url` path strings only (no upload infra); `assertSameEmpresa` on `clienteId`/`cotizacionId`/`registradoPorId`.
- [ ] 3.3 ConfiguracionCobro 1:1 — `comercial.cobro.{ver,configurar}`; enforce one per `contratoId` (`@unique`); spec: ConfiguracionCobro authoritative over the headline; boundary assertion (no payment rows).

## Phase 4 — comercial-alertas
- [ ] 4.1 `comercial.service.ts`: 7 derived query functions + 3-día constants; `GET /comercial/alertas` returns `{ tipo, clienteId, referenciaId, vencidoDesde }[]`, scoped by token `empresaId`, gated by `comercial.alertas.ver`. No stored rows, no scheduler.
- [ ] 4.2 Computed fields (`saldoPendiente` placeholder, `diasSinSeguimiento`, `conversionACliente`, `diasEnFase`) in the serializer layer, never persisted. Document `cuota-inicial` as a date-passed heuristic (provisional until contable).

## Phase 5 — comercial-asignacion-procesos (THE BRIDGE)
- [ ] 5.1 `POST /comercial/solicitudes` (`comercial.solicitud.crear`): require cliente's `ContratoComercial` `estadoContrato = FIRMADO AND estadoPoder = FIRMADO`; `contratoId @unique`; snapshot `resumenCaso`/`cobroSnapshot`; default `tipoProcesoId` from `Cliente.necesidadTipoProcesoId`; `estado = PENDIENTE`. `CANCELADA` = comercial-side withdrawal.
- [ ] 5.2 `GET /comercial/solicitudes?estado=` (`comercial.solicitud.ver`, ADMINISTRADOR) via `@@index([empresaId, estado])`; reachable to all related comercial data + snapshots.
- [ ] 5.3 `POST /comercial/solicitudes/:id/asignar` (`comercial.solicitud.asignar`, ADMINISTRADOR ONLY) in ONE `$transaction`: compare-and-set `PENDIENTE`/`EN_REVISION` → `ASIGNADA`; `assertSameEmpresa` on `contratoId`/`tipoProcesoId`/`abogadoAsignadoId` AND assert `abogadoAsignadoId` holds `RolEmpresa.JURIDICO`; reuse `/convertir` Litigante upsert (set `Cliente.litiganteId` if unset); create `Proceso` (`codigoInterno` GENERATED per-empresa — see Q3, `tipoEsquemaVersion` = `TipoProceso.esquemaVersion` snapshot, `estado = ABIERTO`, `responsableId = abogadoAsignadoId`, `jurisdiccion` from sugerida); create `ParteProceso` (`esNuestroCliente = true`, idempotent via `@@unique`); stamp `solicitud.{procesoId @unique, abogadoAsignadoId, asignadoPorId, tareasDefinidas, fechaAsignacion}`. Admin MAY override `tipoProcesoId`. **FLAG**: this is the one place comercial writes into the legal módulo.
- [ ] 5.4 `POST /comercial/solicitudes/:id/rechazar` (`comercial.solicitud.rechazar`, ADMINISTRADOR ONLY): `estado = RECHAZADA` + `motivoRechazo`; no `Proceso`. Abogado traceability: filter by `abogadoAsignadoId` via `@@index`; chain walkable both ways via `@unique` FKs.

## Phase 6 — Verify
- [ ] 6.1 `tsc --noEmit` clean after `prisma generate`.
- [ ] 6.2 `pnpm test` — existing suite still green + new comercial tests (tenancy isolation, fase close-then-open single-open-row, FIRMADO→convertir / PERDIDO→DESCARTADO, forma-pago validation, ConfiguracionCobro 1:1, 7 alert buckets, bridge assign materializes Proceso+ParteProceso, JURIDICO assertion, COMERCIAL cannot asignar/rechazar).
- [ ] 6.3 Live (on a non-prod copy first): `db push` + re-run seed (idempotent); module gate (`comercial` not contracted → 403); end-to-end funnel LEAD→FIRMADO→solicitud→asignar→Proceso.

## Notes
- DDL: repo uses `prisma db push` (no `prisma/migrations/`). Rollback = manual DROP of the 6 new tables (FK-dependency order) + 9 enums (see proposal Rollback). Test on a non-prod copy first; `db push` can warn on data loss.
- Env/perms: `lex-control-api/.env` (DATABASE_URL) is write-blocked per repo memory — push/seed use the existing connection without editing `.env`.
- `Cliente` is NEVER redefined: no columns, no enum changes — only virtual back-relations. The fase axis is a history table, not columns.
- `comercial.solicitud.asignar`/`.rechazar` are ADMINISTRADOR-only (a COMERCIAL rep must not self-assign cases). Everything else `[ADMINISTRADOR, COMERCIAL]`, mirroring `cliente.*`.
- The assign tx is the ONE coupling into the legal módulo (`codigoInterno` + `esquemaVersion` snapshot) — flag it; pinned by Q3 ("MIRAR CON MARITZA").
- Comercial stores the cobro PLAN only; payment truth (saldo/mora/pagos) is the future contable módulo's domain. `ModalidadCobro` is the shared closed enum.