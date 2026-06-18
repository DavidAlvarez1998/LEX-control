# Diseño — laboral-doble-instancia

Fuente de verdad: `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`
(tramo DEMANDANTE · DOBLE INSTANCIA) + extensión de 2ª instancia acordada con el usuario.

## Fases de este caso (Demandante · Doble) — las 6 completas

| Fase | Etapas de este caso |
|---|---|
| **1 · Demanda y admisión** | Presentación/radicación · Calificación → Subsanación → Recurso de rechazo · ¿Retiro art. 67? |
| **2 · Traslado y contestación** | Traslado y notificación (⏱10 días) · Contestación (reforma · reconvención + sub-flujo) |
| **3 · Audiencias** | Preparación → Citación (orden doble) · Audiencia art. 77 → Audiencia art. 80 |
| **4 · Sentencia y recurso** | Sentencia (art. 80) · Apelación (¿interpone? → ¿concede?) |
| **5 · Segunda instancia** | Remisión → Sustentación → Audiencia 2ª → Sentencia 2ª (CONFIRMA/REVOCA/MODIFICA) |
| **6 · Terminación / archivo** | Terminación · Archivo (retiro · rechazo · conciliación) |

## 1. Grafo definitivo del flujo

```
PROCESO LABORAL — DEMANDANTE · DOBLE INSTANCIA  (Ley 2452/2025 · CPTSS)

0) CREACIÓN  → Cliente · rol=Demandante · instancia=Doble · ¿requiere poder?(→poder.pdf)

1) PRESENTACIÓN / RADICACIÓN
   demanda.pdf(oblig) · pruebas.pdf · anexos.pdf · radicacion.pdf · fechaRadicacion · radicado · juzgado

2) CALIFICACIÓN  (fechaAuto + auto-calificacion.pdf)
   DECISIÓN DEL AUTO:
     ├ ADMISIÓN ─────────────────────────────► (3)
     ├ INADMISIÓN ─► 2a SUBSANACIÓN (5 días háb.)
     │                 escrito-subsanacion.pdf · fechaSubsanacion
     │                 DECISIÓN TRAS SUBSANAR:
     │                   ├ ADMITIR  ─► fechaAdmisionTrasSubsanacion + auto-admision-tras-subsanacion.pdf ─► (3)
     │                   └ RECHAZAR ───────────┐
     │                                          ▼
     └ RECHAZO ──────────────────────► 2b RECURSO CONTRA EL RECHAZO (3 días)
                                          recursoRechazo: NO / REPOSICIÓN / APELACIÓN
                                          (si hay) fechaRecursoRechazo + recurso.pdf + observaciones
                                          DECISIÓN: FAVORABLE ─► (3) · DESFAVORABLE/NO ─► ARCHIVO(fin)

3) ¿RETIRO art.67?  SÍ ─► ARCHIVO(fin) · NO ─► sigue
4) TRASLADO Y NOTIFICACIÓN  fechaNotificacion + notificacion.pdf · ⏱10 días háb. contestar
5) CONTESTACIÓN
     ¿contestaron? SÍ→fecha+contestacion.pdf · NO→fecha+auto-silencio.pdf
     ¿reforma?     SÍ→demanda-reformada.pdf+fecha
     ¿reconvención? SÍ→fecha+reconvencion.pdf → decisión juez (ADMITIR/INADMITIR/RECHAZAR + sub-flujo)
6) PREPARACIÓN DE LA AUDIENCIA   ◄ corregido: antes de la citación (solo doble)
     ¿conciliable? · documentos · observaciones
7) CITACIÓN A AUDIENCIA   auto-citacion.pdf + fechaAudiencia
8) AUDIENCIA ART. 77
     ¿se concilia? SÍ→acuerdo+fecha+obs→TERMINA por conciliación · NO→sigue
     excepciones previas · saneamiento · fijación del litigio · DECRETO de pruebas
9) AUDIENCIA ART. 80
     PRÁCTICA de pruebas · alegatos · fechaSentencia + sentencia.pdf · decisión 1ª: FAVORABLE/DESFAVORABLE
10) APELACIÓN (3 días)
     ¿se interpone? NO ─► TERMINACIÓN (1ª en firme)
                    SÍ ─► forma (audiencia / escrito 3 días → fecha + apelacion.pdf)
                          ¿el juez la concede? NO ─► TERMINACIÓN (1ª en firme)
                                               SÍ ─► SEGUNDA INSTANCIA ▼

══ SEGUNDA INSTANCIA (Tribunal Superior — Sala Laboral) ══
S1 REMISIÓN AL TRIBUNAL        fechaRemision2inst + radicado2inst
S2 SUSTENTACIÓN DEL RECURSO    fechaSustentacion + escrito-sustentacion.pdf + auto-2inst.pdf + fecha
S3 AUDIENCIA DE 2ª INSTANCIA   fechaAudiencia2inst + acta-2inst.pdf(opc) + alegatos
S4 SENTENCIA DE 2ª INSTANCIA   fechaSentencia2inst + sentencia-2inst.pdf + decisión: CONFIRMA/REVOCA/MODIFICA
11) TERMINACIÓN (ejecutoriada — fin)
```

