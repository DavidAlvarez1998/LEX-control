# Acción de tutela

Mecanismo constitucional judicial (grupo `CONSTITUCIONAL`, jurisdicción `CONSTITUCIONAL`, área `constitucional`) para la protección inmediata de derechos fundamentales vulnerados o amenazados (art. 86 C.P.; Decreto 2591/1991). El despacho representa al **cliente accionante** y sigue el proceso desde la radicación hasta el fallo, la impugnación y la eventual remisión a la Corte Constitucional para revisión. El juez debe fallar dentro de los 10 días hábiles siguientes a la presentación.

## Fases de este caso

| Fase | Etapas (key) | Qué ocurre |
|------|--------------|------------|
| 1. Presentación / Radicación | `radicacion` | Se radica la demanda de tutela (+pruebas/anexos); arranca el plazo de fallo (10 días hábiles desde `fechaPresentacion`). |
| 2. Admisión / Traslado | `admision` | El juez admite y corre traslado al accionado (auto admisorio si fue admitida). |
| 3. Fallo de 1ª instancia | `falloPrimeraInstancia` | El juez falla (favorable/desfavorable); se registra la sentencia. |
| 4. Impugnación | `impugnacion` | Sólo si se impugnó: se surte el recurso (3 días hábiles para impugnar). |
| 5. Fallo de 2ª instancia | `falloSegundaInstancia` | El superior resuelve la impugnación; puede haber incidente de desacato. |
| 6. Remisión a revisión | `remisionRevision` | Expediente remitido a la Corte Constitucional para eventual revisión. |
| 7. Cierre | `terminado` | Terminal: tutela resuelta (eventualmente revisada por la Corte). |

> Nota: el flujo es **lineal por orden** (1→7). No hay ramas excluyentes con mismo `orden`; la única etapa **condicional** es `impugnacion` (`disponibleSi impugnada == SI`). Todas las decisiones (admitida, fallo, impugnada, fallo 2ª, desacato) se diligencian como **campos de ficha `soloFicha`** que no ramifican etapas, sólo muestran/ocultan otros campos y habilitan documentos opcionales. No hay acción `crearDerivado` (la tutela es el destino de escalamiento, no escala a otro tipo).

## Grafo del flujo

```
1) RADICACIÓN Y REPARTO (radicacion)        campos req: entidadAccionada
       │                                     📎 demanda.pdf (req) · pruebas.pdf, anexos.pdf (opc)
       │                                     ⏱ desde fechaPresentacion, 10 días HÁBILES (fallo)
       ▼
2) ADMISIÓN Y TRASLADO (admision)           campos req: entidadAccionada
       │   [ficha: ¿Admitieron la tutela? admitida = SI / NO]
       │      └ SI → 📎 auto_admisorio.pdf (opc) + fechaAutoAdmisorio
       ▼
3) FALLO 1ª INSTANCIA (falloPrimeraInstancia)   ⏱ plazoDias 10
       │   [ficha: falloPrimera = Favorable / Desfavorable]
       │      └ (cualquiera) → 📎 sentencia.pdf (opc) + fechaFallo
       ▼
   [ficha: ¿Se impugnó? impugnada = SI / NO]
       ├ NO  → (salta impugnación)
       │
       ▼ SI
4) IMPUGNACIÓN (impugnacion)  disponibleSi impugnada == SI   ⏱ plazoDias 3
       │   (ficha: fechaImpugnacion — 3 días háb. desde notificación del fallo)
       ▼
5) FALLO 2ª INSTANCIA (falloSegundaInstancia)   ⏱ plazoDias 20
       │   [ficha: falloSegunda = Favorable / Desfavorable (mostrarSi impugnada==SI)]
       │   [ficha: ¿Incidente de desacato? incidenteDesacato = SI / NO]
       │      └ SI → 📎 escrito_desacato.pdf, fallo_desacato.pdf (opc) + fechaIncidenteDesacato
       ▼
6) REMISIÓN A REVISIÓN (remisionRevision)   ⏱ plazoDias 10
       │   (remisión a la Corte Constitucional para eventual revisión)
       ▼
7) TERMINACIÓN (terminado)  terminal ✔
       resultado: "Tutela resuelta (eventualmente revisada por la Corte Constitucional)."
```

## Detalle por etapa (campo por campo)

Campos del esquema (todos `soloFicha` salvo donde se indique; sólo `entidadAccionada` es `requerido:true` global):

- **entidadAccionada** [texto] (obligatorio) — Autoridad o particular accionado. (NO es soloFicha; se pide al crear.)
- **derechosFundamentales** [multiselect] (opcional, ficha) — Vida · Salud · Dignidad humana · Debido proceso · Petición · Igualdad · Mínimo vital · Educación · Trabajo · Seguridad social · Libre desarrollo de la personalidad · Acceso a la administración de justicia · Otro.
- **hechos** [textoLargo] (opcional, ficha).
- **pretension** [textoLargo] (opcional, ficha) — Pretensión / amparo solicitado.
- **existeOtroMedioDefensa** [boolean] (opcional, ficha) — ¿Existe otro medio de defensa judicial?
- **perjuicioIrremediable** [boolean] (opcional, ficha) — ¿Se alega perjuicio irremediable?
- **medidaProvisional** [boolean] (opcional, ficha) — ¿Se solicita medida provisional?
- **juramentoNoTutela** [boolean] (opcional, ficha) — Juramento de no haber presentado otra tutela por los mismos hechos.

