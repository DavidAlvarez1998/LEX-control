# Design: Derecho de Petición + deadline & conditional engine

## 1. Business-day deadlines (`diasHabiles.ts` + `proceso-vencimientos`)

### Colombian holidays (festivos)
A pure function `festivosColombia(year): Set<string>` returning ISO dates. Three groups:

1. **Fixed** (always on date): Año Nuevo 01-01, Trabajo 05-01, Independencia 07-20, Batalla de Boyacá
   08-07, Inmaculada Concepción 12-08, Navidad 12-25.
2. **Emiliani — moved to the next Monday** (Ley 51/1983): Reyes 01-06, San José 03-19, San Pedro y San
   Pablo 06-29, Asunción 08-15, Día de la Raza 10-12, Todos los Santos 11-01, Independencia de
   Cartagena 11-11.
3. **Easter-relative, then Emiliani-Monday-shifted where applicable**: Jueves/Viernes Santo (Easter −3/
   −2, kept on their day), Ascensión (Easter +43 → Monday), Corpus Christi (Easter +64 → Monday),
   Sagrado Corazón (Easter +71 → Monday). Easter via the Anonymous Gregorian (Meeus/Jones/Butcher)
   algorithm — no `Date.now`, pure on `year`.

`esDiaHabil(date)` = not Saturday/Sunday and not in `festivosColombia(date.year)`.
`sumarDiasHabiles(desde, n)` = advance `n` business days from `desde` (exclusive of `desde`).
`sumarDiasCalendario(desde, n)` for `tipoDias: 'calendario'`.

> All helpers are pure and unit-tested against an explicit expected festivo set for at least 2024–2027
> (the risk table calls this out — a wrong festivo is a wrong legal deadline).

### Deadline rule on an etapa — EXTENDS the existing `plazoDias`
> Reconciliation (found during validate): `reglasEtapaSchema` ALREADY has `plazoDias: positive int`,
> and `etapaDefSchema` already has `resultado: string`; `campoEsquema` already has `ayuda: string`. The
> existing `plazoDias` is **informational only** (no `fechaLimite` derivation, no business-day math, no
> source date) and is used across the 209 seeded tipos. We **extend** that rule rather than add a
> parallel `plazo` object, so existing rows keep validating and stay informational.

`reglasEtapaSchema` gains (all optional, additive):
```ts
{
  plazoDias?: number               // EXISTING — the fixed term (kept)
  plazoDesdeCampo?: string         // key of a `fecha` field in datos (e.g. "fechaRadicacion")
  plazoTipoDias?: 'habiles' | 'calendario'   // default 'calendario' (back-compat); legal terms use 'habiles'
  plazoDiasPorValorDe?: { campo: string; mapa: Record<string, number> }  // term by another field's value
}
```
A `fechaLimite` is derived **only when `plazoDesdeCampo` is present**. The term is
`plazoDiasPorValorDe.mapa[datos[campo]]` if set, else `plazoDias`. So a row with only `plazoDias`
(every seeded tipo today) stays informational — no behavior change. When a `Proceso` enters such an
etapa the router computes `fechaLimite = sumarDias{Habiles|Calendario}(datos[plazoDesdeCampo], term)`.
If the source field is empty the deadline is left null (not an error). Stored on `Proceso.fechaLimite`
so it is queryable for alerts. Manual override allowed (the field is writable; recompute only on stage
move, never clobbering a manual edit silently — see tasks).

### Deadline status (semáforo)
`GET /procesos/vencimientos` (despacho-scoped) buckets open procesos by `fechaLimite` vs today:
`vencido` (< today), `por_vencer` (≤ 3 business days), `al_dia` (otherwise / null). Mirrors the
comercial-alertas shape so the client can reuse its alert UI.

## 2. Conditional fields (`esquema.ts` + `tramite-catalog`)

