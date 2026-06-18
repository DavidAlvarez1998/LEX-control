# Validación de conformidad — Proceso Laboral vs. documento

Fuente: `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`.
Estado del modelo: seed-tipos.json "Proceso Laboral" (32 campos, 15 etapas).
Fecha de la auditoría: 2026-06-17.

## Por qué hay "tantos campos de fecha"

No son inventados: **el documento pide una fecha en casi cada etapa**, y cada una es una
fecha procesal distinta. Mapeo 1:1:

| Fecha del doc | Campo impl |
|---|---|
| Fecha de radicación de la demanda (doc 14) | `fechaRadicacion` |
| Fecha del auto de calificación (doc 19, 76, 193) | `fechaAdmision` |
| Fecha para subsanar = 5 días háb. (doc 23) | *calculada* (no es campo: hint ⏱) |
| Fecha cuando se subsanó (doc 23) | `fechaSubsanacion` |
| Fecha del recurso contra el rechazo (doc 28) | `fechaRecursoRechazo` |
| Fecha de la notificación (doc 38, 95, 158, 199) | `fechaNotificacion` |
| Fecha de la contestación (doc 100, 204) | `fechaContestacion` |
| Fecha de la reforma (doc 103, 207) | `fechaReforma` |
| Fecha de la reconvención (doc 105, 209) | `fechaReconvencion` |
| Fecha de la audiencia (doc 42, 134, 161, 238) | `fechaAudiencia` |
| Fecha de la sentencia (doc 56, 138, 175, 242) | `fechaSentencia` |
| (recurso contra la sentencia, 3 días — doc 60, 142) | plazo del recurso ⏱ |

→ Las fechas son fieles al doc; cada una es una etapa distinta del proceso real.

## Conformidad por etapa (los 4 flujos)

| Etapa del doc | Impl | Estado |
|---|---|---|
| Presentación: demanda/pruebas/anexos PDF, radicado, juzgado, fecha radicación | `presentacion` + columnas radicado/juzgado | ✅ |
| Admisión: fecha, auto PDF, decisión ADMISIÓN/INADMISIÓN/RECHAZO | `admision` (decisionAuto, fechaAdmision, auto-admision.pdf) | ✅ |
| Inadmisión: subsanar 5 días háb., escrito subsanación PDF, fecha subsanó | `subsanacion` (plazo 5 háb ⏱, subsanacion.pdf, fechaSubsanacion) | ✅ |
| Rechazo: recurso reposición/apelación, fecha, decisión, observaciones | `recurso_rechazo` (recursoRechazo, fechaRecursoRechazo, decisionRecursoRechazo, obs, recurso.pdf) | ✅ |
| ¿Retiro art. 67? → archivo | `retiro` → `archivado` (terminal) | ✅ |
| Traslado / notificación, 10 días háb. para contestar | `traslado` (fechaNotificacion, notificacion.pdf, plazo 10 háb ⏱) | ✅ |
| Contestación (doble): ¿contestaron?, silencio, reforma, reconvención | `contestacion` (contestaron, contestacion.pdf/auto-silencio.pdf, hayReforma, hayReconvencion) | ⚠️ parcial |
| Preparación de audiencia: ¿conciliable?, documentos | `preparacionAudiencia` | ✅ |
| Citación a audiencia: fecha, auto | `citacionAudiencia` (fechaAudiencia, auto-citacion.pdf) | ✅ |
| Audiencia única: conciliación→…→sentencia + reposición | `audienciaUnica` + `recurso` (reposición) | ✅ |
| Audiencia art. 77 + art. 80 (doble) + apelación | `audienciaArt77` + `audienciaArt80` + `recurso` (apelación) | ✅ |
| Sentencia: fecha, decisión, recurso (forma, 3 días, decisión) | `sentencia`(en audiencia) + `recurso` (hayRecurso, formaRecurso, decisionRecurso, plazo 3) | ✅ |

## Gaps reales detectados (ramas secundarias)

Son **caminos de salida tras una decisión negativa**, no el flujo principal:

1. **Subsanación → RECHAZAR no archiva.** El doc: si tras subsanar el juez rechaza, va a
   archivo (doc 109/213). Hoy `decisionTrasSubsanacion = RECHAZAR` se guarda pero el flujo
   sigue a traslado en vez de cerrar. → falta rama `archivado` desde subsanación.
2. **Rechazo con recurso desfavorable no archiva.** Si el recurso contra el rechazo se
   resuelve DESFAVORABLE, el proceso debería terminar; hoy continúa.
3. **Reconvención: sub-flujo simplificado.** El doc (106-114) modela, tras la reconvención,
   la decisión del juez ADMITIR/INADMITIR/RECHAZAR **con su propia subsanación, traslado y
   contestación**. Hoy se captura solo `decisionReconvencion` (un campo), sin esos sub-pasos.
4. **`hayReforma` se ofrece también en demandante/única**, donde el doc no lo pide (el doc
   solo trae reforma en los flujos con contestación). Sobra-inclusión menor.

Ninguno rompe el flujo principal; son refinamientos de los desenlaces negativos.

## Resolución de los gaps (2026-06-17)

- **Gap 1 (subsanación→RECHAZAR) y Gap 2 (rechazo recurso desfavorable/sin recurso):** CERRADOS.
  Nueva etapa terminal `archivado_rechazo` (orden 3) con `disponibleSi` compuesto y gated por
  el contexto de admisión (no cuelga demandado/única ni los flujos sin rechazo). Verificado por
  simulación: los 3 caminos negativos archivan; los 4 felices siguen terminando.
- **Gap 4 (`hayReforma` en demandante/única):** CERRADO. `hayReforma.mostrarSi =
  {alguna:[rol=Demandado, instancia=Doble]}` → no aparece en demandante/única.
- **Gap 3 (reconvención):** por decisión del usuario, queda **solo registrada**
  (`decisionReconvencion` + fecha + doc), sin el sub-flujo de subsanación/traslado/contestación
  de la reconvención. Aceptado como alcance.

## Veredicto

**El flujo principal de los 4 caminos (demandante/demandado × única/doble) está bien
implementado y verificado**: etapas en el orden del doc, ramas por rol×instancia, decisión del
auto con sus 3 ramas, plazos (10/5/3 con días hábiles donde el doc lo dice), documentos
anclados a su campo. Los **4 gaps** son ramas de cierre tras decisiones negativas y la
reconvención detallada — opcionales según qué tan fino se quiera seguir el doc.

Recomendación: cerrar los gaps 1 y 2 (archivar en rechazo/subsanación negativa) por ser
desenlaces claros y simples; los gaps 3 y 4 evaluarlos con el usuario (¿se quiere el sub-flujo
completo de reconvención, o basta con registrarla?).
