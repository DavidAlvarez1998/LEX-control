# Adversarial Review — comercial-funnel

Findings from the multi-agent Review phase against the authored proposal + specs and CURRENT code.

## Resolution (2026-06-05) — all 5 HIGH fixes folded into proposal/specs
- **F1 (wildcards)** RESOLVED: every tenancy requirement now gates on the CONCRETE seeded clave
  (`comercial.X.ver/.crear/.editar`); `comercial.X.*` is documented as shorthand only — requirePermiso
  does exact-clave lookup.
- **F2 (bridge required Proceso fields)** RESOLVED: the assign tx now sets `datos={}`,
  `etapaActual=etapaEntrada(tipo.etapas).key`, `jurisdiccion=tipo.jurisdiccion` (NOT sugerida), resolves
  `tipoProcesoId = adminOverride ?? Cliente.necesidadTipoProcesoId` (null → 400), and
  `ParteProceso.rol = rolParteSugerido ?? DEMANDANTE`.
- **F3 (inline helpers)** RESOLVED: spec states codigoInterno generator + etapaEntrada + the /convertir
  Litigante upsert are INLINE today and MUST be extracted to shared services; `clientes.router.ts` and
  `procesos.router.ts` are now listed Modified.
- **F4 (errno-150 cascade)** RESOLVED: every satellite has `clienteId` as the SINGLE cascade root;
  `empresaId` is a denormalized plain column with NO FK (like `UsuarioRolEmpresa`); `ConfiguracionCobro`
  roots on `contratoId` (clienteId/empresaId no FK).
- **F5 (money precision)** RESOLVED: cobro money fields are `Decimal(14,2)` (match `Proceso.cuantiaValor`);
  percentages stay `Decimal(5,2)`.
- DECISIONS Q1–Q6 confirmed (state.yaml). codigoInterno = `COM-YYYY-NNNN`. The ~12 MED/LOW gaps below
  remain as build-time notes for the implementer.

The original adversarial findings are kept verbatim below.

## Verdict

CONCEPT SOUND, NOT READY TO IMPLEMENT AS WRITTEN. The architecture (Cliente-as-anchor satellites, append-only fase/seguimiento logs, two-layer cobro with authoritative ConfiguracionCobro, derived alerts, snapshot bridge with @unique two-way FKs, ADMINISTRADOR-gated assign) is well reasoned and mostly faithful to the doc and the foundations idiom. But it has BLOCKING defects that violate its own Success Criteria: (1) the requirePermiso wildcard notation does not work — the gate is exact-clave findUnique and would 500; (2) the bridge cannot create a valid Proceso — required datos, etapaActual, jurisdiccion, tipoProcesoId and ParteProceso.rol are unsourced or nullable-vs-required, and the codigoInterno/etapaEntrada/convertir 'reuse' needs an unscoped refactor of procesos.router and clientes.router; (3) cascade fan-in (especially ConfiguracionCobro with empresaId+clienteId+contratoId all Cascade, and every satellite with both Cascade empresaId and Cascade clienteId) is the exact MySQL errno-150 hazard the schema's own ParteProceso avoids with Restrict — threatening Success Criterion #1; (4) Decimal(10,2) under-sizes COP case money vs the established Decimal(14,2). Required before APPLIED: pin gating to concrete claves; resolve the Proceso-creation field gaps and scope the legal/clientes helper extractions (codigoInterno, etapaEntrada, /convertir litigante upsert); fix cascade paths to a single Cascade root per satellite; bump money to Decimal(14,2); reconcile fase-FIRMADO vs contrato-FIRMADO; enumerate the allowed-edges map and the EstadoDocFirma transition endpoints. Open Q3 is mislabeled 'undefined' — EXP-YYYY-NNNN already exists; the real question is extraction, not policy. Files: /mnt/storage/DAVID/lex-control/lex-control-api/prisma/schema.prisma (Proceso 276-318, ParteProceso 379-395, TipoProceso 235-261, Cliente 644-678), /mnt/storage/DAVID/lex-control/lex-control-api/src/middleware/auth.ts (requirePermiso 125-154), /mnt/storage/DAVID/lex-control/lex-control-api/src/modules/procesos/procesos.router.ts (codigoInterno+etapaEntrada 120-185), /mnt/storage/DAVID/lex-control/lex-control-api/src/modules/clientes/clientes.router.ts (concrete claves), /mnt/storage/DAVID/lex-control/lex-control-api/src/seed-foundations.ts (PERMISOS/RBAC pattern)."

