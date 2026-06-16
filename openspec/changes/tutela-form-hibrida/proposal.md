# tutela-form-hibrida

## Por qué

El documento de requerimientos del cliente `openspec/roadmap-docs/"DERECHO DE PETICIÓN -
JUAN DAVID.docx"` (fuente de verdad legal por encima de la interpretación) modela la
**Acción de tutela** como un **flujo de seguimiento corto**: en sus tres apariciones
(escalada de un DdP, renuencia Ley 393, y la sección "ACCIÓN DE TUTELA") siempre dice
*"Acción de tutela – Cargar PDF (enlace de tutela) / Demanda PDF / Pruebas PDF / Anexos
PDF"* + tracking (radicado → admitieron → auto admisorio → fallo → impugnación → 2ª
instancia → incidente de desacato). **Nunca** pide `hechos`/`pretensión`/`derechos
fundamentales` como campos del formulario: el abogado **redacta la demanda y la adjunta**,
no la tipea.

El catálogo actual, en cambio, traía un **intake sustantivo rico** (9 campos: accionado,
derechos fundamentales, hechos, pretensión, subsidiariedad, perjuicio irremediable,
medida provisional, juramento, fecha de presentación) que existía sobre todo para
**auto-generar** la demanda de tutela desde plantilla (`plantillas-seed.ts` →
`DEMANDA_TUTELA`). Esto sobre-modelaba lo que el doc pidió y hacía el formulario de
creación largo, justo lo contrario de "corto y simple".

Disyuntiva planteada: ¿modelo del doc (adjuntar, formulario corto, se pierde la
generación) vs. modelo actual (intake rico, genera la demanda)? **Decisión del usuario:
híbrido** — lo mejor de ambos sin perder nada.

## Qué cambia

### 1. Esquema de tutela = híbrido (form corto + capacidad de generación intacta)
En el `TipoProceso` "Acción de tutela" (`seed-tipos.json`, grupo CONSTITUCIONAL):
- **`entidadAccionada`** ("Autoridad o particular accionado") se **mantiene visible y
  requerido al crear** — es el único campo sustantivo en creación, e identifica la tutela
  (alimenta el título auto, ver §3).
- Los **8 campos sustantivos restantes** (`derechosFundamentales`, `hechos`, `pretension`,
  `existeOtroMedioDefensa`, `perjuicioIrremediable`, `medidaProvisional`,
  `juramentoNoTutela`, `fechaPresentacion`) y los **9 de tracking** (`radicadoTutela`,
  `admitida`, `fechaAutoAdmisorio`, `falloPrimera`, `fechaFallo`, `impugnada`,
  `falloSegunda`, `incidenteDesacato`, `fechaIncidenteDesacato`) pasan a
  **`soloFicha: true` + `requerido: false`**: no aparecen al crear (form corto, modelo
  doc) y se llenan en la ficha al avanzar de etapa.
- **La plantilla `DEMANDA_TUTELA` no se toca**: los campos siguen existiendo (solo
  opcionales/`soloFicha`), así que quien quiera que el sistema le redacte la demanda los
  llena en la ficha y genera. No se pierde la capacidad de generación.

### 2. Gate de etapas relajado al modelo doc (adjuntar, no tipear)
- Etapa `radicacion`: `camposRequeridos` pasa de
  `[derechosFundamentales, entidadAccionada, hechos, pretension, existeOtroMedioDefensa]`
  a **`[entidadAccionada]`**. El gate efectivo para avanzar es **accionado +
  `demanda.pdf`** (documento requerido ya existente) — adjuntas la demanda, no la tipeas.
- Etapa `falloPrimeraInstancia`: se quita `camposRequeridos: [pretension]` (ahora opcional);
  para registrar el fallo basta `sentencia.pdf`.
- Los documentos del doc **ya estaban modelados** en las etapas (`demanda.pdf`,
  `pruebas.pdf`, `anexos.pdf`, `auto_admisorio.pdf`, `sentencia.pdf`, `impugnacion.pdf`,
  `sentencia_segunda.pdf`, `escrito_desacato.pdf`, `fallo_desacato.pdf`): **no se agregan
  slots**.

### 3. Título del caso auto para acciones constitucionales (antes manual)
En el formulario de creación cliente (`procesos/nuevo/page.tsx`):
- El título de la tutela deja de pedirse a mano y se **auto-genera** `"Tipo — Entidad"`
  (p. ej. *"Acción de tutela — Colpensiones"*), igual que el DdP. Antes el flag
  `tituloAuto = !esJudicial` dejaba la tutela (judicial) con título manual.
- `tituloAuto = !esJudicial || grupo === "CONSTITUCIONAL"`; el campo "Título del caso" se
  oculta para CONSTITUCIONAL; `tituloGenerado` lee `entidad` (DdP) **o** `entidadAccionada`
  (tutela). Queda editable luego en la ficha (`TituloEditable`). El resto de judiciales
  (laboral/civil…) sigue con título manual.

## Impacto
- **Catálogo (`seed-tipos.json`)**: solo el tipo "Acción de tutela" (campos `soloFicha`/
  opcionales + 2 etapas con `camposRequeridos` relajados). **DdP, reclamación, renuencia,
  DdP recibido y "Acción de Tutela (Recibida)" NO se tocan** (tipos separados, esquemas
  independientes). Se aplica con re-seed (`pnpm seed:catalogo`).
- **Frontend cliente**: `procesos/nuevo/page.tsx` (título auto para CONSTITUCIONAL). La
  ficha (`DatosProceso`/`FormularioDinamico`) ya renderiza los `soloFicha` para edición →
  sin cambios.
- **Backend/plantillas**: sin cambios de código. `DEMANDA_TUTELA` intacta.
- **Sin schema**: ninguna columna/enum nuevo.

## Fuera de alcance
- "Acción de Tutela (Recibida)" (tutela defensiva): es otro tipo; si se quiere la misma
  simplificación, va aparte.
- La derivación DdP→tutela (`POST /procesos/:id/derivar`) ya auto-titula
  `"Acción de tutela — {título DdP}"` y copia `datos: []` → encaja con el híbrido sin
  cambios.

## Decisiones del usuario (2026-06-16)
- **Doc = fuente de verdad**: el modelo actual (intake rico) sobre-modelaba; el doc manda.
- **Híbrido** (vs. doc-puro que borra campos, vs. dejar el form largo actual): mantener los
  campos opcionales/`soloFicha` para no perder la generación de la demanda, con form de
  creación corto.
- **Título de tutela = auto** (vs. manual): consistente con el DdP, usa `entidadAccionada`.
