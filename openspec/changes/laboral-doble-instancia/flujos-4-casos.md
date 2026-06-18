# Los 4 flujos del Proceso Laboral — mapas perfeccionados

Fuente: `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`.
Un solo `TipoProceso` ("Proceso Laboral") que ramifica por **rol** (Demandante/Demandado) ×
**instancia** (Única/Doble). El detalle campo-por-campo del caso DEMANDANTE·DOBLE está en
`design.md`; aquí los **4 mapas completos** y lo que pide cada paso, ya de-duplicados y con las
correcciones aplicadas de forma **consistente entre casos**.

Convención: `doc.pdf`(oblig) · `doc.pdf?`(opcional) · `[opciones de select]` · ⏱ plazo.

## Diferencias estructurales entre los 4 (resumen)

| | Calificación (decisión + subsanación/rechazo) | Contestación (reforma/reconv.) | Audiencias | Recurso vs. sentencia | 2ª instancia |
|---|---|---|---|---|---|
| **Demandante · Única** | **Sí** (somos quien demanda) | No (doc no lo modela) | 1 audiencia | **Reposición** | No |
| **Demandante · Doble** | **Sí** | **Sí** | art. 77 + 80 | **Apelación** | **Sí** |
| **Demandado · Única** | **No** (recibimos la demanda) | Solo **reforma** | 1 audiencia | **Reposición** | No |
| **Demandado · Doble** | **Solo registro** (fecha + auto, sin decisión) | **Sí** | art. 77 + 80 | **Apelación** | **Sí** |

> Clave: la **calificación con decisión** (admite/inadmite→subsanar/rechaza→recurso) es del
> **demandante** (es *nuestra* demanda la que el juez califica). Como **demandado** no
> subsanamos ni recurrimos la admisión de la demanda contraria: en doble solo **registramos**
> el auto admisorio; en única ni eso (vamos directo a traslado).

---

## CASO 1 — DEMANDANTE · ÚNICA INSTANCIA

```
0) CREACIÓN  → Cliente · rol=Demandante · instancia=Única · ¿requiere poder?(→poder.pdf)
1) PRESENTACIÓN / RADICACIÓN  demanda.pdf · pruebas.pdf? · anexos.pdf? · radicacion.pdf?
                              · fechaRadicacion · radicado · juzgado
2) CALIFICACIÓN  fechaAuto + auto-calificacion.pdf
     [ADMISIÓN]   → (3)
     [INADMISIÓN] → SUBSANACIÓN (⏱5 días háb.): escrito-subsanacion.pdf · fechaSubsanacion
                      [ADMITIR]  → fechaAdmisionTrasSubsanacion + auto-admision-tras-subsanacion.pdf → (3)
                      [RECHAZAR] → RECURSO ↓
     [RECHAZO]    → RECURSO (⏱3 días): recursoRechazo[NO/REPOSICIÓN/APELACIÓN]
                      (si hay) fechaRecursoRechazo + recurso.pdf + obs + decisión[FAV/DESFAV]
                      FAV → (3) · DESFAV/NO → ARCHIVO(fin)
3) ¿RETIRO art.67?  SÍ→ARCHIVO(fin) · NO→sigue
4) TRASLADO Y NOTIFICACIÓN  fechaNotificacion + notificacion.pdf · ⏱10 días háb.
5) CITACIÓN A AUDIENCIA  auto-citacion.pdf + fechaAudiencia       ◄ citación PRIMERO (única)
6) PREPARACIÓN DE LA AUDIENCIA  ¿conciliable? · documentos? · observaciones
7) AUDIENCIA ÚNICA (etapas de la audiencia)
     ¿se concilia? SÍ→acuerdo+fecha+obs→TERMINA por conciliación · NO→sigue
     excepciones previas · saneamiento · fijación del litigio · decreto y práctica de pruebas · alegatos
     fechaSentencia + sentencia.pdf · decisión[FAVORABLE/DESFAVORABLE]
8) RECURSO = REPOSICIÓN (⏱3 días)
     ¿se interpone? NO→TERMINACIÓN
                    SÍ→forma[EN AUDIENCIA / POR ESCRITO(3 días)→fecha+recurso.pdf]
                       decisión recurso[FAVORABLE/DESFAVORABLE] + fecha
9) TERMINACIÓN (fin)
```
- **No** hay contestación/reforma/reconvención, **ni** 2ª instancia (única = sin apelación).
- Calificación **idéntica** a Demandante·Doble (mismas ramas y campos).