**Finales posibles:** Archivo (retiro art. 67 · rechazo sin recurso o desfavorable) ·
Conciliación (art. 77) · Terminación tras 1ª instancia (sin apelación o apelación negada) ·
Terminación tras sentencia de 2ª instancia.

## 2. Campos nuevos (esquemaFormulario)

| key | label | tipo | mostrarSi / soloFicha |
|---|---|---|---|
| `fechaAdmisionTrasSubsanacion` | Fecha del auto de admisión (tras subsanar) | fecha | `decisionTrasSubsanacion = ADMITIR` · soloFicha |
| `concedeApelacion` | ¿El juez concede la apelación? | select SI/NO | `hayRecurso = SI` (doble) · soloFicha |
| `fechaRemision2inst` | Fecha de remisión / reparto al Tribunal | fecha | `concedeApelacion = SI` · soloFicha |
| `radicado2inst` | N.º de radicado en 2ª instancia | texto | `concedeApelacion = SI` · soloFicha |
| `fechaSustentacion` | Fecha de sustentación del recurso | fecha | `concedeApelacion = SI` · soloFicha |
| `fechaAudiencia2inst` | Fecha de la audiencia de 2ª instancia | fecha | `concedeApelacion = SI` · soloFicha |
| `fechaSentencia2inst` | Fecha de la sentencia de 2ª instancia | fecha | `concedeApelacion = SI` · soloFicha |
| `decisionSegundaInstancia` | Decisión de 2ª instancia | select CONFIRMA/REVOCA/MODIFICA | `concedeApelacion = SI` · soloFicha |

**Campos reusados (corrección 1):** `recursoRechazo`, `fechaRecursoRechazo`,
`decisionRecursoRechazo`, `observacionesRecursoRechazo` cambian su `mostrarSi` de
`{decisionAuto: RECHAZO}` a `{alguna: [{decisionAuto: RECHAZO}, {decisionTrasSubsanacion: RECHAZAR}]}`.

**Documentos nuevos:** `auto-admision-tras-subsanacion.pdf`, `apelacion.pdf`,
`escrito-sustentacion.pdf`, `auto-2inst.pdf`, `acta-2inst.pdf`, `sentencia-2inst.pdf`.

## 3. Renumeración de `orden` (motor camina niveles > actual)

Hoy `subsanacion` y `recurso_rechazo` comparten `orden = 2` → el recurso no es alcanzable
*desde* la subsanación. Nueva numeración (los pares comparten nivel solo si son mutuamente
excluyentes por `disponibleSi`):

