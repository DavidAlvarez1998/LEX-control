# Design — procesos-laborales

Fuente de verdad: `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`
(Ley 2452/2025; CPTSS). Este documento traduce ese flujo al modelo data-driven existente
(un `TipoProceso` en `seed-tipos.json`: `esquemaFormulario` + `etapas` + `reglas`).

## 1. Por qué un solo tipo y cómo se evita el AND

El documento abre con dos elecciones que ramifican todo:

- **Rol**: Demandante | Demandado
- **Tipo de instancia**: Única instancia | Doble instancia

El motor (`esquema.ts`) solo evalúa **igualdad sobre un campo** (`mostrarSi`/`requeridoSi`/
`disponibleSi`/`requeridosSi[].si`); **no hay AND/OR**. La regla de diseño que mantiene
todo data-driven, sin tocar el motor, es:

> **Las ETAPAS se ramifican únicamente por `tipoInstancia`. Los CAMPOS se ramifican por
> `rol` o por una decisión puntual (`decisionAdmision`, `contestaron`, …). Nunca se
> necesita "rol Y instancia" en el mismo gate.**

Esto funciona porque, al leer el documento, la **secuencia de etapas** difiere por
instancia (la doble añade contestación-detalle, reconvención y la doble audiencia
art. 77 + art. 80; la única colapsa en una sola audiencia y usa reposición). El **rol**
casi no cambia la secuencia: ajusta etiquetas y un par de campos de perspectiva
(demandante "presenta" vs. demandado "es notificado / contesta"), que se resuelven con
`mostrarSi: { campo: "rol", … }` a nivel de campo. Cuando un campo es propio de la doble
instancia (p. ej. `hayReconvencion`), se gatea con `mostrarSi: { campo: "tipoInstancia",
igualA: "Doble instancia" }`; los campos que dependen de él (`decisionReconvencion`) se
gatean con `mostrarSi: { campo: "hayReconvencion", igualA: "SI" }` — transitivamente
doble-only, **una sola condición cada uno**.

Campos built-in del tipo judicial (`esJudicial = true`): **radicado (23 dígitos), juzgado/
corporación y cuantía** los renderiza el formulario judicial existente (ver
[[tipo-proceso-es-judicial]]); NO se redefinen en `esquemaFormulario`.

## 2. Árbol de etapas (orden + ramas por `tipoInstancia`)

Convención: etapas con el **mismo `orden`** y distinto `disponibleSi` son ramas
alternativas del mismo paso (igual que `reiteracion`/`escala_tutela` en el DdP). El motor
ofrece como "siguiente etapa" las de orden creciente cuyo `disponibleSi` se cumple.

```
orden 0  presentacion         (ambos)  Presentación y radicación de la demanda
orden 1  admision             (ambos)  Calificación de la demanda → decisionAdmision
orden 2  subsanacion          rama: decisionAdmision = INADMISIÓN   (plazo 5 días háb.)
orden 2  recurso_rechazo      rama: decisionAdmision = RECHAZO      → favorable sigue / desfavorable archiva
orden 3  traslado             (ambos)  Traslado y notificación      (plazo 10 días háb. → contestación)
orden 4  contestacion         rama: tipoInstancia = Doble instancia (contestación, reforma, reconvención)
orden 5  preparacionAudiencia (ambos)  Preparación de la audiencia (¿conciliable?, documentos)
orden 6  citacionAudiencia    (ambos)  Citación a audiencia (fecha + auto de citación)
orden 7  audienciaUnica       rama: tipoInstancia = Única instancia (conciliación→…→sentencia en una)
orden 7  audienciaArt77       rama: tipoInstancia = Doble instancia (conciliación, excepciones, saneamiento, fijación, decreto)
orden 8  audienciaArt80       rama: tipoInstancia = Doble instancia (práctica de pruebas, alegatos, sentencia)
orden 9  sentencia            (ambos)  Sentencia + recurso (reposición en única / apelación en doble)
orden 10 archivado            rama: hayRetiro = SI   (terminal: retiro art. 67)
orden 10 terminada            (ambos) terminal general (firmeza / fin del proceso)
```

Recorrido **Única**: 0 → 1 → (2 subsanacion/recurso_rechazo si aplica) → 3 → 5 → 6 → 7
audienciaUnica → 9 sentencia → 10 terminada. (4 contestacion y 7-art77/8-art80 quedan
ocultas por `disponibleSi`.)

Recorrido **Doble**: 0 → 1 → (2 si aplica) → 3 → 4 contestacion → 5 → 6 → 7 art77 → 8 art80
→ 9 sentencia → 10 terminada.