## Conflicts (ordered)

### [HIGH] requirePermiso() does NOT support wildcards. It is `prisma.permiso.findUnique({ where: { clave } })` (auth.ts:129) against an exact clave, and a missing clave throws HttpError(500) 'Permiso no configurado'. Every spec writes the gate as requirePermiso("comercial.seguimiento.*"), requirePermiso("comercial.cotizacion.*"), requirePermiso("comercial.*") etc. Taken literally these are unseeded claves and would 500 on the module gate. The existing clientes.router uses CONCRETE claves (requirePermiso("cliente.ver"), "cliente.crear"...), never "cliente.*". Approach/Affected-Areas/Risks also describe the gate as requirePermiso("comercial.*").

**Fix:** Treat comercial.X.* as shorthand ONLY. Each endpoint MUST gate on the concrete seeded clave (comercial.seguimiento.ver/.crear/.editar, comercial.fase.ver/.mover, ...), exactly as clientes.router does. State this explicitly so an implementer does not pass a literal * clave.

### [HIGH] Proceso.datos (Json) and Proceso.etapaActual (String) are REQUIRED with no default (schema 292-293). The bridge 'Assign materializes Proceso' requirement lists the Proceso fields it sets (codigoInterno, tipoEsquemaVersion, jurisdiccion, titulo, estado, prioridad, responsableId, creadoPorId) but OMITS datos and etapaActual. The existing procesos.router derives etapaActual from etapaEntrada(tipo.etapas) and takes datos from the request body. A Proceso.create missing these fails at the Prisma/DB layer.

**Fix:** The assign tx MUST set etapaActual = etapaEntrada(tipoProceso.etapas).key (reuse the legal helper) and supply datos (e.g. {} or a solicitud snapshot). Add both to the bridge requirement and Success Criteria.

### [HIGH] The legal codigoInterno generator (procesos.router:133-138) is count(...)+1 -> `EXP-${year}-NNNN`, an INLINE tx-local snippet, NOT an exported helper. The proposal claims the bridge 'reuses the EXACT legal-write helpers' for codigoInterno/esquemaVersion, but no such helper exists to import; today it is embedded in the procesos create route. Open Q3 calls the policy 'currently undefined' — but it IS defined (EXP-YYYY-NNNN); the real gap is it is not factored out, so the bridge will duplicate (the High drift risk the proposal flags) or require a procesos.router refactor that the change does not scope.

**Fix:** Scope extraction of the codigoInterno generator + etapaEntrada into a shared legal helper both procesos.router and the bridge call, OR list procesos.router as Modified. Do not call it 'reusing existing helpers' when none are exported.

### [HIGH] Cascade fan-in / errno-150. The proposal says 'only Empresa and Cliente cascade in' to satellites. With Empresa->satellite (denormalized empresaId Cascade) AND Empresa->Cliente->satellite (Cascade), every satellite that has BOTH a Cascade empresaId and a Cascade clienteId has two cascade paths to it — the exact MySQL errno-150/1785 hazard the schema's own ParteProceso avoids with Restrict (line 388 comment). ConfiguracionCobro is worst: empresaId+clienteId+contratoId all proposed Cascade = three paths, plus Empresa->Cliente->config and Empresa->Contrato->config. Directly threatens Success Criterion #1 ('no errno-150').

**Fix:** One Cascade root per satellite. Mirror ParteProceso: keep clienteId Cascade and make the denormalized empresaId a plain indexed column with NO @relation (as UsuarioRolEmpresa already does per Empresa comment 37-38), or NoAction. For ConfiguracionCobro keep ONLY contratoId Cascade; make empresaId/clienteId non-relational denormalized columns.

