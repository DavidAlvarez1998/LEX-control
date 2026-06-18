# Diseño — laboral-flujo-doc

Fuente de verdad: `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`.
Las referencias `(doc N)` son números de párrafo del docx (extraídos con el orden del XML).

## 1. Cómo se mapea el doc al motor existente

El motor de procesos ya soporta: etapas con `orden` (varias con el mismo `orden` = ramas),
`disponibleSi` por etapa, `reglas` (campos/documentos requeridos fijos y condicionales
`requeridosSi`/`opcionalesSi`), `plazoDesdeCampo`+`plazoTipoDias`+`plazoDias`, etapas
`terminal`, y campos con `mostrarSi`/`requeridoSi`/`soloFicha`. Auto-avanza cuando la
siguiente etapa es única e inequívoca y sus requisitos están completos; si hay varias ramas
disponibles a la vez, pide elegir.

**Lo único que falta** para ser fiel al doc es que una etapa/campo dependa de **dos** valores
(rol × instancia). Por eso el único cambio de motor es: condiciones compuestas.

### 1.1 Cambio de motor: `Condicion` compuesta (AND/OR)

Hoy (API `esquema.ts:23`, cliente `lib/procesos.ts:36`):
```ts
type Condicion = { campo: string; igualA: string | string[] };
```
Nuevo (retro-compatible — las tres formas son válidas):
```ts
type Condicion =
  | { campo: string; igualA: string | string[] }   // hoja (igual que hoy)
  | { todas: Condicion[] }                          // AND
  | { alguna: Condicion[] };                        // OR
```
`evaluarCondicion(cond, datos)`:
```ts
if ("todas" in cond)  return cond.todas.every((c) => evaluarCondicion(c, datos));
if ("alguna" in cond) return cond.alguna.some((c) => evaluarCondicion(c, datos));
// hoja: igual que hoy (array-aware para multiselect)
```
Se actualiza en **API** (`src/modules/procesos/esquema.ts`) y **cliente** (`lib/procesos.ts`
y el `evaluarCondicion` que usa `procesos/[id]/page.tsx`). Sin cambios en auto-avance, gating
ni plazos: solo aprenden a evaluar la condición.

## 2. Campos del esquema (esquemaFormulario)

Al **crear** solo se piden los no-`soloFicha`. El resto se llena en la ficha al avanzar.

| key | tipo | creación / ficha | regla |
|---|---|---|---|
| `rol` | select [Demandante, Demandado] | creación, req | bifurca el flujo |
| `tipoInstancia` | select [Única instancia, Doble instancia] | creación, req | bifurca el flujo |
| `requierePoder` | boolean | creación | si true → `poder.pdf` req |
| `fechaRadicacion` | fecha | creación, `mostrarSi rol=Demandante` | plazo base de admisión (informativo) |
| `decisionAuto` | select [ADMISIÓN, INADMISIÓN, RECHAZO] | ficha (soloFicha) | bifurca admisión |
| `fechaAdmision` | fecha | soloFicha | base de subsanación |
| `decisionTrasSubsanacion` | select [ADMITIR, RECHAZAR] | soloFicha, `mostrarSi decisionAuto=INADMISIÓN` | |
| `fechaSubsanacion` | fecha | soloFicha, `mostrarSi decisionAuto=INADMISIÓN` | |
| `recursoRechazo` | select [REPOSICIÓN, APELACIÓN, NINGUNO] | soloFicha, `mostrarSi decisionAuto=RECHAZO` | |
| `decisionRecursoRechazo` | select [FAVORABLE, DESFAVORABLE] | soloFicha, `mostrarSi decisionAuto=RECHAZO` | |
| `observacionesAdmision` | textoLargo | soloFicha | |
| `hayRetiro` | select [SI, NO] | soloFicha | SI → archivo art. 67 |
| `fechaNotificacion` | fecha | soloFicha | plazo contestación 10 días háb. |
| `contestaron` | select [SI, NO] | soloFicha, `mostrarSi tipoInstancia=Doble instancia` | |
| `fechaContestacion` | fecha | soloFicha, `mostrarSi contestaron=SI` | |
| `hayReforma` | select [SI, NO] | soloFicha | doc 102-103, 155, 206-207 |
| `fechaReforma` | fecha | soloFicha, `mostrarSi hayReforma=SI` | |
| `hayReconvencion` | select [SI, NO] | soloFicha, `mostrarSi tipoInstancia=Doble instancia` | doc 104-105 |
| `fechaReconvencion` | fecha | soloFicha, `mostrarSi hayReconvencion=SI` | |
| `decisionReconvencion` | select [ADMITIR, INADMITIR, RECHAZAR] | soloFicha, `mostrarSi hayReconvencion=SI` | doc 106-110, 210-214 |
| `conciliable` | select [SI, NO] | soloFicha | doc 45, 116, 164, 220 |
| `conciliaResultado` | select [SI, NO] | soloFicha | ¿se concilió en audiencia? doc 124, 228 |
| `acuerdoConciliacion` | textoLargo | soloFicha, `mostrarSi conciliaResultado=SI` | |
| `fechaAudiencia` | fecha | soloFicha | |
| `fechaSentencia` | fecha | soloFicha | base recurso 3 días |
| `decisionSentencia` | select [FAVORABLE, DESFAVORABLE] | soloFicha | |
| `hayRecurso` | select [SI, NO] | soloFicha | |
| `formaRecurso` | select [EN AUDIENCIA, POR ESCRITO (3 DÍAS)] | soloFicha, `mostrarSi hayRecurso=SI` | doc 59, 142, 178, 246 |
| `medioRecurso` | texto auto/etiqueta | soloFicha | reposición (única) / apelación (doble) — `mostrarSi` por instancia |
| `decisionRecurso` | select [FAVORABLE, DESFAVORABLE] | soloFicha, `mostrarSi hayRecurso=SI` | |
| `observacionesAudiencia` | textoLargo (excepciones, saneamiento, fijación…) | soloFicha | casillas de la audiencia |

