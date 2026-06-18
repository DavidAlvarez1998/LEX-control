# Flujos detallados — campo por campo (casos 1, 3 y 4)

Mismo nivel de detalle que `design.md` (caso 2 · Demandante·Doble). Aquí los otros 3 casos,
paso a paso, con cada documento, su obligatoriedad y las ramificaciones por opción.

Convención: `[tipo de campo]` · *(obligatorio)* / *(opcional)* · `[opción A / opción B]` ·
⏱ plazo. Bajo cada pregunta: qué pide cada respuesta.

═══════════════════════════════════════════════════════════════════════════════
# CASO 1 — DEMANDANTE · ÚNICA INSTANCIA
═══════════════════════════════════════════════════════════════════════════════

> Igual que Demandante·Doble en la **primera instancia**, pero: una sola audiencia, recurso de
> **reposición**, **sin** contestación/reconvención, **sin** segunda instancia, y el orden es
> **Citación → Preparación**.

### Fases de este caso — **5 de 6** (no aplica la Fase 5)
| Fase | Etapas de este caso |
|---|---|
| **1 · Demanda y admisión** | Presentación · Calificación → Subsanación → Recurso de rechazo · ¿Retiro art. 67? |
| **2 · Traslado** | Traslado y notificación (⏱10 días) — *sin contestación explícita en única* |
| **3 · Audiencia** | Citación → Preparación (orden única) · Audiencia única |
| **4 · Sentencia y recurso** | Sentencia (en la audiencia única) · **Reposición** |
| ~~5 · Segunda instancia~~ | — *no aplica (única no tiene 2ª instancia)* |
| **6 · Terminación / archivo** | Terminación · Archivo (retiro · rechazo · conciliación) |

## Fase 1 — Demanda y admisión

### 0) CREACIÓN
- **Cliente** `[buscar/seleccionar]` *(obligatorio)*
- **Rol** = **Demandante** · **Tipo de instancia** = **Única**
- **¿Requiere poder?** `[Sí / No]` → **Sí**: `poder.pdf` *(obligatorio)* · **No**: nada

### 1) PRESENTACIÓN / RADICACIÓN
- **`demanda.pdf`** *(obligatorio)*
- **`pruebas.pdf`** *(opcional)* · **`anexos.pdf`** *(opcional)* · **`radicacion.pdf`** *(opcional)*
- **Fecha de radicación** `[fecha]` · **N.º de radicado** `[texto]` · **Juzgado/corporación** `[texto]`

### 2) CALIFICACIÓN DE LA DEMANDA
- **Fecha del auto** `[fecha]` · **`auto-calificacion.pdf`** *(obligatorio)*
- **Decisión del auto** `[ADMISIÓN / INADMISIÓN / RECHAZO]`
  - **ADMISIÓN** → observaciones *(opcional)* → **sigue (3)**
  - **INADMISIÓN** → **2a) Subsanación** *(⏱ 5 días hábiles)*
    - **`escrito-subsanacion.pdf`** *(obligatorio)* · **Fecha en que se subsanó** `[fecha]`
    - **Decisión tras subsanar** `[ADMITIR / RECHAZAR]`
      - **ADMITIR** → **Fecha del auto de admisión** + **`auto-admision-tras-subsanacion.pdf`** → **sigue (3)**
      - **RECHAZAR** → **2b) Recurso contra el rechazo**
  - **RECHAZO** → **2b) Recurso contra el rechazo**

### 2b) RECURSO CONTRA EL RECHAZO *(⏱ 3 días)*
- **¿Interpone recurso?** `[NO / REPOSICIÓN / APELACIÓN]`
  - **NO** → **ARCHIVO (fin)**
  - **REPOSICIÓN / APELACIÓN** → **Fecha del recurso** + **`recurso.pdf`** + **Observaciones** + **Decisión** `[FAVORABLE / DESFAVORABLE]`
    - **FAVORABLE** → **sigue (3)** · **DESFAVORABLE** → **ARCHIVO (fin)**

### 3) ¿RETIRO DE LA DEMANDA? (art. 67) `[Sí / No]`
- **Sí** → **ARCHIVO (fin)** · **No** → sigue

## Fase 2 — Traslado *(sin contestación explícita en única)*

### 4) TRASLADO Y NOTIFICACIÓN
- **Fecha de la notificación** `[fecha]` · **`notificacion.pdf`** *(obligatorio)*
- ⏱ *Vencimiento para contestar = 10 días hábiles (calculado)*