### [MED] Proceso.jurisdiccion is REQUIRED (line 283). The solicitud carries jurisdiccionSugerida Jurisdiccion? (optional). The existing router sets Proceso.jurisdiccion = tipo.jurisdiccion (line 147), NOT from a user-supplied sugerida. The bridge says 'jurisdiccion from sugerida' which can be null and contradicts the legal-write convention. If sugerida is null the create fails.

**Fix:** Set Proceso.jurisdiccion = resolvedTipoProceso.jurisdiccion (legal convention); treat jurisdiccionSugerida only as a UI hint for picking the tipo. Reconcile the spec.

### [MED] FIRMADO coupling claims to 'reuse the existing /convertir machinery' / the EXACT upsert from /convertir. But /convertir is an HTTP route handler in clientes.router (POST /clientes/:id/convertir), not an exported service function; it cannot be reused from another module/transaction without refactoring into a shared litigante-upsert helper. clientes is listed only as 'extended (virtual back-relations)'; extracting convertir is unscoped.

**Fix:** Add to scope: factor the Litigante find-or-create + Cliente.convertidoEn/estado update out of /convertir into a service fn reusable inside a passed-in tx; list clientes as Modified.

### [MED] Money precision. Proposal uses Decimal(10,2) for valorCotizado/valorAcordado/valorFijo/valorCuota. Schema convention for case-value money is Decimal(14,2) (Proceso.cuantiaValor, line 286); plan/servicio prices use (10,2). Decimal(10,2) caps at 99,999,999.99 COP (~100M). Colombian honorarios/cuantia routinely exceed 100M COP, so a large cotizacion overflows.

**Fix:** Use Decimal(14,2) for the cobro money fields to match Proceso.cuantiaValor and avoid COP overflow; Decimal(5,2) for percentages is fine.

### [MED] ParteProceso.rol is REQUIRED (RolParte, no default, line 383). The bridge sets rol = rolParteSugerido, but rolParteSugerido is OPTIONAL on the solicitud. If null, ParteProceso.create fails. No default/scenario given.

**Fix:** Define a default rol (e.g. DEMANDANTE) when rolParteSugerido is null, or make it required at solicitud-create time.

### [LOW] FormaPago (offer) and ModalidadCobro (agreed) overlap and are not in the source doc, which lists ONE modality set {cuotalitis,cuota_mixta,prima_exito,fijo}. CONTADO/CUOTAS in the offer enum have no clean target in the agreed enum, creating an undocumented mapping burden.

**Fix:** Document the offer->agreed mapping (CONTADO/CUOTAS -> FIJO; others pass through) in the specs, or collapse to one enum unless the offer/agreed split is a hard requirement.

## Bridge check (comercial→proceso)

Directionally sound but NOT FK-ready / not creation-ready as written. Soundness: contratoId @unique (one solicitud per signed contract) + procesoId @unique (SetNull, bidirectional) gives a walkable Cliente -> ContratoComercial -> Solicitud -> Proceso chain both ways; immutable snapshots (resumenCaso, cobroSnapshot, notaComercial) correctly survive Cliente edits; compare-and-set PENDIENTE/EN_REVISION -> ASIGNADA guards double-assignment; ParteProceso idempotency via @@unique([procesoId,litiganteId,rol]) is correct; procesoId SetNull (not Cascade) correctly preserves the solicitud audit when a Proceso is deleted, matching the legal Restrict/SetNull discipline. Roles: ADMINISTRADOR (assign endpoint, ADMINISTRADOR-only RBAC) creates the Proceso; abogadoAsignadoId (asserted to hold JURIDICO via UsuarioRolEmpresa, which is checkable and empresa-scoped) becomes responsableId; asignadoPorId becomes creadoPorId. That separation matches the doc (admin assigns, abogado receives) and is sound. Traceability is preserved. BUT it cannot create a VALID Proceso: (1) required Proceso.datos (Json) and Proceso.etapaActual (String) are never set by the bridge requirement — the create fails; the legal router sources etapaActual from etapaEntrada(tipo.etapas) and datos from the body, neither provided by the solicitud. (2) Proceso.tipoProcesoId is REQUIRED but solicitud.tipoProcesoId and Cliente.necesidadTipoProcesoId are both optional/SetNull — no null guard. (3) Proceso.jurisdiccion is REQUIRED; 'from sugerida' is optional/nullable and contradicts the legal convention (jurisdiccion = tipo.jurisdiccion). (4) ParteProceso.rol is REQUIRED but rolParteSugerido is optional — no default. (5) codigoInterno generation and etapaEntrada are inline, non-exported logic in procesos.router; 'reusing the exact legal helpers' needs an unscoped refactor, so the High drift risk the proposal itself flags is real and unmitigated. (6) If TipoProceso.etapas is empty (a legal global tipo), the existing logic throws 400; the bridge inherits this with no fallback. Net: traceability/role-separation are correct; Proceso-creation correctness and the legal-write coupling are the unfinished parts.

