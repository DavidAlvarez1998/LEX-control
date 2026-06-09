# Apply Progress: legal-tramites

Jurisdiction: **Colombia**. Delivery: **UX-first**, then backend, then catalog/admin.
Status snapshot — Phases 1–3 applied & verified; Phases 4–5 pending.

## Phase 1 — Client UX prototype ✅ (was mock, now wired)
`lex-control-client`:
- `components/form-ui.tsx` — NEW form primitives (the client app had none): `Field, Input, Textarea, NumberInput, Select, MultiSelect, Checkbox, MoneyInput, SelectableCard`.
- `components/formulario-dinamico.tsx` — generic renderer for any `esquemaFormulario`.
- `lib/tramites.ts` — TS contract (Colombian unions) + shared `validarDatos`. `Jurisdiccion` uses the API enum values (UPPERCASE).
- `lib/tramites-api.ts` — API client (replaced the localStorage mock, which was deleted).
- Routes `(dashboard)/tramites/{page, nuevo, [id]}` — list (filters), 3-step create (área → tipo → form + partes), expediente (rule-gated stage stepper). Forms centered `mx-auto max-w-4xl`.
- `Button` in `ui.tsx` extended (`type/onClick/disabled`); "Trámites" added to `nav.tsx`.
- Verify: `tsc` + `next build` clean.

## Phase 2 — Data layer + API ✅
`lex-control-api`:
- `prisma/schema.prisma` — models AreaPractica, TipoTramite (+TipoTramiteArea M:N), Tramite, EtapaTramite, DocumentoTramite, Litigante, ParteTramite, PlantillaDocumento + enums. `db push` OK (no errno 150). Cascades: Usuario→Tramite/EtapaTramite SetNull; ParteTramite→Litigante Restrict; `empresaKey` sentinel; per-empresa `codigoInterno`; `tipoEsquemaVersion` anti-drift.
- `middleware/auth.ts` — `requireAuth` now resolves `empresaId`+`esAdminEmpresa` per request (JWT is `{sub,rol}` only); new `requireEmpresaAdmin` + `empresaIdRequerido`.
- Modules: `catalog` (areas + tipos CRUD, global/own visibility), `tramites` (POST in `$transaction` with codigoInterno+partes+datos validation; GET list/by-id tenant-scoped; PATCH `/etapa` rule-gated; PATCH), `litigantes` (CRUD scoped). Shared validator `modules/tramites/esquema.ts`.
- Mounted in `app.ts`: `/catalogo`, `/litigantes`, `/tramites`.
- Verify: `tsc` clean; **79 tests pass** (8 new `tests/tramites.test.ts` + 71 existing intact).

## Phase 3 — Catalog (AI-seeded) + Admin builder ✅
- `prisma/seed-tipos.json` + `seed-catalogo.ts` (`pnpm seed:catalogo`) — AI-generated (6 research subagents) catalog: **16 áreas + 35 tipos globales** with complete forms + real Colombian stages and legal citations. **Pending lawyer review.**
- `lex-control-admin/src/app/(dashboard)/catalogo-tramites/page.tsx` — visual builder (form fields + stages). Users edit only labels; `key`s auto-derived; stage required-fields picked by chip. Added to admin `nav.tsx`.
- API ADMIN endpoints (create/edit/delete global) already existed in `catalog.router.ts`.
- Verify: admin `tsc` + `next build` clean.

## Phase 4 — Document templates + generation ✅
`lex-control-api`:
- `schema.prisma` — `DocumentoProceso` got `contenido @db.Text` (editable generated draft) + `updatedAt`; `url` now nullable (attachments have url, drafts have contenido). `db push` OK.
- `modules/procesos/plantilla.ts` — NEW pure template engine (Decisión 9). Handlebars-style: `{{datos.*}}`, `{{proceso.*}}`/`{{tramite.*}}` (alias), `{{parte.<rol>.<field>}}`, `{{#if}}…{{else}}…{{/if}}`, `{{#each list}}…{{@index}}…{{this}}…{{/each}}`; helpers `moneda` (1.000.000), `enLetras` (number→words, art. 623 C.Co), `fecha`, `mayus`. Unresolved placeholder → visible marker `[[falta: <path>]]` (never throws; broken syntax does). `construirContexto(proceso)` builds the namespace from proceso + partes.litigante.
- `modules/catalog` — plantilla CRUD nested on a tipo: GET/POST `/catalogo/tipos-proceso/:id/plantillas`, PATCH/DELETE `/catalogo/plantillas/:plantillaId` (reuse `esVisible`/`autorizarEscritura`).
- `modules/procesos` — documentos on the expediente: GET `/:id/plantillas` (picker), POST `/:id/documentos` (attach link), POST `/:id/documentos/generar` (render+persist; plantilla must belong to the proceso's tipo), PATCH/DELETE `/:id/documentos/:docId` (tenant-scoped). `detalleInclude` returns `documentos`. **Stage transition now also enforces `documentosRequeridos`** (400 with `documentosFaltantes`, name-match case-insensitive).
- Verify: `tsc` clean; **260 tests** (was 228 + 22 `plantilla.test.ts` + 10 new doc/plantilla/etapa cases).

`lex-control-client`:
- `lib/procesos-api.ts` — `DocumentoProceso` type + `documentos` on `ProcesoDetalle`; helpers `getPlantillasDeProceso`/`generarDocumento`/`adjuntarDocumento`/`editarDocumento`/`eliminarDocumento`.
- `components/documentos-proceso.tsx` — NEW: list (draft vs attachment), generate-from-template, attach-by-link, inline draft editor, delete. Wired into `/procesos/[id]`. `next build` clean.

`lex-control-admin`:
- `catalogo-procesos/page.tsx` — "Plantillas" button per tipo → modal: list + create/edit/delete templates, textarea editor + `<details>` marker cheat-sheet (the tipo's `datos.<key>` + helpers/blocks). `next build` clean.

## Pending
- **Phase 5** — state integrations (`integraciones-estatales` spec): CPNU (scrape) + Corte Constitucional SODA (api) + RUES (aggregator); `ActuacionJudicial`/`ProviderConfig` models.
- **Verify** — manual runtime cross-tenant check; lawyer review of catalog accuracy.
- Admin stage builder does not yet expose a `documentosRequeridos` picker (rule is enforced + seedable, not yet UI-editable).

## Notes
- "Samai": the product's billable AI doc-reader service is UNRELATED to the judicial SAMAI (Consejo de Estado) and is NOT used to brand any AI feature (per product owner). See design.md Decision 12.
- The user enhanced `auth.ts` mid-stream to also revoke users when their empresa is deactivated (compatible with the empresaId/esAdminEmpresa additions).