`# radicado` y `juzgado` **no** son campos del esquema: usan las columnas reales
`Proceso.radicado` y `Proceso.despachoJuzgado` (bloque "Datos judiciales", reubicado en
creación — §4).

## 3. Etapas (lista única, ramificada). `orden` con duplicados = ramas.

> Convención: `D?` = `disponibleSi`. Documentos en minúscula `*.pdf`. Plazos "créele al doc".

| orden | key | nombre | D? | requeridos | docs | plazo |
|---|---|---|---|---|---|---|
| 0 | `presentacion` | Presentación / radicación de la demanda | — | `rol`, `tipoInstancia` | `demanda.pdf` (req); `pruebas.pdf`,`anexos.pdf` opc; `poder.pdf` si `requierePoder`; `radicacion.pdf` opc si `rol=Demandante` | — |
| 1 | `admision` | Calificación de la demanda (auto) | `{alguna:[{rol:Demandante},{tipoInstancia:Doble instancia}]}` | `decisionAuto`, `fechaAdmision` | `auto-admision.pdf` req | — |
| 2 | `subsanacion` | Subsanación (inadmisión) | `{todas:[…admision…],{decisionAuto:INADMISIÓN}}`† | `decisionTrasSubsanacion`, `fechaSubsanacion` | `subsanacion.pdf` req | 5 días **hábiles** desde `fechaAdmision` |
| 2 | `recurso_rechazo` | Recurso contra el rechazo | `{decisionAuto:RECHAZO}` | `recursoRechazo`, `decisionRecursoRechazo` | `recurso.pdf` opc | 3 días desde `fechaAdmision` |
| 3 | `retiro` | ¿Retiro de la demanda? (art. 67) | — | `hayRetiro` | — | — |
| 4 | `archivado` | Archivo por retiro (art. 67) | `{hayRetiro:SI}` | — | — | terminal |
| 4 | `traslado` | Traslado y notificación | `{hayRetiro:NO}` | `fechaNotificacion` | `notificacion.pdf` req | 10 días **hábiles** desde `fechaNotificacion` |
| 5 | `contestacion` | Contestación (reforma / reconvención) | `{tipoInstancia:Doble instancia}` | `contestaron` | `contestacion.pdf` si `contestaron=SI`, `auto-silencio.pdf` si `=NO`; `demanda-reformada.pdf` si `hayReforma=SI`; `reconvencion.pdf` si `hayReconvencion=SI` | — |
| 6 | `preparacionAudiencia` | Preparación de la audiencia | — | `conciliable` | `documentos-audiencia.pdf` opc | — |
| 7 | `citacionAudiencia` | Citación a audiencia | — | `fechaAudiencia` | `auto-citacion.pdf` req | — |
| 8 | `audienciaUnica` | Audiencia única (art. CPTSS) | `{tipoInstancia:Única instancia}` | `conciliaResultado`, `fechaSentencia`, `decisionSentencia` | `acta-audiencia.pdf`, `sentencia.pdf` | — |
| 8 | `audienciaArt77` | Audiencia art. 77 (concil./excep./saneam./fijación/decreto) | `{tipoInstancia:Doble instancia}` | `conciliaResultado` | `acta-art77.pdf` opc | — |
| 9 | `audienciaArt80` | Audiencia art. 80 (pruebas/alegatos/sentencia) | `{tipoInstancia:Doble instancia}` | `fechaSentencia`, `decisionSentencia` | `acta-art80.pdf`, `sentencia.pdf` | — |
| 10 | `recurso` | Recurso contra la sentencia | — | `hayRecurso` | `recurso.pdf` si `hayRecurso=SI` | 3 días desde `fechaSentencia` |
| 11 | `archivado` | Archivo por retiro (art. 67) | `{hayRetiro:SI}` | — | — | terminal |
| 11 | `terminada` | Terminación | — | — | — | terminal |