---

## CASO 2 — DEMANDANTE · DOBLE INSTANCIA  *(detalle completo en `design.md`)*

```
0) CREACIÓN → Cliente · Demandante · Doble · ¿poder?
1) PRESENTACIÓN / RADICACIÓN   (igual que Caso 1)
2) CALIFICACIÓN  → [ADMISIÓN→(3)] · [INADMISIÓN→SUBSANACIÓN→ADMITIR(+auto admisorio)→(3) / RECHAZAR→RECURSO] · [RECHAZO→RECURSO]
   (RECURSO: FAV→(3) · DESFAV/NO→ARCHIVO)
3) ¿RETIRO art.67?  SÍ→ARCHIVO · NO→sigue
4) TRASLADO Y NOTIFICACIÓN  ⏱10 días háb.
5) CONTESTACIÓN  ¿contestaron?(SÍ→contestacion.pdf / NO→auto-silencio.pdf) ·
                 ¿reforma?(SÍ→demanda-reformada.pdf+fecha) ·
                 ¿reconvención?(SÍ→reconvencion.pdf→decisión juez ADMITIR/INADMITIR/RECHAZAR + sub-flujo + traslado 10d + contestación reconv.)
6) PREPARACIÓN DE LA AUDIENCIA      ◄ preparación PRIMERO (doble)
7) CITACIÓN A AUDIENCIA
8) AUDIENCIA ART. 77  (¿concilia?→termina · excepciones · saneamiento · fijación · DECRETO de pruebas)
9) AUDIENCIA ART. 80  (PRÁCTICA · alegatos · fechaSentencia+sentencia.pdf · decisión 1ª[FAV/DESFAV])
10) APELACIÓN (⏱3 días)  ¿se interpone? NO→TERMINACIÓN · SÍ→forma→¿el juez concede? NO→TERMINACIÓN · SÍ→2ª INSTANCIA
S1) REMISIÓN AL TRIBUNAL      fechaRemision2inst + radicado2inst
S2) SUSTENTACIÓN             fechaSustentacion + escrito-sustentacion.pdf + auto-2inst.pdf
S3) AUDIENCIA 2ª INSTANCIA   fechaAudiencia2inst + acta-2inst.pdf? + alegatos
S4) SENTENCIA 2ª INSTANCIA   fechaSentencia2inst + sentencia-2inst.pdf + decisión[CONFIRMA/REVOCA/MODIFICA]
11) TERMINACIÓN (ejecutoriada)
```

---

## CASO 3 — DEMANDADO · ÚNICA INSTANCIA

```
0) CREACIÓN  → Cliente · rol=Demandado · instancia=Única · ¿requiere poder?(→poder.pdf)
1) PRESENTACIÓN (DEMANDA RECIBIDA)  demanda.pdf · pruebas.pdf? · anexos.pdf? · radicado · juzgado
                                    (sin fechaRadicacion: la radicó la contraparte)
   — SIN etapa de calificación (no calificamos la demanda contraria) —
2) ¿RETIRO art.67?  SÍ→ARCHIVO(fin) · NO→sigue
   ¿REFORMA de la demanda?  SÍ→demanda-reformada.pdf + fecha · NO→nada
3) TRASLADO Y NOTIFICACIÓN  fechaNotificacion + notificacion.pdf · ⏱10 días háb. (para NUESTRA contestación)
4) CITACIÓN A AUDIENCIA  auto-citacion.pdf + fechaAudiencia    ◄ citación PRIMERO (única)
5) PREPARACIÓN DE LA AUDIENCIA  ¿conciliable? · documentos? · observaciones
6) AUDIENCIA ÚNICA (etapas)  ¿concilia?→termina · excepciones · saneamiento · fijación · decreto y práctica · alegatos
                             · fechaSentencia + sentencia.pdf · decisión[FAV/DESFAV]
7) RECURSO = REPOSICIÓN (⏱3 días)  ¿se interpone? → forma → decisión[FAV/DESFAV]
8) TERMINACIÓN (fin)
```
- El flujo más corto: sin calificación, sin reconvención, sin 2ª instancia.
- Sí trae **reforma** (el doc la pone en demandado·única).