## Fase 3 — Audiencia *(orden única: Citación → Preparación)*

### 5) CITACIÓN A AUDIENCIA
- **`auto-citacion.pdf`** *(obligatorio)* · **Fecha de citación** `[fecha]`

### 6) PREPARACIÓN DE LA AUDIENCIA
- **¿Se puede conciliar?** `[Sí / No]` · **Documentos para la audiencia** `[archivo, opc]` · **Observaciones** `[texto]`

### 7) AUDIENCIA ÚNICA (etapas de la audiencia)
- **¿Se concilia?** `[Sí / No]`
  - **Sí** → **Acuerdo** `[texto]` + acta/PDF + fecha + obs → **TERMINA por conciliación**
  - **No** → sigue
- **Excepciones previas** `[texto]` · **Saneamiento** `[texto]` · **Fijación del litigio** `[texto]` · **Decreto y práctica de pruebas** `[texto]` · **Alegatos** `[texto]`
- **Fecha de la sentencia** `[fecha]` + **`sentencia.pdf`** *(obligatorio)* · **Decisión** `[FAVORABLE / DESFAVORABLE]`

## Fase 4 — Recurso

### 8) RECURSO = REPOSICIÓN *(⏱ 3 días)*
- **¿Se interpone?** `[Sí / No]`
  - **No** → **TERMINACIÓN**
  - **Sí** → **Forma** `[EN AUDIENCIA / POR ESCRITO (3 días)]` → (si escrito) **Fecha** + **`recurso.pdf`** → **Decisión del recurso** `[FAVORABLE / DESFAVORABLE]` + **Fecha de la decisión**

## Fase 6 — Terminación
### 9) TERMINACIÓN (fin)   ·   *(no hay Fase 5 — única no tiene 2ª instancia)*

═══════════════════════════════════════════════════════════════════════════════
# CASO 3 — DEMANDADO · ÚNICA INSTANCIA
═══════════════════════════════════════════════════════════════════════════════

> El flujo más corto. Representamos al demandado: **no** hay calificación (no calificamos la
> demanda contraria), **no** hay reconvención-sub-flujo ni segunda instancia. Sí hay **reforma**.
> Orden **Citación → Preparación**.

### Fases de este caso — **5 de 6** (Fase 1 sin calificación; no aplica la Fase 5)
| Fase | Etapas de este caso |
|---|---|
| **1 · Demanda** | Presentación (demanda recibida) · ¿Retiro art. 67? · ¿Reforma? — *sin calificación* |
| **2 · Traslado** | Traslado y notificación (⏱10 días, para nuestra contestación) |
| **3 · Audiencia** | Citación → Preparación (orden única) · Audiencia única |
| **4 · Sentencia y recurso** | Sentencia · **Reposición** |
| ~~5 · Segunda instancia~~ | — *no aplica* |
| **6 · Terminación / archivo** | Terminación · Archivo (retiro · conciliación) |

## Fase 1 — Demanda recibida

### 0) CREACIÓN
- **Cliente** *(obligatorio)* · **Rol** = **Demandado** · **Instancia** = **Única**
- **¿Requiere poder?** → **Sí**: `poder.pdf` · **No**: nada

### 1) PRESENTACIÓN (DEMANDA RECIBIDA)
- **`demanda.pdf`** *(obligatorio)* · **`pruebas.pdf`** *(opc)* · **`anexos.pdf`** *(opc)*
- **N.º de radicado** `[texto]` · **Juzgado** `[texto]`
- *(No se pide fecha de radicación: la radicó la contraparte.)*
- *(No hay etapa de calificación.)*

### 2) ¿RETIRO DE LA DEMANDA? (art. 67) `[Sí / No]`
- **Sí** → **ARCHIVO (fin)** · **No** → sigue
### ¿REFORMA DE LA DEMANDA? `[Sí / No]`
- **Sí** → **`demanda-reformada.pdf`** + **Fecha de la reforma** · **No** → nada

## Fase 2 — Traslado

### 3) TRASLADO Y NOTIFICACIÓN
- **Fecha de la notificación** `[fecha]` · **`notificacion.pdf`** *(obligatorio)*
- ⏱ *Vencimiento para NUESTRA contestación = 10 días hábiles*

## Fase 3 — Audiencia *(orden única: Citación → Preparación)*

