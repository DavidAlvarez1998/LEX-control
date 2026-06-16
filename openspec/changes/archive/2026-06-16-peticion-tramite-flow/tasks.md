# Tasks

## 1. Catalog (seed-tipos.json)
- [x] 1.1 `Derecho de Petición`: add `fechaRadicado`; `fechaRadicacion` → "del proceso" + `soloFicha` + ayuda; `nroRadicado`/`contestaron` → `soloFicha`; stage "Contestación" → "Respuesta".
- [x] 1.2 `Reclamación Administrativa`: same set of changes; add optional `recurso.pdf` on response=PARCIAL (parity with DdP).
- [x] 1.2b Remove `respuestaDeFondo` field + its `camposRequeridos` ref (DdP + Reclamación): unused, redundant with `contestaron`. SI now requires only `fechaRespuesta` + `respuesta.pdf`.
- [x] 1.3 `Reclamación Administrativa` templates (plantillas-seed.ts): "Reclamación administrativa" (base) + "Reiteración de la reclamación" (uses `{{casoBase...}}`).
- [x] 1.4 `Constitución de Renuencia`: fields + `soloFicha` + "Respuesta" + base template "Constitución de renuencia". Per the Juan David doc, plazo stays **15 días hábiles** and escalation stays **Acción de tutela** (doc is source of truth over the strict Ley 393 reading of 10 días / acción de cumplimiento).
- [x] 1.5 `Derecho de Petición Recibido`: `contestada` + `observacionContestacion` → `soloFicha`; stage "Contestación" → "Respuesta"; auto-title now uses `peticionario` (reception fields `radicadoIngreso`/`fechaRecepcion` stay at creation).
- [x] 1.6 Generable template for `Derecho de Petición Recibido` (our written response): plantilla "Respuesta a la petición recibida" en plantillas-seed.ts.

## 2. API (procesos.router.ts)
- [x] 2.1 GET `/:id/plantillas`: hide `{{casoBase}}` templates unless `casoRelacionadoId != null`.
- [x] 2.2 POST `/:id/documentos/generar` and `/render`: reject `{{casoBase}}` templates on non-derived (422).
- [x] 2.3 POST `/:id/derivar`: set `responsableId: proceso.responsableId` on the derivative.
- [x] 2.4 GET `/:id/caso`: expose resolved `radicado` (judicial column else `nroRadicado`/`radicadoIngreso`/`radicadoTutela`).

## 3. Client
- [x] 3.1 `CampoEsquema.soloFicha`; creation form filters it (render + validation).
- [x] 3.2 Auto title `"Tipo — Entidad"` for `esJudicial = false`; hide field at creation; `TituloEditable` in ficha.
- [x] 3.3 Stage-advance: scroll to first missing field (`data-campo` + center); clearer 422 message.
- [x] 3.4 Read-only summary hides empty fields; wide fields full-row; CasoChain shows radicado instead of `codigoInterno`.

## 4. Verify
- [x] 4.1 `pnpm seed:catalogo` re-applied; DB reflects fields/labels.
- [x] 4.2 API + client `tsc --noEmit` clean; routes compile (200).
- [x] 4.3 Smoke e2e por HTTP (scripts/smoke-peticion-flow.ts, 13/13): crear→radicar→respuesta→reiterar/escalar + plantillas + caso.

## 5. Archive
- [x] 5.1 Merge the delta into `openspec/specs/tramite-management/spec.md` and move this change to `archive/`.
