# Diseño — procesos-verbales-civil (CGP)

Fuente: **Código General del Proceso** (Ley 1564/2012). Verbal: arts. 368–373; Verbal sumario:
arts. 390–392; calificación/subsanación: arts. 90, 82–84; términos: art. 118 (días hábiles).
Patrón de modelado: igual que `laboral-doble-instancia` (1 `TipoProceso` → ramas por
`disponibleSi`/`mostrarSi`, fases, plazos, documentos anclados, terminales).

═══════════════════════════════════════════════════════════════════════════════
# A) PROCESO (DECLARATIVO) VERBAL — CGP 368–373
═══════════════════════════════════════════════════════════════════════════════
*Mayor o menor cuantía · **doble instancia** (apelable) · 2 audiencias.*

## Fases
| Fase | Etapas | Qué ocurre |
|---|---|---|
| 1 · Demanda y admisión | `presentacion` · `calificacion` · `subsanacion` · `recurso_rechazo` · `archivado_rechazo` · `retiro` · `archivado` | Se presenta/califica la demanda. |
| 2 · Traslado y contestación | `traslado` · `contestacion` | Notificación + 20 días háb.; contestación/excepciones/reconvención. |
| 3 · Audiencia inicial (art. 372) | `audienciaInicial` | Conciliación, excepciones previas, saneamiento, fijación del litigio, decreto de pruebas. |
| 4 · Instrucción y juzgamiento (art. 373) | `audienciaInstruccion` | Práctica de pruebas, alegatos, sentencia. |
| 5 · Segunda instancia | `remision2inst` · `sustentacion2inst` · `audiencia2inst` · `sentencia2inst` | Apelación concedida → Tribunal. |
| 6 · Terminación / archivo | `terminada` · `terminada_conciliacion` · terminales de archivo | Cierre. |

## Grafo
```
FASE 1 ─ DEMANDA Y ADMISIÓN
 ① PRESENTACIÓN        📎 demanda.pdf(req) · pruebas.pdf · anexos.pdf · poder.pdf(si requierePoder)
     rol · tipoPretensión · pretensiones · cuantía · estimación jurada · ¿conciliación previa? · ¿medidas cautelares?
 ② CALIFICACIÓN (auto)  fechaAuto + 📎 auto-calificacion.pdf
     ◇ decisionAuto = ADMISIÓN ─────────────────────────► ④
                    = INADMISIÓN → ③ SUBSANACIÓN (⏱5 háb.) 📎 subsanacion.pdf
                                      ◇ ADMITIR → ④   ◇ RECHAZAR → ②b
                    = RECHAZO ─────────► ②b RECURSO (reposición/apelación, ⏱3)
                                          FAVORABLE → ④ · DESFAVORABLE/NO → ARCHIVO ✦
 ④ ¿RETIRO? (art. 93)  SÍ → ARCHIVO ✦ · NO → sigue

FASE 2 ─ TRASLADO Y CONTESTACIÓN
 ⑤ NOTIFICACIÓN + TRASLADO  fechaNotificacion + 📎 notificacion.pdf · ⏱ 20 días háb.
 ⑥ CONTESTACIÓN
     ¿contestaron? SÍ → 📎 contestacion.pdf · NO → 📎 auto-silencio.pdf
     ¿excepciones de mérito? · ¿reconvención? → decisión juez (admite/inadmite→subsanar/rechaza)
        → traslado reconv. → contestación reconv.   · ¿llamamiento en garantía?

FASE 3 ─ AUDIENCIA INICIAL (art. 372)
 ⑦ ¿se concilia? SÍ → 📎 acta + acuerdo → TERMINA por conciliación ✦ · NO → sigue
   · excepciones previas · saneamiento · fijación del litigio · decreto de pruebas
   (si solo prueba documental → sentencia anticipada)

FASE 4 ─ INSTRUCCIÓN Y JUZGAMIENTO (art. 373)
 ⑧ práctica de pruebas · alegatos · fechaSentencia + 📎 sentencia.pdf · ◇ FAVORABLE/DESFAVORABLE

FASE 5 ─ SEGUNDA INSTANCIA  (si se apela y se concede)
 ⑨ APELACIÓN (⏱3 háb.) ¿se interpone? → ¿el juez concede?
     NO/niega → TERMINA (1ª en firme) · SÍ → S1 REMISIÓN → S2 SUSTENTACIÓN(📎) → S3 AUDIENCIA 2ª → S4 SENTENCIA 2ª ◇ CONFIRMA/REVOCA/MODIFICA

FASE 6 ─ TERMINACIÓN ✔   (✦ = desenlace de archivo/conciliación)
```