### 4) CITACIÓN A AUDIENCIA
- **`auto-citacion.pdf`** *(obligatorio)* · **Fecha de citación** `[fecha]`
### 5) PREPARACIÓN DE LA AUDIENCIA
- **¿Se puede conciliar?** `[Sí / No]` · **Documentos** `[archivo, opc]` · **Observaciones** `[texto]`
### 6) AUDIENCIA ÚNICA (etapas)
- **¿Se concilia?** Sí → acuerdo + acta/PDF + fecha + obs → **TERMINA por conciliación** · No → sigue
- **Excepciones previas** · **Saneamiento** · **Fijación del litigio** · **Decreto y práctica de pruebas** · **Alegatos** `[texto]`
- **Fecha de la sentencia** + **`sentencia.pdf`** *(obligatorio)* · **Decisión** `[FAVORABLE / DESFAVORABLE]`

## Fase 4 — Recurso
### 7) RECURSO = REPOSICIÓN *(⏱ 3 días)*
- **¿Se interpone?** No → **TERMINACIÓN** · Sí → **Forma** `[EN AUDIENCIA / POR ESCRITO (3 días)→fecha+recurso.pdf]` → **Decisión** `[FAVORABLE / DESFAVORABLE]` + fecha

## Fase 6 — Terminación
### 8) TERMINACIÓN (fin)   ·   *(sin Fase 5)*

═══════════════════════════════════════════════════════════════════════════════
# CASO 4 — DEMANDADO · DOBLE INSTANCIA
═══════════════════════════════════════════════════════════════════════════════

> Como demandado en doble: la admisión es **solo registro** (sin decisión/subsanación/rechazo).
> Tiene contestación/reconvención completas y **segunda instancia** (igual que el caso 2).
> Orden **Preparación → Citación**.

### Fases de este caso — **las 6** (Fase 1 con admisión solo-registro)
| Fase | Etapas de este caso |
|---|---|
| **1 · Demanda y admisión** | Presentación (recibida) · **Admisión = solo registro** (fecha + auto, sin decisión) · ¿Retiro art. 67? |
| **2 · Traslado y contestación** | Traslado y notificación (⏱10 días) · Contestación (reforma · reconvención + sub-flujo) |
| **3 · Audiencias** | Preparación → Citación (orden doble) · Audiencia art. 77 → Audiencia art. 80 |
| **4 · Sentencia y recurso** | Sentencia (art. 80) · Apelación (¿interpone? → ¿concede?) |
| **5 · Segunda instancia** | Remisión → Sustentación → Audiencia 2ª → Sentencia 2ª (CONFIRMA/REVOCA/MODIFICA) |
| **6 · Terminación / archivo** | Terminación · Archivo (retiro · conciliación) |

## Fase 1 — Demanda y admisión

### 0) CREACIÓN
- **Cliente** *(obligatorio)* · **Rol** = **Demandado** · **Instancia** = **Doble**
- **¿Requiere poder?** → **Sí**: `poder.pdf` · **No**: nada

### 1) PRESENTACIÓN (DEMANDA RECIBIDA)
- **`demanda.pdf`** *(obligatorio)* · **`pruebas.pdf`** *(opc)* · **`anexos.pdf`** *(opc)*
- **N.º de radicado** `[texto]` · **Juzgado/corporación** `[texto]`

### 2) ADMISIÓN (SOLO REGISTRO)
- **Fecha de la admisión** `[fecha]` · **`auto-calificacion.pdf`** *(obligatorio)*
- *(No se pide `decisionAuto`; no se abren subsanación ni recurso de rechazo — no calificamos la demanda contraria.)*

### 3) ¿RETIRO DE LA DEMANDA? (art. 67) `[Sí / No]`
- **Sí** → **ARCHIVO (fin)** · **No** → sigue

## Fase 2 — Traslado y contestación

### 4) TRASLADO Y NOTIFICACIÓN
- **Fecha de la notificación** `[fecha]` · **`notificacion.pdf`** *(obligatorio)*
- ⏱ *Vencimiento para NUESTRA contestación = 10 días hábiles*

### 5) CONTESTACIÓN
- **¿Contestaron la demanda?** `[Sí / No]`
  - **Sí** → **Fecha** + **`contestacion.pdf`** · **No** → **Fecha** + **`auto-silencio.pdf`**