| orden | etapa(s) | nota |
|---|---|---|
| 0 | `presentacion` | |
| 1 | `admision` | gated `{alguna:[Demandante, Doble]}` |
| 2 | `subsanacion` | gated INADMISIÓN |
| 3 | `recurso_rechazo` | gated `{alguna:[RECHAZO, decisionTrasSubsanacion=RECHAZAR]}` ← **alcanzable desde admisión Y desde subsanación** |
| 4 | `archivado_rechazo` (terminal) | rechazo sin recurso / recurso desfavorable |
| 5 | `retiro` | |
| 6 | `archivado` (terminal) · `traslado` | `hayRetiro=SI` / `=NO` |
| 7 | `contestacion` | gated Doble |
| 8 | `citacionAudiencia` (única) · `preparacionAudiencia_doble` | por instancia |
| 9 | `preparacionAudiencia` (única) · `citacionAudiencia_doble` | por instancia |
| 10 | `audienciaUnica` (única) · `audienciaArt77` (doble) | |
| 11 | `audienciaArt80` (doble) | |
| 12 | `recurso` (reposición única / apelación doble) | |
| 13 | `remision2inst` | gated `concedeApelacion=SI` (⇒ solo doble) |
| 14 | `sustentacion2inst` | gated `concedeApelacion=SI` |
| 15 | `audiencia2inst` | gated `concedeApelacion=SI` |
| 16 | `sentencia2inst` | gated `concedeApelacion=SI` |
| 17 | `terminada` (terminal) | |

> El rechazo **directo** (admisión orden 1) y el rechazo **tras subsanar** (subsanación orden
> 2) ambos llegan a `recurso_rechazo` (orden 3): para el directo, `subsanacion` (orden 2) no
> está disponible (su condición INADMISIÓN ya está decidida en falso) → el motor salta de
> nivel. Verificado contra la lógica `siguienteEtapaAuto` (salta niveles sin ramas disponibles
> ni pendientes).

## 4. Orden Preparación↔Citación por instancia (corrección 3)

`preparacionAudiencia`/`citacionAudiencia` existentes → **gated a Única** (mantienen el orden
Citación→Preparación correcto para única). Se agregan `preparacionAudiencia_doble` (orden 8) y
`citacionAudiencia_doble` (orden 9), **gated a Doble**, con orden invertido. Comparten campos
(`conciliable`, `observacionesPreparacion`, `fechaAudiencia`, `auto-citacion.pdf`).

Cliente `datos-proceso.tsx`:
- `TITULO_SECCION_LABORAL` += `preparacionAudiencia_doble: "Preparación de la audiencia"`,
  `citacionAudiencia_doble: "Citación a audiencia"`, y las 4 etapas de 2ª instancia.
- `tituloEtapa` instance-aware: devuelve `null` para la variante inactiva (mismo patrón que
  `audienciaArt77/80`), de modo que el **orden de las secciones** sea Preparación→Citación en
  doble y Citación→Preparación en única.
- `tituloCampo`: rutea `conciliable`/`observacionesPreparacion` → "Preparación de la audiencia"
  y `fechaAudiencia` → "Citación a audiencia" por conjunto (independiente de instancia), para
  que la asignación por proximidad no los mande a "Datos del proceso".

## 5. Segunda instancia — gating

Todas las etapas S1–S4 llevan `disponibleSi: {campo: concedeApelacion, igualA: "SI"}`. Como
`concedeApelacion` solo se ofrece en doble (su `mostrarSi` cuelga de `hayRecurso=SI`, y la
apelación es la forma del recurso en doble), la 2ª instancia queda naturalmente excluida en
única. Si la apelación no se interpone o el juez la niega → ninguna S* está disponible y el
motor cae en `terminada`.

## 6. Plazos (créele al doc — ver [[plazos-dias-habiles-creele-al-doc]])

Sin cambios respecto a lo aplicado: contestación 10 días hábiles (`fechaNotificacion`),
subsanación 5 días hábiles (`fechaAdmision`), recurso 3 días. La 2ª instancia no fija plazos
de vencimiento en el doc → S1–S4 quedan **sin** `plazoDesdeCampo` (solo registro de fechas).

## 7. Alcance no cubierto (explícito)

- **Grado de consulta (art. 69 CPT):** cuando la sentencia es adversa al trabajador y NO se
  apela, sube automáticamente al superior. **No** se modela (el doc no lo trae; decisión del
  usuario).
- **Recurso de casación (Corte Suprema):** **no** se modela.
- **Recurso de queja** (si el juez niega la apelación): no se modela; "apelación negada" cierra
  en Terminación.
- **Limitación menor:** el plazo del recurso tras subsanar reusa `fechaAdmision` como ancla
  (no se captura una fecha de auto de rechazo independiente para ese sub-camino). Es
  informativo; aceptado.
