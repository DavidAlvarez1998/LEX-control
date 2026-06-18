# Reclamación Administrativa

Reclamación respetuosa presentada ante la administración (o un particular) para obtener pronta resolución de lo solicitado (art. 23 C.P.; Ley 1755/2015). Representa al **reclamante/peticionario** (el cliente) frente a la **entidad o particular destinatario**. No es judicial (`esJudicial: false`); grupo `PETICION`, jurisdicción `CONSTITUCIONAL`.

## Fases de este caso

| Fase | Etapas (key) |
|------|--------------|
| 1. Elaboración / Solicitud | `borrador` (Elaboración de la reclamación) |
| 2. Radicación / Traslado (corre el plazo) | `radicada` (Radicación) |
| 3. Respuesta | `respondida` (Respuesta) — ramifica por `contestaron` SI/PARCIAL/NO |
| 4. Reiteración / Escalamiento | `reiteracion` (nueva reclamación, parcial) · `escala_tutela` (acción de tutela, NO/parcial) |
| 5. Cierre | `terminada` (Terminación, terminal) |

> Nota de motor: `reiteracion` y `escala_tutela` comparten `orden: 3` → son **ramas excluyentes** (decisión) ofrecidas según `contestaron`. La fase de Respuesta no tiene `terminal`, así que el cierre formal siempre pasa por `terminada` (orden 4).

## Grafo del flujo

```
0) ELABORACIÓN (borrador)
   req: entidad, tipoPeticion, queSolicita
        │
        ▼
1) RADICACIÓN (radicada)
   req: fechaRadicacion, nroRadicado + doc reclamacion.pdf
   requierePoder=Sí → doc poder.pdf
   ⏱ plazo desde fechaRadicacion · días HÁBILES
       General 15 · Documental 10 · Consulta 30
        │
        ▼  (se habilita solo si contestaron ∈ {SI, PARCIAL, NO})
2) RESPUESTA (respondida)
   ├ contestaron = SI       → req: fechaRespuesta + doc respuesta.pdf
   │                          → (cierre) ─────────────────────────► 4) TERMINACIÓN
   ├ contestaron = PARCIAL  → req: fechaRespuestaParcial, queFalto + doc respuesta.pdf
   │                          (opc: recurso.pdf)
   │                          ├─► 3a) REITERACIÓN  → crea NUEVA Reclamación Administrativa
   │                          └─► 3b) ESCALAR TUTELA → crea Acción de tutela
   └ contestaron = NO       → (observacionNoRespuesta opcional)
                              └─► 3b) ESCALAR TUTELA → crea Acción de tutela

3a) REITERACIÓN (reiteracion)      [orden 3, solo si contestaron=PARCIAL]
    crearDerivado → "Reclamación Administrativa" (copia datos+cliente+poder.pdf)
3b) ESCALAR A TUTELA (escala_tutela) [orden 3, solo si contestaron ∈ {NO, PARCIAL}]
    crearDerivado → "Acción de tutela" (copia cliente+poder.pdf)
        │
        ▼
4) TERMINACIÓN (terminada)  ★ terminal — "Reclamación terminada."
```

## Detalle por etapa (campo por campo)

### 0) Elaboración de la reclamación (`borrador`, orden 0)
Campos requeridos para avanzar: **entidad**, **tipoPeticion**, **queSolicita**.

Campos del formulario disponibles aquí:
- **entidad** [texto] (obligatorio) — Entidad o particular destinatario.
- **correo** [listaCorreos] (opcional) — Correos de la entidad; pueden ser varios (para enviar la petición a todos).
- **fechaRadicado** [fecha] (opcional) — Fecha en que se elabora/radica la reclamación. Es solo referencia; el término de respuesta NO corre desde aquí.
- **tipoPeticion** [select] (obligatorio) — ¿Tipo de reclamación? [General / Documental / Consulta]. Determina el plazo de respuesta en la etapa de Radicación: General → 15 háb · Documental → 10 háb · Consulta → 30 háb.
- **queSolicita** [multiselect] (obligatorio) — ¿Qué desea solicitar? Opciones: Información · Copia de documentos · Certificación · Historia laboral · Historia clínica · Estado de trámite · Pago pendiente · Reconocimiento de derecho · Corrección de información · Habeas data · Solicitud laboral · Salud · Seguridad social · Queja · Reclamo · Consulta · Otro.
  - → si incluye **Otro**: aparece **otroSolicita** [textoLargo] (obligatorio por `requeridoSi`) — Especifica qué solicitan.
- **detalle** [textoLargo] (opcional) — Detalle de la solicitud.
- **requierePoder** [boolean] (opcional) — ¿Requiere poder? Si =Sí, en Radicación se exigirá `poder.pdf`.
- **envio** [select] (opcional) — Medio de envío [Físico / Correo electrónico].

### 1) Radicación (`radicada`, orden 1)
Campos requeridos: **fechaRadicacion**, **nroRadicado**.
- **fechaRadicacion** [fecha] (obligatorio, soloFicha) — Fecha de radicación del proceso. **Desde aquí corre el término de respuesta (días hábiles).**
- **nroRadicado** [texto] (obligatorio, soloFicha) — Número de radicado.

Documentos:
- **reclamacion.pdf** — requerido siempre.
- **poder.pdf** — requerido solo si `requierePoder = true` (`requeridosSi`).

Plazo (⏱): `plazoDesdeCampo = fechaRadicacion`, `plazoTipoDias = habiles`, días según `tipoPeticion` (`plazoDiasPorValorDe`):
- General → **15 días hábiles**
- Documental → **10 días hábiles**
- Consulta → **30 días hábiles**