Extend `CampoEsquema` (all optional, absent ⇒ today's behavior):
```ts
type Condicion = { campo: string; igualA: string | string[] }  // equality only
type CampoEsquema = {
  key; label; tipo; requerido; opciones?;
  mostrarSi?: Condicion       // field hidden unless condition holds
  requeridoSi?: Condicion     // required (additionally) when condition holds
}
```
`evaluarCondicion(cond, datos)` compares `String(datos[cond.campo])` against `igualA` (array ? includes
: equals) — the `String()` coercion matters because booleans like `requierePoder` arrive as `true`/
`false` and conditions are written `igualA: "true"`. A field is **effectively required** iff
`requerido === true` OR (`requeridoSi` present AND `evaluarCondicion(requeridoSi)`), AND it is currently
**visible** (`mostrarSi` absent OR true). `validarDatos` ignores hidden fields entirely
(no "faltante" for a hidden required field). The client `<FormularioDinamico>` uses the same evaluator
to hide/show and to mark the red asterisk dynamically — one shared helper, server is source of truth.

Etapa `reglas` gains conditional required lists (keep the flat ones for back-compat):
```ts
reglas: {
  camposRequeridos?: string[]
  documentosRequeridos?: string[]
  requeridosSi?: { si: Condicion; camposRequeridos?: string[]; documentosRequeridos?: string[] }[]
  plazo?: PlazoRegla
}
```

## 3. Stage branching & `crearDerivado` (`tramite-management`)

The stage graph is already non-linear (movement allowed; `terminal` closes). We add **value-guarded
availability** and a **derive action** rather than a full BPMN engine:

- `etapas[].disponibleSi?: Condicion` — the stage is only offered as a "next" when the condition over
  `datos` holds (e.g. `reiteracion` available only when `contestaron === 'PARCIAL'`; `escala_tutela`
  only when `contestaron === 'NO'`). Movement to a non-available stage is rejected 422 with a reason.
- `etapas[].accion?: { tipo: 'crearDerivado'; tipoDestinoNombre: string }` — entering the stage offers
  creating a derived `Proceso` of the named global tipo, with `casoRelacionadoId = origen.id`,
  `empresaId` inherited, a fresh `codigoInterno`. **Idempotent**: one derived proceso per
  `(casoRelacionadoId, tipoProcesoId)`; a repeat returns 409 with the existing id. This is exactly the
  schema's `casoRelacionado`/`derivados` relation — no new column.

## 4. Seed content (global, jurisdicción CONSTITUCIONAL)

> Both types: `jurisdiccion: "CONSTITUCIONAL"`, `areaSlugs: ["constitucional"]` (the seeded
> "Constitucional" área, `tipo JURISDICCION`, already exists; orden 7). No CONSTITUCIONAL tipo is
> seeded today (the 209 seeded tipos are civil/comercial/laboral/familia/administrativo/penal) — DdP and
> Tutela are the first. Seeded into `prisma/seed-tipos.json` and upserted idempotently by
> `(empresaKey="", nombre)` like the rest.

### Derecho de Petición
**esquemaFormulario** (keys): `entidad`(texto, req), `correo`(texto), `tipoPeticion`(select, req,
opciones `General|Documental|Consulta`), `queSolicita`(multiselect, req, opciones = doc checklist:
Información, Copia de documentos, Certificación, Historia laboral, Historia clínica, Estado de trámite,
Pago pendiente, Reconocimiento de derecho, Corrección de información, Habeas data, Solicitud laboral,
Salud, Seguridad social, Queja, Reclamo, Consulta, Otro), `detalle`(textoLargo),
`requierePoder`(boolean), `envio`(select `Físico|Correo electrónico`), `fechaRadicacion`(fecha),
`nroRadicado`(texto), `contestaron`(select `SI|PARCIAL|NO`, `mostrarSi` etapa-driven).

**etapas**:
1. `borrador` (orden 0) — req: entidad, tipoPeticion, queSolicita; doc `peticion.pdf`;
   `requeridosSi`: `{si:{campo:requierePoder,igualA:"true"}, documentosRequeridos:["poder.pdf"]}`.
2. `radicada` (orden 1) — req: fechaRadicacion, nroRadicado; `reglas`:
   `plazoDesdeCampo:"fechaRadicacion", plazoTipoDias:"habiles", plazoDiasPorValorDe:{ campo:"tipoPeticion",
   mapa:{General:15, Documental:10, Consulta:30} }`.
3. `respondida` (orden 2, terminal) — `disponibleSi:{campo:contestaron,igualA:"SI"}`.
4. `reiteracion` (orden 2) — `disponibleSi:{campo:contestaron,igualA:"PARCIAL"}`; doc `reiteracion.pdf`;
   own `plazo` recomputed from a new radicación (loops back conceptually to `radicada`).
5. `escala_tutela` (orden 3) — `disponibleSi:{campo:contestaron,igualA:"NO"}`;
   `accion:{tipo:"crearDerivado", tipoDestinoNombre:"Acción de Tutela"}`.
6. `terminada` (orden 4, terminal).

### Acción de Tutela
**esquemaFormulario**: `accionado`(texto, req), `derechoVulnerado`(textoLargo, req),
`radicadoTutela`(texto), `admitida`(select `SI|NO`), `falloPrimera`(select `Favorable|Desfavorable`),
`impugnada`(select `SI|NO`), `falloSegunda`(select `Favorable|Desfavorable`).
**etapas**: `presentada` → `admitida`(req auto admisorio pdf; `plazo` 10 días hábiles for fallo) →
`fallo_primera` → `impugnacion` (`disponibleSi:{campo:impugnada,igualA:"SI"}`) → `segunda_instancia` →
`terminada`(terminal). Documents: demanda.pdf, pruebas.pdf, anexos.pdf, auto_admisorio.pdf,
sentencia.pdf, sentencia_segunda.pdf as `documentosRequeridos` on the matching stages.

## 5. Why not a separate module
DdP/tutela reuse `Proceso`, `EtapaProceso`, `DocumentoProceso`, `PlantillaDocumento`, `Litigante`/
`ParteProceso`, the dynamic-form renderer and the stage engine verbatim. A separate module would
duplicate all of that. The only genuinely missing primitives (business-day deadlines, conditional
rules, derive action) are cross-cutting and benefit every tipo — so they extend the engine.