† Las ramas de subsanación/recurso solo existen cuando hubo etapa de admisión; como la
admisión solo aparece bajo `{alguna:[Demandante, Doble]}`, sus ramas heredan implícitamente
ese contexto (si no hubo admisión, `decisionAuto` queda vacío y las ramas no se habilitan).
Para que la subsanación no se ofrezca en demandado+única, su `disponibleSi` se deja en
`{decisionAuto: INADMISIÓN}` (en ese flujo `decisionAuto` nunca se setea → no aparece).

### 3.1 Verificación de los 4 flujos contra el doc

- **Demandante / Única** (doc 7-63): presentacion → admision → (subsanacion|recurso_rechazo|—) → retiro → traslado → *(contestacion oculta: instancia≠Doble)* → preparacionAudiencia → citacionAudiencia → **audienciaUnica** → recurso(**reposición**). ✔
- **Demandante / Doble** (doc 64-143): presentacion → admision → ramas → retiro → traslado → **contestacion** (reforma/reconvención + decisión del juez) → preparacionAudiencia → citacionAudiencia → **audienciaArt77 → audienciaArt80** → recurso(**apelación**). ✔
- **Demandado / Única** (doc 145-182): presentacion *(demanda recibida; sin `fechaRadicacion`)* → *(admision oculta: ni Demandante ni Doble)* → retiro → traslado → preparacionAudiencia → citacionAudiencia → **audienciaUnica** → recurso(**reposición**). ✔ La reforma (doc 155) se expone como campo `hayReforma` en la etapa `retiro`/`traslado` vía `mostrarSi`.
- **Demandado / Doble** (doc 183-247): presentacion → admision → retiro → traslado → **contestacion** → preparacionAudiencia → citacionAudiencia → **audienciaArt77 → audienciaArt80** → recurso(**apelación**). ✔

### 3.2 "Auto PDF" — qué es (la duda del usuario)
En el doc, tras "ADMISIÓN DE LA DEMANDA" aparece `FECHA:` y `AUTO PDF`, y luego
`DECISIÓN DEL AUTO: ADMISIÓN / INADMISIÓN / RECHAZO`. El **auto** es la **providencia escrita
del juez** que resuelve sobre la demanda; se **adjunta** como `auto-admision.pdf` y su
**decisión** (`decisionAuto`) es la que abre las tres ramas. En la UI se rotula
"Auto de calificación (PDF)" + "Decisión del auto" para que se entienda.

## 4. Formulario de creación en orden del doc (solo `grupo === "LABORAL"`)

`procesos/nuevo/page.tsx` hoy renderiza: título → cliente → peticionarios → responsable →
**campos del esquema** → documentos → **Datos judiciales (radicado/juzgado/cuantía)** →
partes. Para laboral se reordena a la secuencia de la etapa *Presentación* del doc:

1. **Rol** (Demandante/Demandado) y **Tipo de instancia** (Única/Doble) — los dos primeros.
2. **¿Requiere poder?**
3. **Documentos de la demanda**: `demanda.pdf` (req), `pruebas.pdf`, `anexos.pdf`,
   `poder.pdf` (si aplica), `radicacion.pdf` (si demandante).
4. **Fecha de radicación** (solo demandante).
5. **# Radicado de la demanda** y **Juzgado o corporación** (bloque "Datos judiciales"
   reubicado aquí y recortado: sin cuantía; mapea a `Proceso.radicado`/`despachoJuzgado`).
6. **Cliente** + **responsable** (se mantienen; el título es auto — ver [[laboral-titulo-auto]]).

Implementación: el orden se controla con el render condicional `tipo.grupo === "LABORAL"`
(secciones reordenadas) y reusando `FormularioDinamico` (respeta el orden del array). No se
toca el orden de los demás grupos.

## 5. Alternativas consideradas

- **Sin tocar el motor (v1).** Ramificar solo por instancia y resolver el rol con `mostrarSi`
  a nivel de campo. Descartado: la etapa *Admisión* existe/no-existe según (rol×instancia) —
  es estructural, no cosmético; forzarla con campos sueltos deja un flujo infiel (demandado+
  única vería una etapa de admisión que el doc no tiene).
- **4 `TipoProceso` separados.** Un tipo por flujo. Descartado: el doc lo presenta como **un**
  proceso con dos elecciones de arranque; fragmentaría el catálogo y la vista "Procesos
  Laborales", y duplicaría plazos/plantillas.
- **Campo `flujo` derivado de 4 valores.** El motor no deriva campos (solo `auto` server-side
  para cosas como radicado). Pedir un 4-en-1 contradice las dos elecciones del doc.
- **Mantener `pretensiones`/`hechos` para un generador de demanda.** Descartado por ahora: el
  doc modela la demanda como PDF adjunto, no hay plantilla de demanda laboral pedida. Si luego
  se quiere generar, se reintroducen como `soloFicha` opcionales (decisión futura, aparte).