## Multi-tenant / permiso gating

Isolation design is correct and faithfully mirrors clientes.router: empresaId always from token (empresaIdRequerido), hard WHERE { empresaId }, app-level assertSameEmpresa on every outgoing FK (Prisma FKs do not prevent cross-tenant links), with the correct nuance that a global TipoProceso (empresaId=null) is accepted. Denormalized empresaId on every satellite matches the Litigante/Cliente precedent. Cross-empresa rejections (clienteId/tipoProceso/cotizacion of despacho B) are covered in scenarios. abogadoAsignadoId is additionally asserted to hold RolEmpresa.JURIDICO (checkable via UsuarioRolEmpresa, which carries empresaId) and must also be same-empresa — covered. GATING DEFECT (high): the comercial.* permiso gating as written (requirePermiso(\"comercial.seguimiento.*\") etc.) will NOT gate — requirePermiso does an exact findUnique on the clave and 500s on an unseeded one; wildcards are not implemented. Intent (module gate via permiso.modulo='comercial' + RBAC) is right, but the router must pass CONCRETE seeded claves, exactly as clientes.router uses cliente.crear not cliente.*. The module gate itself is correct: every comercial.* permiso has modulo='comercial' and requirePermiso checks modulosHabilitados.has('comercial'), so an empresa whose plan lacks the comercial módulo is correctly blocked. RBAC split (asignar/rechazar = ADMINISTRADOR-only so a COMERCIAL cannot self-assign cases to abogados) is correct and well justified. Note: esAdminEmpresa short-circuits RBAC (auth.ts:148), so a company admin bypasses the role check on these endpoints too — consistent with existing behavior, but worth flagging for the assign endpoint (a non-COMERCIAL company admin could still assign), not a regression."

## Gaps vs the doc

- Proceso.datos and Proceso.etapaActual (both required, no default) are never sourced by the bridge — doc-vs-spec gap; the bridge cannot create a valid Proceso as specified.
- Empty/absent TipoProceso.etapas: procesos.router throws HttpError(400,'El tipo de proceso no define etapas') when etapaEntrada returns nothing. The bridge defaults tipoProcesoId from Cliente.necesidadTipoProcesoId, which may be a global TipoProceso; if its etapas are empty the assign tx fails. No scenario covers 'tipo without etapas'.
- tipoProcesoId null at assign: Solicitud.tipoProcesoId is optional (SetNull) and Cliente.necesidadTipoProcesoId is optional, but Proceso.tipoProcesoId is REQUIRED (Restrict). If both null and admin does not override, the assign tx has no tipo. No scenario guards this.
- Seguimiento: no requirement/endpoint for moving estadoSeguimiento -> CERRADO, although comercial.seguimiento.editar is seeded and the tarea-vencida alert depends on estadoSeguimiento != CERRADO. The closing transition is unspecified.
- Allowed-edges fase map is asserted but never enumerated. 'forward LEAD -> ... -> FIRMADO' is ambiguous vs the non-terminal scenario LEAD->PROPUESTA (which implies skipping is allowed). Define the concrete edge set.
- Fase CONTRATO/PODERES vs ContratoComercial.estadoContrato/estadoPoder are unreconciled. Moving to fase FIRMADO converts the Cliente but does NOT require a FIRMADO ContratoComercial; yet POST /comercial/solicitudes requires estadoContrato=FIRMADO AND estadoPoder=FIRMADO. A Cliente can be fase FIRMADO (estado=CLIENTE) with no signed contrato, then be unable to create a solicitud. Two 'firmado' notions are uncoupled.
- EstadoDocFirma transitions (PENDIENTE->ENVIADO->FIRMADO for estadoContrato/estadoPoder) have no state-machine spec or dedicated endpoint, and Open Q5 defers whether comercial.contrato.firmar exists. Yet FIRMADO is the gate for the whole bridge; its transition path is unspecified.
- Alertas: cuota-inicial-no-pagada depends on ConfiguracionCobro.fechaPrimerPago which is OPTIONAL — silently produces nothing if omitted (no note). cita-hoy restricts to REUNION/VIDEOLLAMADA, but SeguimientoComercial has no field marking a touch as a scheduled cita vs a logged past contact; fechaProximaTarea+tipoGestion conflate next-task and contact-medium. The cita semantics are under-modeled.
- Campos calculados: saldoPendiente is a serializer placeholder but, with no Pago/Cuota data in comercial, its computation is undefined (can only be full plan value or null). diasSinSeguimiento/diasEnFase/conversionACliente are well specified.
- The Proceso solicitudComercial back-relation is 1:1 (procesoId @unique). Prisma needs the inverse declared as a nullable single relation (Solicitud? on Proceso) with explicit one-to-one cardinality, not merely 'a virtual back-relation'. Three Usuario FKs (solicitadoPorId/asignadoPorId/abogadoAsignadoId) also require three NAMED relations + matching named back-relations on Usuario, which the proposal mentions only generically.
- ConfiguracionCobro adds OTRO to the doc's modality set {cuotalitis,cuota_mixta,prima_exito,fijo}; minor additive divergence, undocumented vs the source doc.
- seed RBAC grants comercial.cobro.configurar and comercial.contrato.* to COMERCIAL; since cobro is the contable-shared plan, a sales rep editing the binding cobro plan may cross the doc's contable boundary — confirm intended.

## Open questions (from synthesis)

- Contrato naming: ship ContratoComercial / contratos_comerciales now (recommended — verified no Contrato model exists today, but cobro is explicitly shared with a future contable module that will plausibly own its own Contrato, so the suffix is a cheap collision hedge), or keep bare Contrato and rename later? Confirm with the team that contable will indeed have its own contract concept.
- Fase initialization: does creating a Cliente (POST /clientes) auto-seed an initial LEAD FaseComercialHistorial row, or is the first fase row created lazily on the first POST /comercial/clientes/:id/fase? Recommend lazy creation so the clientes router stays untouched (no comercial coupling leaking into the foundations create path).
- Bridge codigoInterno generation: the assign transaction must generate a Proceso.codigoInterno unique per empresa and snapshot TipoProceso.esquemaVersion into tipoEsquemaVersion. Confirm the codigoInterno format/sequence policy (e.g. YYYY-NNNN per empresa) — this is the one place comercial writes into the legal module and is currently undefined. THE doc flags this whole bridge as 'MIRAR CON MARITZA'.
- Solicitud vs estado/fase authority on assign: confirm that ASIGNADA should also advance/confirm the funnel, and whether the abogado assignment is allowed to override the comercial-proposed tipoProcesoId (recommend: admin MAY override tipoProcesoId at assign time; the override is what materializes the Proceso).
- Is comercial.contrato.firmar / comercial.solicitud.cancelar needed as distinct permisos, or do .editar (state transitions incl. FIRMADO) and ADMINISTRADOR-gated rejection cover it? Recommend folding firmar into .editar and cancelar into .crear-owner scope to keep the permiso set lean, matching the lean cliente.* set.
- Does comercial need a per-fase or per-cotizacion responsable distinct from Cliente.responsableComercialId, or is reusing the existing Cliente.responsableComercialId + per-row registradoPorId sufficient? Recommend reuse (no extra responsable table) unless reps split work mid-funnel.