---

## CASO 4 — DEMANDADO · DOBLE INSTANCIA

```
0) CREACIÓN  → Cliente · rol=Demandado · instancia=Doble · ¿requiere poder?(→poder.pdf)
1) PRESENTACIÓN (DEMANDA RECIBIDA)  demanda.pdf · pruebas.pdf? · anexos.pdf? · radicado · juzgado
2) ADMISIÓN (SOLO REGISTRO)  fechaAdmision + auto-calificacion.pdf
   — sin decisión/subsanación/rechazo: como demandado solo registramos que se admitió —
3) ¿RETIRO art.67?  SÍ→ARCHIVO(fin) · NO→sigue
4) TRASLADO Y NOTIFICACIÓN  fechaNotificacion + notificacion.pdf · ⏱10 días háb. (nuestra contestación)
5) CONTESTACIÓN  ¿contestaron?(SÍ→contestacion.pdf / NO→auto-silencio.pdf) ·
                 ¿reforma?(SÍ→demanda-reformada.pdf+fecha) ·
                 ¿reconvención?(SÍ→reconvencion.pdf→decisión juez + sub-flujo + traslado 10d + contestación reconv.)
6) PREPARACIÓN DE LA AUDIENCIA      ◄ preparación PRIMERO (doble)
7) CITACIÓN A AUDIENCIA
8) AUDIENCIA ART. 77  (¿concilia?→termina · excepciones · saneamiento · fijación · DECRETO de pruebas)
9) AUDIENCIA ART. 80  (PRÁCTICA · alegatos · fechaSentencia+sentencia.pdf · decisión 1ª[FAV/DESFAV])
10) APELACIÓN (⏱3 días)  ¿se interpone? → forma → ¿el juez concede? → 2ª INSTANCIA / TERMINACIÓN
S1–S4) SEGUNDA INSTANCIA  (igual que Caso 2: remisión → sustentación → audiencia → sentencia 2ª[CONFIRMA/REVOCA/MODIFICA])
11) TERMINACIÓN (ejecutoriada)
```
- Como demandado, la admisión es **solo registro** (sin las 3 ramas de decisión).
- Contestación/reconvención y 2ª instancia **iguales** que Caso 2.

---

## Mejoras de consistencia detectadas al alinear los 4 (vs. el modelo actual)

1. **Demandado · admisión = solo registro.** Hoy la etapa `admision` exige `decisionAuto`
   (con sus ramas inadmisión/subsanación/rechazo) para todo el que la tenga, incluido
   demandado·doble. Pero el demandado **no califica** la demanda contraria → debe registrar
   solo `fechaAdmision` + `auto-calificacion.pdf`. **Mejora:** `decisionAuto` (y subsanación/
   recurso de rechazo) solo cuando `rol = Demandante`.
2. **Calificación con decisión = solo demandante.** Subsanación y recurso-de-rechazo deben
   gatear por `rol = Demandante` (no por `{alguna:[Demandante, Doble]}` como hoy, que las
   ofrecería en demandado·doble).
3. **Orden prep↔citación por instancia, en AMBOS roles.** Única (1 y 3): citación→preparación.
   Doble (2 y 4): preparación→citación.
4. **2ª instancia en AMBOS doble** (2 y 4), no solo demandante.
5. **Reforma:** presente en demandado·única (Caso 3), demandante·doble y demandado·doble
   (en contestación). El doc **no** la trae en demandante·única → no se ofrece ahí.
6. **Contestación (¿contestaron? + reconvención):** solo en los **doble** (2 y 4). El doc no
   modela contestación explícita en los única.

## Decisiones a confirmar con el usuario (antes de implementar los 4)

- **D1.** ¿Demandado·doble registra la admisión **sin** decisión (solo fecha + auto)? *(recomendado: sí — el demandado no califica)*
- **D2.** ¿Subsanación/recurso-de-rechazo quedan **solo para demandante**? *(recomendado: sí)*
- **D3.** ¿2ª instancia también para **demandado·doble**? *(recomendado: sí)*
- **D4.** ¿Dejamos sin contestación/reforma explícita los **única** (salvo reforma en
  demandado·única), tal como el doc? *(recomendado: sí, fiel al doc)*