## Campos a usar (`esquemaFormulario`)
**Intake (al crear):**
| key | label | tipo | notas |
|---|---|---|---|
| `rol` | Rol en el proceso | select `Demandante`/`Demandado` | define quién califica (solo Demandante) |
| `tipoPretension` | Tipo de pretensión | select | declarativa / constitutiva / de condena (existente) |
| `relacionJuridica` | Relación jurídica | texto | |
| `pretensiones` | Pretensiones | textoLargo | |
| `cuantia` | Cuantía | numero | |
| `cuantiaTipo` | Tipo de cuantía | select `Mayor`/`Menor` | ambas doble instancia |
| `estimacionJuramentada` | Estimación juramentada | textoLargo | |
| `fechaHechos` | Fecha de los hechos | fecha | |
| `hechos` | Hechos | textoLargo | |
| `pruebasOfrecidas` | Pruebas ofrecidas | textoLargo | |
| `solicitaMedidasCautelares` | ¿Solicita medidas cautelares? | boolean | |
| `conciliacionPrevia` | ¿Hubo conciliación previa? | boolean | requisito de procedibilidad |
| `requierePoder` | ¿Requiere poder? | boolean | sí → `poder.pdf` |

**Ficha (`soloFicha`):** `decisionAuto` [ADMISIÓN/INADMISIÓN/RECHAZO], `fechaAuto`,
`decisionTrasSubsanacion` [ADMITIR/RECHAZAR], `fechaSubsanacion`, `fechaAdmisionTrasSubsanacion`,
`recursoRechazo` [NO/REPOSICIÓN/APELACIÓN], `fechaRecursoRechazo`, `decisionRecursoRechazo`,
`observacionesRecursoRechazo`, `hayRetiro` [SI/NO], `fechaNotificacion`, `contestaron` [SI/NO],
`fechaContestacion`, `excepcionesMerito`, `hayReconvencion` [SI/NO], `fechaReconvencion`,
`decisionReconvencion` [ADMITIR/INADMITIR/RECHAZAR] (+ sub-flujo), `llamamientoGarantia` [SI/NO],
`conciliaResultado` [SI/NO], `acuerdoConciliacion`, `excepcionesPrevias`, `saneamiento`,
`fijacionLitigio`, `decretoPruebas`, `practicaPruebas`, `alegatos`, `fechaSentencia`,
`decisionSentencia` [FAVORABLE/DESFAVORABLE], `hayRecurso` [SI/NO], `formaRecurso`,
`concedeApelacion` [SI/NO], `fechaRemision2inst`, `radicado2inst`, `fechaSustentacion`,
`fechaAudiencia2inst`, `fechaSentencia2inst`, `decisionSegundaInstancia` [CONFIRMA/REVOCA/MODIFICA].
*(Columnas reales reutilizadas: `radicado`, `despachoJuzgado`, `cuantiaValor`.)*

## Etapas (reglas clave)
| orden | etapa | disponibleSi | camposReq | docsReq | plazo |
|---|---|---|---|---|---|
| 0 | `presentacion` | — | rol, pretensiones, cuantia | demanda.pdf | — |
| 1 | `calificacion` | rol=Demandante | fechaAuto + (requeridosSi rol=Demandante→decisionAuto) | auto-calificacion.pdf | — |
| 2 | `subsanacion` | rol=Demandante ∧ decisionAuto=INADMISIÓN | decisionTrasSubsanacion, fechaSubsanacion | subsanacion.pdf | 5 háb. desde fechaAuto |
| 3 | `recurso_rechazo` | rol=Demandante ∧ (RECHAZO ∨ trasSubsanación=RECHAZAR) | recursoRechazo | — | 3 háb. |
| 4 | `archivado_rechazo` (term) | rechazo ∧ (recurso NO ∨ DESFAVORABLE) | — | — | — |
| 5 | `retiro` | — | hayRetiro | — | — |
| 6 | `archivado` (term) / `traslado` | hayRetiro=SI / =NO | (traslado) fechaNotificacion | notificacion.pdf | 20 háb. contestar |
| 7 | `contestacion` | — | contestaron | (SÍ) contestacion.pdf / (NO) auto-silencio.pdf | — |
| 8 | `audienciaInicial` | — | conciliaResultado | acta-art372.pdf (opc) | — |
| 9 | `audienciaInstruccion` | conciliaResultado=NO | fechaSentencia, decisionSentencia | sentencia.pdf | — |
| 9 | `terminada_conciliacion` (term) | conciliaResultado=SI | — | — | — |
| 10 | `recurso` (apelación) | — | hayRecurso (+concedeApelacion si SÍ) | recurso.pdf (opc) | 3 |
| 11–14 | `remision2inst`…`sentencia2inst` | concedeApelacion=SI | (S4) fechaSentencia2inst, decisionSegundaInstancia | (S2) escrito-sustentacion.pdf · (S4) sentencia-2inst.pdf | — |
| 15 | `terminada` (term) | — | — | — | — |

