# Flujo end-to-end — ejecutivo de mínima cuantía + API Rama Judicial

> Objetivo de este documento: dejar **completamente claro el flujo** antes de codificar.
> Toma el flujo ya implementado del ejecutivo de mínima cuantía
> ([[proceso-ejecutivo-minima-cuantia]], fuente: `proceso-ejecutivo-minima-cuantia/flujo-completo.md`)
> y le superpone qué **automatiza** la API de actuaciones (contrato en `specs/rama-judicial/spec.md`).
> Verificado contra el motor real (`maquina-etapas.ts`, `procesos.service.ts`, `diasHabiles.ts`).

## 1. El flujo que propone el usuario — ¿es correcto?

> "Creamos la demanda; cuando el juzgado responde con el radicado, se pega y ahí empieza el
> consumo de la API."

**Sí, es correcto.** Aterrizado a las etapas reales del tipo:

```
Etapa 1 radicacion          ── el ABOGADO trabaja: llena campos + GENERA demanda/poder/cautelares
        │                       (aún NO hay radicado; la API todavía no aplica)
        ▼   (radica en el juzgado físico/online)
Etapa 2 radicacionJuzgado   ── el JUZGADO devuelve el radicado de 23 díg.
        │                       → se PEGA en el proceso  ◀── AQUÍ EMPIEZA EL CONSUMO DE LA API
        ▼
Etapas 3..8 (calificacion → … → terminacion)
                             ── la API trae las ACTUACIONES y mantiene el expediente al día,
                                autollena algunos campos y SUGIERE hitos de etapa.
```

**Matiz clave (refinamiento):** el "consumo" tiene dos momentos distintos:

1. **Al pegar el radicado (validación inmediata, 1 request — Endpoint A):** confirmamos contra la
   Rama que el radicado existe y es el correcto, y traemos `idProceso` + `despacho` +
   `fechaUltimaActuacion` + `sujetosProcesales`. UX: *"✅ Radicado encontrado: JUZGADO 003 … —
   última actuación 2026-03-09"* o *"⚠️ aún no aparece en la Rama (procesos: [])"*. Esto evita
   pegar un radicado mal escrito del que luego dependemos.
2. **Sincronización de actuaciones (Endpoint B, repetible):** ya con `idProceso` cacheado, se
   descargan las actuaciones (todas las páginas) y se guardan las nuevas. Se dispara on-demand
   (botón "Actualizar") y/o por cron (decisión abierta §6).

## 2. Qué automatiza la API — CAMPOS

La API **no reemplaza** el trabajo del abogado (redactar/adjuntar); **enriquece** datos de
seguimiento. Lo que puede autollenar/sugerir, mapeado a nuestro modelo:

| Origen API | Campo nuestro | Cómo |
|---|---|---|
| Endpoint A `idProceso` | (nuevo) `Proceso.idProcesoRama` o `datos.idProcesoRama` | **cachear** para no repetir A en cada sync |
| Endpoint A `despacho` | `datos.juzgado` / `Proceso.despachoJuzgado` | **sugerir** al pegar radicado (el abogado confirma) |
| Endpoint A `fechaUltimaActuacion` | señal de "¿hay novedad?" | si no cambió desde el último sync, **saltar** el Endpoint B |
| Endpoint A `sujetosProcesales` | validación de partes | mostrar como verificación (no sobrescribe partes) |
| Endpoint B última actuación | `datos.ultimaActuacion` | **autollenar** (¡este campo ya lo usa la plantilla `memorial.pdf`!) → el memorial se genera sin `[[falta:]]` |
| Endpoint B fecha de un hito | campos-fecha de gating (p. ej. `fechaMandamiento`, `fechaNotificacion`, `fechaAdmision`) | **pre-rellenar como sugerencia** cuando se detecta el hito (§3) |

> Regla de oro: la API **propone**, el abogado **confirma**. Nunca sobrescribe en silencio un dato
> legal que el usuario ya escribió.

## 3. Qué automatiza la API — ETAPAS (con honestidad sobre los límites)