En cualquier punto previo a la sentencia, si `hayRetiro = SI` (art. 67) se habilita la
etapa terminal `archivado`.

## 3. Reglas por etapa (campos requeridos, documentos, plazos)

| Etapa | `disponibleSi` | Requeridos / docs | Plazo derivado |
|---|---|---|---|
| `presentacion` | — | campos: `rol`, `tipoInstancia`, `pretensiones`, `hechos`; doc `demanda.pdf`; `requeridosSi requierePoder=true → poder.pdf` | — |
| `admision` | — | campo `decisionAdmision`; doc `auto-admision.pdf` | — |
| `subsanacion` | `decisionAdmision = INADMISIÓN` | campos `fechaSubsanacion`, `decisionTrasSubsanacion`; doc `subsanacion.pdf` | `plazoDesdeCampo: fechaInadmision`, `plazoTipoDias: habiles`, `plazoDias: 5` |
| `recurso_rechazo` | `decisionAdmision = RECHAZO` | campos `recursoRechazo`, `decisionRecursoRechazo`; doc `recurso.pdf` | `plazoDesdeCampo: fechaAuto`, `plazoTipoDias: calendario`, `plazoDias: 3` |
| `traslado` | — | campo `fechaNotificacion`; doc `notificacion.pdf` | `plazoDesdeCampo: fechaNotificacion`, `plazoTipoDias: habiles`, `plazoDias: 10` |
| `contestacion` | `tipoInstancia = Doble instancia` | `requeridosSi contestaron=SI → fechaContestacion + contestacion.pdf`; `contestaron=NO → auto-silencio.pdf`; `opcionalesSi hayReforma=SI → demanda-reformada.pdf`; `hayReconvencion=SI → reconvencion.pdf` | — |
| `preparacionAudiencia` | — | campo `conciliable`; `opcionalesSi → documentos-audiencia.pdf` | — |
| `citacionAudiencia` | — | campo `fechaAudiencia`; doc `auto-citacion.pdf` | — |
| `audienciaUnica` | `tipoInstancia = Única instancia` | campos de acta (conciliación, excepciones, saneamiento, fijación, pruebas, alegatos); doc `acta-audiencia.pdf` | — |
| `audienciaArt77` | `tipoInstancia = Doble instancia` | `conciliacionResultado`, `excepcionesPrevias`, `saneamiento`, `fijacionLitigio`, `decretoPruebas`; doc `acta-art77.pdf` | — |
| `audienciaArt80` | `tipoInstancia = Doble instancia` | `practicaPruebas`, `alegatos`; doc `acta-art80.pdf` | — |
| `sentencia` | — | campos `fechaSentencia`, `decisionSentencia`, `hayRecurso`; doc `sentencia.pdf`; `opcionalesSi hayRecurso=SI → recurso.pdf` | `plazoDesdeCampo: fechaSentencia`, `plazoTipoDias: calendario`, `plazoDias: 3` (recurso por escrito) |
| `archivado` | `hayRetiro = SI` | — | terminal (`resultado: "Demanda retirada y archivada (art. 67)"`) |
| `terminada` | — | — | terminal (`resultado: "Proceso terminado"`) |

> Nota sobre plazos condicionales: `subsanacion` y `recurso_rechazo` solo se entran cuando
> su campo fuente (`fechaInadmision` / fecha del rechazo) existe, así que `derivarFechaLimite`
> recibe siempre una fecha válida — igual patrón que `radicada` en el DdP.

## 4. `esquemaFormulario` (campos, agrupados por bloque)

**Selección inicial (ramifican todo):**
- `rol` — select [Demandante, Demandado], requerido
- `tipoInstancia` — select [Única instancia, Doble instancia], requerido

**Demanda (creación):**
- `pretensiones` — multiselect (reusa lista laboral: cesantías, primas, indemnizaciones art. 64/65, etc.), requerido
- `hechos` — textoLargo, requerido
- `requierePoder` — boolean
- (built-in judicial: radicado, juzgado/corporación, cuantía)

**Admisión (`soloFicha`):**
- `decisionAdmision` — select [ADMISIÓN, INADMISIÓN, RECHAZO]
- `fechaAuto` — fecha
- `fechaInadmision` — fecha, `mostrarSi decisionAdmision=INADMISIÓN`
- `decisionTrasSubsanacion` — select [ADMISIÓN, RECHAZO], `mostrarSi decisionAdmision=INADMISIÓN`
- `recursoRechazo` — select [Reposición, Apelación, Ninguno], `mostrarSi decisionAdmision=RECHAZO`
- `decisionRecursoRechazo` — select [Favorable, Desfavorable], `mostrarSi decisionAdmision=RECHAZO`
- `observacionesAdmision` — textoLargo

