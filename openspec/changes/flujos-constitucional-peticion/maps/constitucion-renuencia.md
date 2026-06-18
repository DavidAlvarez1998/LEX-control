# Constitución de Renuencia

Reclamo previo dirigido a la autoridad o particular para **constituir la renuencia**, requisito de procedibilidad de la **acción de cumplimiento** (art. 8 Ley 393/1997). Representamos al peticionario/cliente que exige el cumplimiento de un deber legal: si transcurridos los días de plazo no se atiende o se reitera el incumplimiento, la renuencia queda constituida y habilita escalar a tutela. No es judicial (`esJudicial: false`); grupo **PETICION**, jurisdicción **CONSTITUCIONAL**.

> Fuente de verdad = el doc "DERECHO DE PETICIÓN - JUAN DAVID" (sección CONSTITUCIÓN DE RENUENCIA LEY 393) + el seed (`prisma/seed-tipos.json`). El doc fija dos puntos antes marcados como huecos: **plazo 15 días hábiles** ("General – (15 días hábiles)") y **escalamiento → Acción de Tutela** ("ACCIÓN DE TUTELA / Acción de tutela - Cargar PDF"). Ambos son INTENCIONALES (confirmado con el usuario 2026-06-18): aunque jurídicamente la renuencia precede a la acción de cumplimiento (art. 8) y el art. 8 cita 10 días, **el doc manda** → tutela + 15 hábiles.

## Fases de este caso

5 etapas agrupadas en 4 fases. El término legal del art. 8 son 10 días; el seed implementa el plazo de la etapa de Radicación en **15 días hábiles** (ver Notas).

| Fase | Etapas de este caso |
|---|---|
| **1 · Elaboración** | Elaboración de la renuencia *(borrador)* — exige `entidad` + `solicitud` |
| **2 · Radicación y vencimiento** | Radicación *(radicada)* — sube `renuencia.pdf` (+`poder.pdf` si aplica) · ⏱ **15 días hábiles** desde `fechaRadicacion` |
| **3 · Respuesta** | Respuesta *(respondida)* — según `contestaron` = SI / PARCIAL / NO |
| **4 · Escalamiento / Cierre** | Escalar a acción de tutela *(escala_tutela, crearDerivado)* · Terminación *(terminada, terminal)* |

## Grafo del flujo

```
0) ELABORACIÓN (borrador)
   req: entidad, solicitud
   │
1) RADICACIÓN (radicada)                    ⏱ 15 días hábiles desde fechaRadicacion
   req: fechaRadicacion, nroRadicado
   doc req: renuencia.pdf
   doc req si requierePoder=true: poder.pdf
   │
2) RESPUESTA (respondida)   [disponible solo si contestaron ∈ {SI, PARCIAL, NO}]
   ├ contestaron=SI      → doc opc: respuesta.pdf  ──────────────┐
   ├ contestaron=PARCIAL → doc opc: respuesta.pdf  ──┐           │
   └ contestaron=NO      → (sin doc opcional)        │           │
                                                     ▼           ▼
                                    (orden 3) ESCALAR        (orden 4)
                                                     │
3) ESCALAR A ACCIÓN DE TUTELA (escala_tutela)   [disponible si contestaron ∈ {NO, PARCIAL}]
   accion: crearDerivado → "Acción de tutela"
           copiarCliente=true · copiarDocumentos=[poder.pdf]
   (escala a otro proceso; no es terminal del propio flujo)
   │
4) TERMINACIÓN (terminada)  ── terminal:true
   resultado: "Renuencia constituida."  → FIN
```

Las etapas con orden 3 (Escalar) y orden 4 (Terminación) **no comparten orden**, así que no son ramas excluyentes entre sí: Escalar (3) está gateada por `contestaron ∈ {NO, PARCIAL}`; Terminación (4) es el cierre. Si contestaron=SI, Escalar no se ofrece y el flujo va directo a Terminación.

## Detalle por etapa (campo por campo)

### Campos del formulario de creación (esquemaFormulario)
Campos visibles al crear / editar la ficha (no son etapa; alimentan los gates):
- **Entidad o autoridad renuente** `entidad` [texto] *(obligatorio)*
- **Correos electrónicos de la entidad** `correo` [listaCorreos] *(opcional)* — varios; sirven para enviar la petición a todos.
- **Deber legal o acto cuyo cumplimiento se exige** `solicitud` [textoLargo] *(obligatorio)*
- **Fecha de radicación de solicitud** `fechaRadicado` [fecha] *(opcional)* — referencia; el término corre desde `fechaRadicacion`.
- **¿Requiere poder?** `requierePoder` [boolean] *(opcional)* — si `true`, la etapa Radicación exige `poder.pdf`.
- **Medio de envío** `envio` [select: Físico / Correo electrónico] *(opcional)*
- **Fecha de radicación del proceso** `fechaRadicacion` [fecha] *(opcional, soloFicha)* — desde aquí corren los 15 días hábiles.
- **Número de radicado** `nroRadicado` [texto] *(opcional, soloFicha)*
- **¿Contestaron?** `contestaron` [select: SI / PARCIAL / NO] *(opcional, soloFicha)* — gatea las etapas Respuesta y Escalar.
- **Anexar/observaciones de la contestación** `observacionContestacion` [textoLargo] *(opcional, soloFicha)*