### 1) Radicación y reparto — `radicacion` (orden 1)
Campos requeridos para avanzar: `entidadAccionada`.

Campos de ficha relevantes:
- **fechaPresentacion** [fecha] (opcional) — Fecha de presentación de la tutela. **Desde aquí corren los 10 días hábiles para el fallo.**
- **radicadoTutela** [numero] (opcional) — Radicado de la tutela.

Documentos requeridos: `demanda.pdf`.
Documentos opcionales: `pruebas.pdf`, `anexos.pdf`.
Plazo: `plazoDesdeCampo = fechaPresentacion`, `plazoTipoDias = habiles`, `plazoDias = 10`.

### 2) Admisión y traslado al accionado — `admision` (orden 2)
Campos requeridos: `entidadAccionada`.

Campo de ficha que controla visibilidad/documento:
- **admitida** [select] (opcional) — ¿Admitieron la tutela? [SI / NO]
  - **SI** → muestra **fechaAutoAdmisorio** [fecha] (`mostrarSi admitida==SI`) y habilita documento opcional **auto_admisorio.pdf** (`opcionalesSi admitida==SI`).
  - **NO** → no muestra fecha ni habilita el auto admisorio.

Sin documentos requeridos. Documento opcional condicional: `auto_admisorio.pdf` (sólo si admitida==SI).

### 3) Fallo de primera instancia — `falloPrimeraInstancia` (orden 3)
Sin campos requeridos.

Campos de ficha:
- **falloPrimera** [select] (opcional) — Fallo de primera instancia [Favorable / Desfavorable]
  - cualquiera de los dos valores → muestra **fechaFallo** [fecha] (`mostrarSi falloPrimera ∈ {Favorable, Desfavorable}`) y habilita documento opcional **sentencia.pdf** (`opcionalesSi falloPrimera ∈ {Favorable, Desfavorable}`).

Plazo: `plazoDias = 10`.
Documento opcional condicional: `sentencia.pdf`.

### 4) Impugnación — `impugnacion` (orden 4)
**`disponibleSi`: `impugnada == SI`** (única etapa condicional; se salta si no se impugnó).

Campos de ficha (no en esta etapa por reglas, pero ramifican el flujo):
- **impugnada** [select] (opcional) — ¿Se impugnó el fallo? [SI / NO]
  - **SI** → muestra **fechaImpugnacion** [fecha] (ayuda: "3 días hábiles desde la notificación del fallo") y **falloSegunda** [select] [Favorable / Desfavorable]. Además habilita la etapa `impugnacion`.
  - **NO** → no muestra fecha ni fallo de 2ª; la etapa `impugnacion` no se ofrece.

Plazo: `plazoDias = 3`. Sin campos ni documentos requeridos en la etapa.

### 5) Fallo de segunda instancia — `falloSegundaInstancia` (orden 5)
Sin campos requeridos.

Campos de ficha:
- **falloSegunda** [select] (opcional) — Fallo de segunda instancia [Favorable / Desfavorable] (`mostrarSi impugnada==SI`).
- **incidenteDesacato** [select] (opcional) — ¿Se promovió incidente de desacato? [SI / NO]
  - **SI** → muestra **fechaIncidenteDesacato** [fecha] (`mostrarSi incidenteDesacato==SI`) y habilita documentos opcionales **escrito_desacato.pdf**, **fallo_desacato.pdf** (`opcionalesSi incidenteDesacato==SI`).
  - **NO** → no muestra fecha ni habilita esos documentos.

Plazo: `plazoDias = 20`.
Documentos opcionales condicionales: `escrito_desacato.pdf`, `fallo_desacato.pdf` (sólo si incidenteDesacato==SI).

### 6) Remisión a la Corte Constitucional para eventual revisión — `remisionRevision` (orden 6)
Sin campos ni documentos requeridos. Plazo: `plazoDias = 10`. Representa el envío del expediente a la Corte para selección/eventual revisión.

### 7) Terminación — `terminado` (orden 7)
`terminal: true`. Resultado: "Tutela resuelta (eventualmente revisada por la Corte Constitucional)." Sin campos ni documentos.

## Desenlaces posibles

1. **Terminación normal** (`terminado`) — único terminal real. Se llega siempre por la línea, con o sin impugnación, tras la remisión a revisión.
2. **Sin impugnación** — si `impugnada == NO`, la etapa `impugnacion` no se ofrece; el flujo pasa de fallo de 1ª a fallo de 2ª/remisión y cierra (el seed no bifurca a un cierre temprano: el orden lineal sigue hacia `remisionRevision`→`terminado`).
3. **Con impugnación** — `impugnada == SI` habilita `impugnacion` (⏱3 días), luego fallo de 2ª (⏱20) y remisión (⏱10).
4. **Incidente de desacato** — no es un terminal ni una rama de etapa: es un campo de ficha en `falloSegundaInstancia` que sólo agrega documentos opcionales (escrito/fallo de desacato). No abre etapa propia.