**Retiro (art. 67):**
- `hayRetiro` — select [SI, NO], `soloFicha`

**Traslado / notificación (`soloFicha`):**
- `fechaNotificacion` — fecha (fuente del plazo de 10 días hábiles)

**Contestación (doble; `mostrarSi tipoInstancia=Doble instancia`, `soloFicha`):**
- `contestaron` — select [SI, NO]
- `fechaContestacion` — fecha, `mostrarSi contestaron=SI`
- `hayReforma` — select [SI, NO]  (+ `fechaReforma` mostrarSi hayReforma=SI)
- `hayReconvencion` — select [SI, NO]
- `decisionReconvencion` — select [ADMITIR, INADMITIR, RECHAZAR], `mostrarSi hayReconvencion=SI`
- `contestacionReconvencion` — select [SI, NO], `mostrarSi hayReconvencion=SI`

**Preparación / citación (`soloFicha`):**
- `conciliable` — select [SI, NO]
- `fechaAudiencia` — fecha

**Audiencia (`soloFicha`):** campos de acta (textoLargo/select) — para única todos en una;
para doble repartidos entre art. 77 (`conciliacionResultado`, `excepcionesPrevias`,
`saneamiento` [SI/NA/NO], `fijacionLitigio`, `decretoPruebas`) y art. 80 (`practicaPruebas`,
`alegatos`). Cada uno con su `mostrarSi tipoInstancia=…`.

**Sentencia y recurso (`soloFicha`):**
- `fechaSentencia` — fecha
- `decisionSentencia` — select [Favorable, Desfavorable]
- `hayRecurso` — select [SI, NO]
- `medioRecurso` — select [En audiencia, Por escrito (3 días)], `mostrarSi hayRecurso=SI`
  (en única se rotula "Reposición"; en doble "Apelación", vía `ayuda`/etiqueta por instancia)
- `decisionRecurso` — select [Favorable, Desfavorable], `mostrarSi hayRecurso=SI`

## 5. Taxonomía y navegación (frontend)

- `GrupoProceso += LABORAL` (`schema.prisma`); el tipo de TS espejo en
  `lib/procesos.ts` (`type GrupoProceso`) suma `"LABORAL"`.
- `SECCION_RUTA["LABORAL"] = "/procesos-laborales"`; `rutaProceso` ya enruta por grupo.
- `nav.tsx`: nuevo ítem `{ href: "/procesos-laborales", label: "Procesos Laborales",
  roles: ["JURIDICO"] }` **debajo** del de Acciones Constitucionales.
- Rutas nuevas en `(dashboard)/procesos-laborales/`: `page.tsx` (lista, filtra
  `grupo === "LABORAL"`), `nuevo/page.tsx` (tipo bloqueado a "Proceso Laboral", estilo
  `/peticiones/nueva?tipo=ID`), `[id]/page.tsx` (ficha; reusa la ficha de proceso).
- `/procesos/nuevo`: filtrar `esJudicial && grupo === "JUDICIAL"` para que los laborales
  no aparezcan en el wizard genérico.
- RBAC: sección visible a `JURIDICO` (y admin de empresa). Sin permisos nuevos —
  reusa `proceso.ver/crear/editar` ([[procesos-rbac]]).

## 6. Riesgos y mitigaciones

- **Aparece un caso que sí requiera rol Y instancia juntos.** No se detectó en el
  documento. Si surgiera, el plan B es duplicar el campo afectado (uno por rol) o, como
  último recurso, extender `Condicion` a una lista AND — cambio pequeño y localizado en
  `evaluarCondicion`. **No se hace ahora.**
- **`fechaLimite` con fuente vacía.** Mitigado poniendo `plazoDesdeCampo` solo en etapas
  que ya garantizan la fecha (`subsanacion`, `traslado`), nunca en etapas comunes.
- **Stub "Proceso ordinario laboral de primera instancia" duplica intención.** Se elimina
  del seed (o se renombra a "(obsoleto)") al implementar, para no ofrecer dos flujos
  ordinarios. Decisión a confirmar en el apply.
- **`grupo` de los stubs laborales restantes** (ejecutivo, fuero, invalidez) hoy es
  JUDICIAL por defecto → seguirían en la sección "Procesos". Se dejan así en v1 (fuera de
  alcance); migrarlos a LABORAL es un follow-up.