### 2) Respuesta (`respondida`, orden 2)
Se habilita (`disponibleSi`) solo cuando **contestaron** ∈ {SI, PARCIAL, NO}.
- **contestaron** [select] (opcional, soloFicha) — ¿Contestaron? [SI / PARCIAL / NO]. Es el campo que ramifica todo lo siguiente.

¿Contestaron? [SI / PARCIAL / NO] →
- **SI**: requeridos **fechaRespuesta** + doc **respuesta.pdf** (`requeridosSi`).
  - **fechaRespuesta** [fecha] (obligatorio si SI) — Fecha de la respuesta.
  - **numeroRespuesta** [texto] (opcional, visible si SI) — N.º de oficio/radicado de la respuesta.
  - **observacionesRespuesta** [textoLargo] (opcional, visible si SI).
  - No abre rama de escalamiento → camino directo a Terminación.
- **PARCIAL**: requeridos **fechaRespuestaParcial** + **queFalto** + doc **respuesta.pdf** (`requeridosSi`); doc opcional **recurso.pdf** (`opcionalesSi`).
  - **fechaRespuestaParcial** [fecha] (obligatorio si PARCIAL) — Fecha de la respuesta parcial.
  - **queFalto** [textoLargo] (obligatorio si PARCIAL) — ¿Qué quedó sin responder?
  - Abre **ambas** ramas de orden 3: Reiteración y Escalar a tutela.
- **NO**: sin campos/documentos requeridos.
  - **observacionNoRespuesta** [textoLargo] (opcional, visible si NO) — Observación del incumplimiento.
  - Abre solo la rama Escalar a tutela.

### 3a) Reiteración (respuesta parcial) (`reiteracion`, orden 3)
`disponibleSi`: **contestaron = PARCIAL**. Sin campos/documentos propios.
Acción `crearDerivado` → tipo destino **"Reclamación Administrativa"** (una nueva reclamación prellenada):
- `copiarDatos`: entidad, correo, tipoPeticion, queSolicita, detalle, requierePoder.
- `copiarCliente: true`.
- `copiarDocumentos`: poder.pdf.

### 3b) Escalar a acción de tutela (`escala_tutela`, orden 3)
`disponibleSi`: **contestaron ∈ {NO, PARCIAL}**. Sin campos/documentos propios.
Acción `crearDerivado` → tipo destino **"Acción de tutela"**:
- `copiarCliente: true`.
- `copiarDocumentos`: poder.pdf.
- (No `copiarDatos`: la tutela arranca con cliente y poder, sin copiar los sustantivos de la reclamación.)

### 4) Terminación (`terminada`, orden 4)
`terminal: true` · `resultado: "Reclamación terminada."` Sin campos ni documentos. Cierra el caso.

## Desenlaces posibles

1. **Terminación normal** (`terminada`) — único terminal del flujo. Se llega tras respuesta SI, o tras agotar/decidir las ramas de PARCIAL/NO.
2. **Reiteración** (`reiteracion`, solo PARCIAL) — escala a una **nueva Reclamación Administrativa** (no es terminal en sí; genera un proceso derivado).
3. **Escalamiento a tutela** (`escala_tutela`, NO o PARCIAL) — crea una **Acción de tutela** como proceso derivado.

> Las ramas 3a/3b no llevan `terminal: true`; producen un derivado y el proceso original aún debe cerrarse en `terminada`.

## Notas

- **Fuente de verdad = seed.** No hay doc fuente específico; el flujo legal implementado es el de `seed-tipos.json`. Términos legales declarados en la descripción (Ley 1755/2015): general 15 háb, documental 10, consulta 30 — coinciden con `plazoDiasPorValorDe`.
- **Dos fechas de radicación distintas (posible confusión):** `fechaRadicado` (referencia, en el form, "fecha en que se elabora/radica") vs `fechaRadicacion` (soloFicha, etapa Radicación, **desde aquí corre el plazo**). El plazo se ancla a `fechaRadicacion`, no a `fechaRadicado`.
- **Camino SI no es terminal:** con `contestaron=SI` no hay rama de escalamiento, pero el cierre sigue requiriendo pasar a `terminada` (orden 4); la etapa `respondida` no es terminal.
- **PARCIAL ofrece ambas salidas** (reiterar otra reclamación o saltar a tutela); **NO** ofrece solo tutela; **SI** no ofrece ninguna (va a terminación).
- **Huecos / inconsistencias detectados:**
  - `escala_tutela` NO copia `requierePoder` ni datos sustantivos a la tutela (`copiarDatos` ausente); solo cliente + poder.pdf. La nueva tutela arranca casi vacía. Posible hueco vs. la reiteración, que sí copia datos.
  - El plazo de Radicación usa la clave **`plazoDiasPorValorDe`** (mapa por valor de `tipoPeticion`), no `plazoDias` fijo. El motor debe soportar esta clave; si solo lee `plazoDias`, el término no se calcularía. Verificar soporte del motor.
  - `respondida` no tiene `accion` ni `terminal`: solo registra la respuesta. El avance a cierre/escalamiento depende de las etapas de orden 3/4, todas gateadas por `contestaron` (que es `soloFicha`, no requerido) — si nunca se setea `contestaron`, ni `respondida` ni las ramas se habilitan, pero `terminada` (orden 4, sin `disponibleSi`) sí queda alcanzable. Posible camino de cierre "silencioso" sin registrar respuesta.