- **¿Se presentó reforma?** `[Sí / No]` → **Sí**: **`demanda-reformada.pdf`** + fecha · **No**: nada
- **¿Se presentó reconvención?** `[Sí / No]`
  - **No** → nada
  - **Sí** → **Fecha** + **`reconvencion.pdf`** + **Decisión del juez** `[ADMITIR / INADMITIR / RECHAZAR]`
    - **ADMITIR** → `auto-reconvencion.pdf` + traslado reconv. (⏱ 10 días háb., fecha notif.) → **¿Contestaron la reconvención?** Sí→`contestacion-reconvencion.pdf` / No→`auto-silencio-reconvencion.pdf`
    - **INADMITIR** → `auto-reconvencion.pdf` + **`subsanacion-reconvencion.pdf`** + fecha → **Decisión** `[ADMITIR / RECHAZAR]`: ADMITIR→`auto-admision-reconvencion.pdf` + traslado→contestación · RECHAZAR→`auto-rechazo-reconvencion.pdf` → archivo de la reconvención
    - **RECHAZAR** → `auto-rechazo-reconvencion.pdf` + fecha → archivo de la reconvención
  - *(El proceso principal continúa a la audiencia en todos los casos.)*

## Fase 3 — Audiencias *(orden doble: Preparación → Citación)*

### 6) PREPARACIÓN DE LA AUDIENCIA
- **¿Se puede conciliar?** `[Sí / No]` · **Documentos para la audiencia** `[archivo, opc]` · **Observaciones** `[texto]`
### 7) CITACIÓN A AUDIENCIA
- **`auto-citacion.pdf`** *(obligatorio)* · **Fecha de citación** `[fecha]`
### 8) AUDIENCIA ART. 77
- **¿Se concilia?** Sí → acuerdo + fecha + obs → **TERMINA por conciliación** · No → sigue
- **Excepciones previas** · **Saneamiento** · **Fijación del litigio** · **Decreto de pruebas** `[texto]`
### 9) AUDIENCIA ART. 80 (trámite y juzgamiento)
- **Práctica de pruebas** · **Alegatos** `[texto/PDF]`
- **Fecha de la sentencia** + **`sentencia.pdf`** *(obligatorio)* · **Decisión (1ª inst.)** `[FAVORABLE / DESFAVORABLE]`

## Fase 4 — Sentencia y recurso

### 10) APELACIÓN CONTRA LA SENTENCIA *(⏱ 3 días)*
- **¿Se interpone apelación?** `[Sí / No]`
  - **No** → **TERMINACIÓN** (1ª inst. en firme)
  - **Sí** → **Forma** `[EN AUDIENCIA / POR ESCRITO (3 días)→fecha+apelacion.pdf]`
    - **¿El juez la concede?** `[Sí / No]`
      - **No** → **TERMINACIÓN** (1ª inst. en firme)
      - **Sí** → **Segunda instancia ▼**

## Fase 5 — Segunda instancia (Tribunal Superior — Sala Laboral)

### S1) REMISIÓN AL TRIBUNAL — **Fecha de remisión/reparto** + **N.º de radicado 2ª instancia**
### S2) SUSTENTACIÓN DEL RECURSO — **Fecha** + **`escrito-sustentacion.pdf`** *(obligatorio)* + **`auto-2inst.pdf`** + fecha
### S3) AUDIENCIA DE 2ª INSTANCIA — **Fecha** + **`acta-2inst.pdf`** *(opcional)* + **Alegatos** `[texto]`
### S4) SENTENCIA DE 2ª INSTANCIA — **Fecha** + **`sentencia-2inst.pdf`** *(obligatorio)* + **Decisión** `[CONFIRMA / REVOCA / MODIFICA]`

## Fase 6 — Terminación
### 11) TERMINACIÓN (sentencia ejecutoriada — fin)

═══════════════════════════════════════════════════════════════════════════════

## Nota de consistencia (los 4 casos)
- **Calificación con decisión** (subsanación/recurso de rechazo) → **solo casos 1 y 2** (demandante).
- **Admisión solo-registro** → **caso 4** (demandado·doble). **Caso 3** no tiene admisión.
- **Contestación/reconvención** → **solo doble** (casos 2 y 4). **Caso 3** solo trae reforma.
- **Segunda instancia** → **solo doble** (casos 2 y 4).
- **Orden Prep↔Citación** → única (1, 3): Citación→Preparación · doble (2, 4): Preparación→Citación.