El texto de cada actuación es **libre y heterogéneo** ("RECIBE MEMORIALES ONLINE", "Auto que ordena
…", "Fijacion estado"). **No** mapea de forma determinista a nuestras etapas → **NO** se hace
auto-avance "a ciegas" por texto. En su lugar, dos mecanismos seguros:

### 3a. Detección de hitos → SUGERENCIA (no avance forzado)
Por keywords sobre `actuacion`/`anotacion` detectamos hitos probables y los **sugerimos** al abogado
(badge "posible avance a *Mandamiento de pago*"), pre-rellenando el campo-fecha correspondiente:

| Keyword en la actuación (heurística) | Hito / etapa sugerida | Campo-fecha que pre-rellena |
|---|---|---|
| "ADMITE" / "auto admisorio" | calificacion = Admite | `fechaAdmision` |
| "INADMITE" / "inadmisorio" | calificacion = Inadmite | `fechaAdmision` (+ abre subsanacion) |
| "MANDAMIENTO DE PAGO" / "libra mandamiento" | mandamientoPago | `fechaMandamiento` |
| "NOTIFIC…" / "Envió de Notificación" | notificación | `fechaNotificacion` |
| "EXCEPCIONES" / "contestación" | contesto = Sí (rama audiencia) | `fechaAudiencia` (pista) |
| "SENTENCIA" | sentencia / "seguir adelante" | — |
| "LIQUIDACIÓN" / "AVALÚO" / "REMATE" | impulsos/remate | `valorLiquidacion`/`fechaRemate` (pista) |
| "TERMINA" / "ARCHIVO" / "auto de terminación" | terminacion | `fechaTerminacion` |

### 3b. Auto-avance REAL solo donde el motor ya lo permite
El motor (`autoavanzarEtapas`) avanza **solo si es inequívoco Y se cumplen requisitos** (campos +
**documentos**). Como casi todas las etapas 3..8 exigen **ADJUNTAR un documento del juez**
(`auto-calificacion.pdf`, `mandamiento-pago.pdf`, `sentencia.pdf`, …), el avance **no** ocurrirá solo
por pre-rellenar una fecha: faltará el doc oficial que el abogado debe subir. **Esto es deseable** —
garantiza que no marquemos un estado legal sin su evidencia. Resultado: la API **acelera el
papeleo** (fecha + sugerencia + timeline), el abogado **adjunta y confirma**, y entonces el motor
avanza (a veces solo, vía `autoavanzarEtapas`, una vez subido el doc).

> Implicación: la automatización de etapas es **asistida**, no autónoma. Es lo correcto legalmente y
> encaja con el gating actual sin tocar el motor.

## 4. Dónde se ven las actuaciones (UI)

- La ficha del proceso (`procesos/[id]/page.tsx`) **carga `historial` pero NO lo pinta** → ahí va una
  **línea de tiempo**. Mostramos **dos fuentes** claramente separadas:
  - **Etapas internas** (nuestro `historial` = `EtapaProceso`): lo que gestiona el despacho.
  - **Actuaciones de la Rama** (nuevo): lo que publica el juzgado (fecha · actuación · anotación),
    con badge **"nueva"** desde el último sync y botón **"Actualizar"**.
- Al pegar el radicado: feedback inmediato de validación (Endpoint A) — ver §1.

## 5. Cómo encaja con el motor (sin romper nada)

- **Radicado:** ya se setea vía parámetro explícito (`updateProceso` con `body.radicado`) y espeja a
  la columna. El consumo se ata a "radicado seteado y validado".
- **Plazos:** al pre-rellenar `fechaNotificacion`/`fechaMandamiento` (sugerencia confirmada), el
  motor recalcula `fechaLimite` con días hábiles CO automáticamente (ya existe `derivarFechaLimite`).
- **Sync idempotente:** insertar solo actuaciones nuevas. La API no da id por actuación → clave
  natural `(procesoId, fechaActuacion, actuacion, anotacion)` o hash (anti-duplicado).
- **Persistencia:** modelo nuevo `ActuacionProceso` (decisión §6) — el `historial` de etapas NO se
  mezcla con las actuaciones del juzgado (son cosas distintas).

## 6. Decisiones abiertas que faltan cerrar (gating de la implementación)

1. **Disparo del sync** — recomendado: **on-demand** (validar al pegar + botón "Actualizar") en v1, y
   **cron nocturno** después (cuando haya volumen). ¿De acuerdo?
2. **Persistir actuaciones** — recomendado: **sí**, modelo `ActuacionProceso` (permite "nuevas",
   notificar y no depender de que la Rama responda). ¿De acuerdo?
3. **Alcance** — recomendado: **solo mínima cuantía** primero; el código sirve para cualquier
   `Proceso` con `radicado`, se amplía luego. ¿De acuerdo?
4. **Autollenado de campos** — ¿autollenar `ultimaActuacion` (para el memorial) y **sugerir**
   `juzgado` al validar? ¿O solo timeline y nada de tocar `datos`?
5. **Sugerencia de etapas** — ¿activamos la detección de hitos (§3a) en v1, o v1 = solo timeline +
   validación de radicado y dejamos las sugerencias para v2?
6. **Notificar novedades** — ¿avisar (in-app/correo, reusando [[correos-cuenta-invitacion-reset]])
   cuando aparezca una actuación nueva? Encaja con el spine Cliente+Proceso.
7. **idProceso** — cachear en columna nueva `Proceso.idProcesoRama` (recomendado) vs en `datos`.

## 7. Propuesta de fases (al cerrar §6)

- **v1 (núcleo):** validar radicado al pegar (Endpoint A) + `idProceso` cacheado + sync de
  actuaciones (Endpoint B, on-demand) + modelo `ActuacionProceso` + timeline en la ficha + badge
  "nuevas". Smoke real contra `66001333300320140049500`.
- **v2 (asistencia):** autollenar `ultimaActuacion`, sugerir `juzgado`, detección de hitos (§3a) con
  pre-rellenado de fechas, notificación de novedades, y cron nocturno con el batching anti-bloqueo.