═══════════════════════════════════════════════════════════════════════════════
# B) PROCESO VERBAL SUMARIO — CGP 390–392
═══════════════════════════════════════════════════════════════════════════════
*Mínima cuantía + asuntos del art. 390 · **única instancia** (NO apelable) · 1 audiencia.*

## Fases
| Fase | Etapas | Qué ocurre |
|---|---|---|
| 1 · Demanda y admisión | `presentacion` · `calificacion` · `subsanacion` · `archivado_rechazo` · `retiro` · `archivado` | Demanda (puede ser en formato) y calificación. |
| 2 · Traslado y contestación | `traslado` · `contestacion` | Notificación + 10 días háb.; contestación (limitada). |
| 3 · Audiencia única (art. 392) | `audienciaUnica` · `terminada_conciliacion` | Conciliación, excepciones, pruebas, alegatos, sentencia — todo concentrado. |
| 4 · Recurso | `recurso` | Reposición (no hay apelación). |
| 5 · Terminación / archivo | `terminada` · terminales de archivo | Cierre. |

## Grafo
```
FASE 1 ─ DEMANDA Y ADMISIÓN
 ① PRESENTACIÓN (formato art. 390 §)  📎 demanda.pdf(req) · pruebas.pdf · anexos.pdf · poder.pdf
     asunto/naturaleza · pretensiones · cuantía(mínima) · fundamento de derecho
 ② CALIFICACIÓN  fechaAuto + 📎 auto-calificacion.pdf
     ◇ ADMISIÓN → ③ · INADMISIÓN → SUBSANACIÓN(⏱5)→admite/rechaza · RECHAZO → ARCHIVO ✦
   ¿RETIRO? SÍ → ARCHIVO ✦ · NO → sigue

FASE 2 ─ TRASLADO Y CONTESTACIÓN
 ③ NOTIFICACIÓN + TRASLADO  fechaNotificacion + 📎 notificacion.pdf · ⏱ 10 días háb.
 ④ CONTESTACIÓN  ¿contestaron? SÍ→📎contestacion.pdf · NO→📎auto-silencio.pdf
     (SIN reconvención · SIN excepciones previas separadas · SIN terceros)

FASE 3 ─ AUDIENCIA ÚNICA (art. 392)
 ⑤ ¿se concilia? SÍ → 📎acta+acuerdo → TERMINA ✦ · NO → sigue
   · interrogatorios · excepciones (se resuelven aquí) · pruebas · alegatos
   · fechaSentencia + 📎 sentencia.pdf · ◇ FAVORABLE/DESFAVORABLE

FASE 4 ─ RECURSO
 ⑥ REPOSICIÓN (hayRecurso; NO apelación — única instancia)

FASE 5 ─ TERMINACIÓN ✔
```

## Campos a usar (`esquemaFormulario`)
**Intake:** `asuntoNaturaleza` [select: restitución de inmueble arrendado · servidumbres ·
posesorios · propiedad horizontal · alimentos (los que correspondan) · otros del art. 390],
`pretensiones` [textoLargo], `cuantia` [numero], `fundamentoDerecho` [textoLargo],
`fechaHechos` [fecha], `hechos` [textoLargo], `pruebasOfrecidas` [textoLargo],
`requierePoder` [boolean], `observaciones` [textoLargo].
**Ficha (`soloFicha`):** `decisionAuto`, `fechaAuto`, `decisionTrasSubsanacion`,
`fechaSubsanacion`, `fechaAdmisionTrasSubsanacion`, `hayRetiro`, `fechaNotificacion`,
`contestaron`, `fechaContestacion`, `conciliaResultado`, `acuerdoConciliacion`, `excepciones`,
`practicaPruebas`, `alegatos`, `fechaSentencia`, `decisionSentencia`, `hayRecurso` (reposición),
`decisionRecurso` [FAVORABLE/DESFAVORABLE]. *(SIN `concedeApelacion`/2ª instancia.)*