No hay escalamiento (`crearDerivado`): la tutela es el destino al que escalan DdP / reclamación / renuencia, no un origen.

## Conformidad con el doc Juan David

Sección fuente: bloque autónomo "ACCIÓN DE TUTELA" (fuente-juan-david.txt líneas 204-234), además de las versiones embebidas que cuelgan de NO/PARCIAL del DdP (líneas 28-60, 94-122, 152-180).

### Coincidencias
- "Acción de tutela – Cargar PDF (enlace de tutela)" + **Demanda PDF / Pruebas PDF / Anexos PDF** → `demanda.pdf` (requerido) + `pruebas.pdf`, `anexos.pdf` (opcionales) en `radicacion`.
- **Radicado de la tutela (numérico)** → `radicadoTutela` [numero].
- **ADMITIERON LA TUTELA – SI/NO** → `admitida` [select SI/NO]; **Auto admisorio PDF + Fecha Auto Admisorio** → `auto_admisorio.pdf` (opc) + `fechaAutoAdmisorio`, condicionados a admitida==SI.
- **FALLO Favorable/Desfavorable + PDF sentencia + Fecha del fallo** → `falloPrimera` + `sentencia.pdf` + `fechaFallo`.
- **IMPUGNACIÓN SI/NO; SI → Fecha** → `impugnada` + `fechaImpugnacion` (3 días háb.); la etapa `impugnacion` se gatea con `disponibleSi impugnada==SI`.
- **FALLO DE SEGUNDA INSTANCIA Favorable/Desfavorable** → `falloSegunda`.
- **INCIDENTE DE DESACATO SI/NO; SI → Fecha; SI SI → Escrito PDF, Fallo PDF** → `incidenteDesacato` + `fechaIncidenteDesacato` + `escrito_desacato.pdf` + `fallo_desacato.pdf`.
- Plazo de fallo de 10 días hábiles desde la presentación → `plazoDesdeCampo=fechaPresentacion` (10 hábiles) en `radicacion`.

### Huecos / inconsistencias (el doc pide y el seed NO modela, o al revés)
1. **El doc no separa "Auto admisorio – Fecha"**: la versión embebida (líneas 28-60) trae el auto admisorio **sin** fecha; la versión autónoma (línea 214) sí incluye "Fecha Auto Admisorio". El seed sigue la versión completa (incluye `fechaAutoAdmisorio`). Sin hueco; anotado.
2. **`derechosFundamentales`, `hechos`, `pretension`, `existeOtroMedioDefensa`, `perjuicioIrremediable`, `medidaProvisional`, `juramentoNoTutela`**: el seed agrega estos campos sustantivos (propios de una demanda de tutela bien armada) que **el doc Juan David NO lista** (el doc trata la demanda como un PDF a adjuntar, no como campos a tipear). Es enriquecimiento del seed sobre el doc; coherente con la decisión "doc = adjuntar PDF, no tipear", pero son campos extra que el doc no pide.
3. **Etapas `admision`, `remisionRevision` y la línea procesal**: el doc describe la tutela como una lista de campos/PDF (radicado, admitieron, fallo, impugnación, 2ª instancia, desacato) sin estructurarla en etapas de "admisión y traslado" ni "remisión a la Corte para revisión". El seed las modela como etapas con plazos (admisión sin plazo, remisión 10 días). La **remisión a revisión** no aparece en el doc → es agregado del seed (fiel a la ley, no al doc).
4. **Plazos `plazoDias` 10/3/20/10 en etapas posteriores**: el doc sólo fija explícitamente el plazo de fallo (10 háb. desde presentación) y "3 días para impugnar". Los `plazoDias` de fallo 1ª (10), fallo 2ª (20) y remisión (10) son agregados del seed sin respaldo textual en el doc, y `plazoTipoDias` no está fijado en esas etapas (sólo en `radicacion`) → quedan ambiguos (¿hábiles o calendario?). Inconsistencia menor de modelado: contradice "donde el doc calle, preguntar; no asumir".
5. **`impugnada`/`falloSegunda`/`incidenteDesacato` no ramifican etapas**: el doc presenta la tutela como bifurcaciones (SI/NO) que abren más campos; el seed sólo gatea **una** etapa condicional (`impugnacion` por `impugnada==SI`) y resuelve el resto con `mostrarSi`/`opcionalesSi`. Los demás "SI/NO" no crean ramas de etapa. Es decisión de diseño (ficha-céntrica), no hueco de datos, pero el flujo de etapas es más lineal que el árbol del doc.
6. **Sin etapa/terminal de "fallo desfavorable en firme" ni de "cumplimiento"**: el doc no lo pide y el seed no lo modela; el único terminal es `terminado`. Sin hueco respecto al doc; anotado por completitud.
7. **Documentos siempre OPCIONALES salvo `demanda.pdf`**: auto admisorio, sentencia, escrito/fallo de desacato son opcionales (no bloquean avance). El doc los lista como entregables sin marcarlos obligatorios → coincide; sin hueco.
