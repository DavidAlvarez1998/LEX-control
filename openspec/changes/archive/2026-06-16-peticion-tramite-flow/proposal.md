# Proposal: Standard flow for entity-directed trámites (peticiones)

## Intent
Several catalog types are **trámites ante una entidad** (not judicial cases): `Derecho de Petición`,
`Reclamación Administrativa`, `Constitución de Renuencia`, `Derecho de Petición Recibido`. They share
the same shape: draft → file (radicar) → response → (reiterate | escalate to tutela) → close. This
change captures the **UX/data standard** already applied to `Derecho de Petición` and now mirrored to
`Reclamación Administrativa`, so future entity-trámites follow one consistent pattern.

## What changes (data-driven, no schema change)
1. **Field staging via `soloFicha`.** New per-field flag in `esquemaFormulario`. A `soloFicha` field is
   hidden in the **creation** form and only shown in the **ficha** when advancing stages. The radication
   and response fields (`fechaRadicacion`, `nroRadicado`, `contestaron`, response fields) are `soloFicha`
   — at creation you only draft the petition; you don't have the entity's radicado yet.
2. **Two distinct radicado dates.**
   - `fechaRadicado` ("Fecha de radicación de solicitud") — captured at creation; OUR reference of when
     the petition was drafted/sent. Does **not** start any term.
   - `fechaRadicacion` ("Fecha de radicación del proceso") — the entity's acuse-de-recibo date; **starts
     the legal term** (`plazoDesdeCampo`). Filled at the Radicación stage.
   - `nroRadicado` — the radicado number the **entity** assigns on receipt (radicado de recibido).
3. **Auto title for non-judicial types.** When `esJudicial = false`, the case `titulo` is auto-generated
   as `"{TipoProceso.nombre} — {entidad}"` and the manual title field is hidden at creation; it stays
   editable in the ficha.
4. **Stage naming.** The response stage is named **"Respuesta"** (was "Contestación").
   - Removed the informational field `respuestaDeFondo` ("¿Resolvió de fondo lo solicitado?"): it drove
     no gating/branch/template and was redundant with `contestaron` (SI/PARCIAL/NO). On `contestaron=SI`
     the stage now requires only `fechaRespuesta` + `respuesta.pdf`.
5. **Reiteración template gating.** Templates that reference `{{casoBase...}}` (the reiteración document)
   are only offered/generated on a **derived** trámite (`casoRelacionadoId != null`), never on the original.
6. **Responsible lawyer inherited on derivación.** When the reiteración/tutela derivative is created
   (`crearDerivado`), it inherits `responsableId` from the base trámite (same case, same lawyer).

## Scope
- `lex-control-api/prisma/seed-tipos.json`: applied to `Derecho de Petición` and `Reclamación
  Administrativa` (fields, `soloFicha`, labels, "Respuesta", optional `recurso.pdf` on PARCIAL).
- `lex-control-api` `procesos.router.ts`: template gating (GET /plantillas, POST /generar, /render) +
  `responsableId` inheritance in POST /derivar.
- `lex-control-client`: `CampoEsquema.soloFicha`; creation form filters `soloFicha` and auto-title for
  non-judicial; ficha `TituloEditable`; stage-advance scroll to first missing field; read-only summary
  hides empty fields; clearer 422 message ("solo aplica si X es Y — actualmente es Z").

## Out of scope / follow-ups
- Applying the same standard to `Constitución de Renuencia` and `Derecho de Petición Recibido` (incl. their
  generable templates).
- Editable responsable in the ficha + backfill of pre-fix derivatives.

## Rollback
Seed is idempotent (re-seed restores prior labels/flags). Client/API changes are additive; reverting the
commits restores the previous behavior with no data migration.