## Etapas (reglas clave)
| orden | etapa | disponibleSi | camposReq | docsReq | plazo |
|---|---|---|---|---|---|
| 0 | `presentacion` | — | asuntoNaturaleza, pretensiones | demanda.pdf | — |
| 1 | `calificacion` | — | decisionAuto, fechaAuto | auto-calificacion.pdf | — |
| 2 | `subsanacion` | decisionAuto=INADMISIÓN | decisionTrasSubsanacion, fechaSubsanacion | subsanacion.pdf | 5 háb. |
| 3 | `archivado_rechazo` (term) | RECHAZO ∨ trasSubsanación=RECHAZAR | — | — | — |
| 4 | `retiro` | — | hayRetiro | — | — |
| 5 | `archivado`(term)/`traslado` | hayRetiro=SI/=NO | (traslado) fechaNotificacion | notificacion.pdf | 10 háb. |
| 6 | `contestacion` | — | contestaron | (SÍ)contestacion.pdf/(NO)auto-silencio.pdf | — |
| 7 | `audienciaUnica` | — | conciliaResultado + (requeridosSi conciliaResultado=NO → fechaSentencia, decisionSentencia + sentencia.pdf) | — | — |
| 7 | `terminada_conciliacion` (term) | conciliaResultado=SI | — | — | — |
| 8 | `recurso` | — | hayRecurso | — | 3 |
| 9 | `terminada` (term) | — | — | — | — |

## Notas de diseño
- **Demandado (verbal):** si se modela `rol`, el demandado **no califica** (la `calificacion`,
  `subsanacion` y `recurso_rechazo` van gateadas a `rol=Demandante`), igual que el laboral. El
  sumario se deja sin `rol` por simplicidad (representamos al demandante; confirmar).
- **Sentencia anticipada** (art. 278): el verbal puede fallar en la audiencia inicial si solo
  hay prueba documental → se puede modelar como rama de `audienciaInicial` (opcional, fase 2).
- **Plazos**: 20/10 (traslado), 5 (subsanación), 3 (recursos), todos **hábiles** (CGP 118)
  salvo que se confirme lo contrario.
- **Reutilización**: el verbal es prácticamente el laboral civil (mismas etapas/ramas/2ª
  instancia); el sumario es el "única instancia" sin reconvención ni apelación.

## Comportamiento heredado del motor (aplica a los dos) — NO se reimplementa

Estos dos tipos usan el **mismo motor** que el laboral/DdP/tutela (`esquema.ts` +
`procesos.router.ts`). Por eso, con solo declarar bien las `reglas` por etapa, heredan:

1. **Avance automático conforme se llenan los campos** (`autoavanzarEtapas` →
   `siguienteEtapaAuto`): al **guardar** datos, si la siguiente etapa tiene sus
   `camposRequeridos` + `documentosRequeridos` completos y la rama no es ambigua, el proceso
   **avanza solo**. Por eso CADA etapa de estos diseños declara qué exige (a diferencia del
   esqueleto de la tutela, donde se avanzaba sin pedir nada).
2. **Bloqueo y guía al avanzar manual** (clic en el stepper): si faltan datos/documentos, NO
   avanza, abre el formulario y **resalta lo que falta**.
3. **Guardar lo diligenciado antes de avanzar** (`flush`): si hay cambios sin guardar y se
   hace clic en una etapa, primero se guardan y se reevalúa el avance.
4. **Salto a terminal decidido** (`terminalDecidido`): si los datos ya implican un cierre
   (retiro art. 93 = SÍ, rechazo definitivo, conciliación = SÍ), el proceso **se cierra solo**
   al guardar, aunque falte papeleo intermedio. El botón muestra "Guardar y archivar/finalizar".
5. **Ramas por opción** (`disponibleSi` `{todas}`/`{alguna}`) y **campos condicionales**
   (`mostrarSi`): las opciones que abren otro camino aparecen con su animación (`.lex-campo-reveal`).
6. **Plazos / vencimientos** derivados (`plazoDesdeCampo` + `plazoTipoDias`): el vencimiento se
   calcula y se muestra en la ficha (semáforo) — por eso fijamos `plazoTipoDias`.
7. **Stepper agrupado por fase** (genérico para judiciales) + **documentos en tarjeta** con el
   nombre del archivo subido.

→ En resumen: para que estos verbales "avancen solos conforme se llena el form" **no hay que
programar nada nuevo**; basta poblar `camposRequeridos`/`documentosRequeridos`/`disponibleSi`/
plazos en el seed (que es justo lo que detallan las tablas de etapas de arriba).