*(Ningún campo tiene `mostrarSi`: todos los del esquema son siempre visibles.)*

### 0) Elaboración de la renuencia — `borrador` (orden 0)
- Campos requeridos para avanzar: **`entidad`** + **`solicitud`**.
- Sin documentos, sin plazo, sin gate de disponibilidad (siempre el punto de entrada).

### 1) Radicación — `radicada` (orden 1)
- Campos requeridos: **`fechaRadicacion`** + **`nroRadicado`**.
- Documento requerido: **`renuencia.pdf`**.
- Documento requerido condicional: **¿Requiere poder?** → `requierePoder=true`: **`poder.pdf`** *(obligatorio)* · `false`/vacío: nada.
- ⏱ Plazo: **15 días hábiles** desde **`fechaRadicacion`** (`plazoDesdeCampo: fechaRadicacion`, `plazoTipoDias: habiles`, `plazoDias: 15`).

### 2) Respuesta — `respondida` (orden 2)
- **Disponible solo si** `contestaron ∈ {SI, PARCIAL, NO}` (es decir, hay que registrar la respuesta antes de que la etapa se ofrezca).
- **¿Contestaron?** [SI / PARCIAL / NO]:
  - **SI** → documento opcional **`respuesta.pdf`** (no bloquea).
  - **PARCIAL** → documento opcional **`respuesta.pdf`** (no bloquea).
  - **NO** → sin documento opcional definido.
- Sin campos requeridos propios ni plazo. Las observaciones de la contestación se llevan en `observacionContestacion` (campo soloFicha del esquema).

### 3) Escalar a acción de tutela — `escala_tutela` (orden 3)
- **Disponible solo si** `contestaron ∈ {NO, PARCIAL}` (incumplimiento total o parcial).
- **Acción:** `crearDerivado` → crea un proceso **"Acción de tutela"**, con `copiarCliente=true` y `copiarDocumentos=[poder.pdf]`.
- No es terminal: escala a otro proceso; el flujo de renuencia puede cerrarse en Terminación.

### 4) Terminación — `terminada` (orden 4)
- **terminal:true** · **resultado:** "Renuencia constituida."
- Sin campos, documentos ni gate. Cierra el caso.

## Desenlaces posibles
1. **Renuencia constituida (Terminación, terminal)** — desenlace formal del trámite: transcurrido el plazo sin atención o con reiteración del incumplimiento, queda constituida la renuencia (resultado del seed: "Renuencia constituida.").
2. **Escalamiento a Acción de tutela** — si `contestaron ∈ {NO, PARCIAL}`, se ofrece `escala_tutela` (crearDerivado), generando un proceso de tutela con cliente y poder copiados. No cierra por sí mismo el trámite de renuencia.
3. **Contestación favorable (SI)** — se registra `respuesta.pdf` opcional; no se ofrece el escalamiento; el caso puede ir a Terminación.

## Notas
- **Plazo 15 vs 10 días — RESUELTO:** el art. 8 Ley 393/1997 cita "transcurridos **10 días**", pero el **doc fuente Juan David dice "General – (15 días hábiles)"** y el seed implementa **`plazoDias: 15` (hábiles)**. NO es inconsistencia: créele al doc → 15 hábiles es lo correcto (confirmado con el usuario 2026-06-18).
- **Escalamiento → Tutela (no Cumplimiento) — RESUELTO:** jurídicamente la renuencia es requisito de la acción de cumplimiento, pero el **doc fuente modela explícitamente el escalamiento a Acción de Tutela** ("ACCIÓN DE TUTELA / Acción de tutela - Cargar PDF"). El seed (`escala_tutela` → "Acción de tutela") es fiel al doc. Mantener (confirmado con el usuario 2026-06-18).
- **`fechaRadicado` vs `fechaRadicacion`:** son dos campos distintos. `fechaRadicado` (fecha de radicación de **la solicitud**) es solo referencia; el plazo corre desde `fechaRadicacion` (fecha de radicación **del proceso**, soloFicha). Convención frágil por nombres casi idénticos.
- **`escala_tutela` no es terminal y no exige `poder.pdf`:** `copiarDocumentos=[poder.pdf]` se copia al derivado solo si existe; si en Radicación `requierePoder=false`, no habrá `poder.pdf` que copiar (la copia simplemente no aporta ese documento). No es un error, pero la copia es condicional al estado previo.
- **No hay rama explícita de "no escalar / archivo sin tutela":** con `contestaron=NO/PARCIAL` el flujo ofrece Escalar (3) y Terminación (4); no existe una etapa de archivo distinta. El cierre siempre es Terminación con resultado "Renuencia constituida.", aunque la respuesta haya sido SI (cumplimiento) — el seed no diferencia el resultado de cierre por `contestaron`. Hueco menor: un cumplimiento total (SI) termina con el mismo literal "Renuencia constituida.", que semánticamente no aplicaría.
- **Sin `mostrarSi` en ningún campo:** todos los campos del esquema son siempre visibles; la lógica condicional vive únicamente en `disponibleSi` (etapas) y `requeridosSi`/`opcionalesSi` (documentos).
