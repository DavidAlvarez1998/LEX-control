# Derecho de Petición

Trámite constitucional (no judicial, grupo `PETICION`, jurisdicción `CONSTITUCIONAL`) en el que el despacho presenta, en nombre del **cliente peticionario**, una petición respetuosa ante una entidad o particular (art. 23 C.P.; Ley 1755/2015) y hace seguimiento al término legal de respuesta hasta que la entidad contesta, se reitera o se escala a tutela.

## Fases de este caso

| Fase | Etapas (key) | Qué ocurre |
|------|--------------|------------|
| 1. Elaboración / Solicitud | `borrador` | Se arma la petición: destinatario, tipo, qué se solicita. |
| 2. Radicación / Vencimiento | `radicada` | Se radica el PDF (+ poder si aplica); arranca el plazo de respuesta (días hábiles según tipo). |
| 3. Respuesta | `respondida` | Se registra si la entidad contestó SÍ / PARCIAL / NO. |
| 4. Reiteración / Recurso | `reiteracion` | Sólo si fue PARCIAL: se genera un **nuevo DdP** prellenado (reiterar). |
| 5. Escalamiento | `escala_tutela` | Si NO o PARCIAL: se escala a **Acción de tutela** (proceso derivado). |
| 6. Cierre | `terminada` | Terminal: petición terminada. |

## Grafo del flujo

```
0) ELABORACIÓN (borrador)              campos req: entidad, tipoPeticion, queSolicita
       │
       ▼
1) RADICACIÓN (radicada)              📎 peticion.pdf  (+poder.pdf si requierePoder)
       │                              ⏱ plazo desde fechaRadicacion, días HÁBILES:
       │                                 General=15 · Documental=10 · Consulta=30
       ▼
   [se diligencia en ficha: contestaron = SI / PARCIAL / NO]
       │
2) RESPUESTA (respondida)   disponibleSi contestaron ∈ {SI, PARCIAL, NO}
       ├ SI       → campos req: fechaRespuesta · 📎 respuesta.pdf
       │            └────────────────────────────────────────────► 4) TERMINACIÓN ✔
       │
       ├ PARCIAL  → campos req: fechaRespuestaParcial, queFalto · 📎 respuesta.pdf
       │            (opcional 📎 recurso.pdf)
       │            ├ 3a) REITERACIÓN (reiteracion)  → crearDerivado: NUEVO Derecho de Petición
       │            │        (copia entidad, correo, tipoPeticion, queSolicita, detalle,
       │            │         requierePoder, cliente, poder.pdf)
       │            └ 3b) ESCALAR A TUTELA (escala_tutela) → crearDerivado: Acción de tutela
       │                     (copia cliente, poder.pdf)
       │
       └ NO       → (sin campos/documentos requeridos)
                    └ 3b) ESCALAR A TUTELA (escala_tutela) → crearDerivado: Acción de tutela
                             (copia cliente, poder.pdf)

4) TERMINACIÓN (terminada)  terminal ✔  resultado: "Petición terminada."
```

Nota de orden: `reiteracion` y `escala_tutela` comparten `orden:3` (ramas excluyentes de decisión); `terminada` es `orden:4`. Ambas ramas de orden 3 son acciones `crearDerivado` (escalan a otro proceso); no marcan terminal por sí mismas — el cierre formal es `terminada`.

## Detalle por etapa (campo por campo)

### 0) Elaboración de la petición — `borrador` (orden 0)
Campos requeridos para avanzar: `entidad`, `tipoPeticion`, `queSolicita`.

Campos del formulario:
- **entidad** [texto] (obligatorio) — Entidad o particular destinatario.
- **correo** [listaCorreos] (opcional) — Correos de la entidad (varios; para enviar la petición).
- **fechaRadicado** [fecha] (opcional) — Fecha en que se elabora/radica la solicitud (referencia; el término NO corre desde aquí).
- **tipoPeticion** [select] (obligatorio) — ¿Tipo de DdP? [General / Documental / Consulta]
  - General → término 15 días hábiles
  - Documental → 10 días hábiles
  - Consulta → 30 días hábiles
- **queSolicita** [multiselect] (obligatorio) — opciones: Información · Copia de documentos · Certificación · Historia laboral · Historia clínica · Estado de trámite · Pago pendiente · Reconocimiento de derecho · Corrección de información · Habeas data · Solicitud laboral · Salud · Seguridad social · Queja · Reclamo · Consulta · Otro.
  - **Otro** → muestra y exige **otroSolicita** [textoLargo] (Especifica qué solicitan).
- **detalle** [textoLargo] (opcional) — Detalle de la solicitud.
- **requierePoder** [boolean] (opcional) — ¿Requiere poder? Si =true, en la etapa de radicación se exige `poder.pdf`.
- **envio** [select] (opcional) — Medio de envío [Físico / Correo electrónico].

### 1) Radicación — `radicada` (orden 1)
Campos requeridos: `fechaRadicacion`, `nroRadicado`.
- **fechaRadicacion** [fecha, soloFicha] — Fecha de radicación del proceso. **Desde aquí corre el término** (días hábiles).
- **nroRadicado** [texto, soloFicha] — Número de radicado.

Documentos requeridos: `peticion.pdf`.
Documentos requeridos condicionales: si `requierePoder == true` → `poder.pdf`.

Plazo: `plazoDesdeCampo = fechaRadicacion`, `plazoTipoDias = habiles`, días según `tipoPeticion` (General=15, Documental=10, Consulta=30).

### 2) Respuesta — `respondida` (orden 2)
`disponibleSi`: `contestaron ∈ {SI, PARCIAL, NO}` (la etapa se ofrece sólo cuando ya se diligenció el campo de ficha `contestaron`).

Campo de ficha que ramifica:
- **contestaron** [select, soloFicha] — ¿Contestaron? [SI / PARCIAL / NO]

Reglas por valor:
- **SI** → campos req: `fechaRespuesta` · documento req: `respuesta.pdf`.
  - Muestra además: **fechaRespuesta** [fecha] (obligatorio), **numeroRespuesta** [texto] (opcional), **observacionesRespuesta** [textoLargo] (opcional).
- **PARCIAL** → campos req: `fechaRespuestaParcial`, `queFalto` · documento req: `respuesta.pdf` · documento opcional: `recurso.pdf`.
  - Muestra además: **fechaRespuestaParcial** [fecha] (obligatorio), **queFalto** [textoLargo] (obligatorio).
- **NO** → sin campos ni documentos requeridos.
  - Muestra: **observacionNoRespuesta** [textoLargo] (opcional, Observación del incumplimiento).

### 3a) Reiteración (respuesta parcial) — `reiteracion` (orden 3)
`disponibleSi`: `contestaron == PARCIAL`.
Acción: `crearDerivado` → tipo destino **Derecho de Petición** (un nuevo DdP).
- `copiarDatos`: entidad, correo, tipoPeticion, queSolicita, detalle, requierePoder.
- `copiarCliente`: sí. `copiarDocumentos`: poder.pdf.
Sin campos/documentos propios: es un salto que prellena un DdP nuevo.

### 3b) Escalar a acción de tutela — `escala_tutela` (orden 3)
`disponibleSi`: `contestaron ∈ {NO, PARCIAL}`.
Acción: `crearDerivado` → tipo destino **Acción de tutela**.
- `copiarCliente`: sí. `copiarDocumentos`: poder.pdf.
Sin `copiarDatos` (la tutela tiene su propio esquema).

### 4) Terminación — `terminada` (orden 4)
`terminal: true`. Resultado: "Petición terminada." Sin campos ni documentos.

## Desenlaces posibles

1. **Terminación normal** (`terminada`) — la entidad contestó (SÍ), o tras parcial/no se decidió cerrar. Único terminal real del flujo.
2. **Reiteración** (`reiteracion`, sólo PARCIAL) — escala creando un **nuevo DdP** prellenado (no cierra el caso; encadena otro proceso).
3. **Escalamiento a tutela** (`escala_tutela`, NO o PARCIAL) — crea una **Acción de tutela** derivada arrastrando cliente + poder. El seguimiento posterior (admisión, fallo, impugnación, segunda instancia) vive en el proceso de tutela, no aquí.

## Conformidad con el doc Juan David

### Coincidencias
- Campos de SOLICITAR del doc (entidad, correo, fecha de radicado, tipo con sus plazos 15/10/30 hábiles, "¿Qué desea solicitar?" con la lista completa, PDF de la petición, requiere poder→poder PDF, envío físico/correo, fecha de radicación del proceso, nro de radicado, vencimiento automático, "Contestaron SI/PARCIAL/NO") → todos modelados.
- Vencimiento automático según tipo → implementado con `plazoDiasPorValorDe` + días hábiles.
- "PARCIALMENTE → Reiteración del DdP (cargar PDF, fecha de radicación, contestaron SI/PARCIAL/NO)" → modelado como `reiteracion` (crearDerivado a nuevo DdP, que reabre el mismo ciclo).
- "RECURSO: cargar PDF" en parcial → `recurso.pdf` como documento **opcional** en `respondida` (PARCIAL).
- "Acción de tutela (enlace de tutela)" desde NO y desde PARCIAL → `escala_tutela` (crearDerivado a Acción de tutela), disponible en {NO, PARCIAL}.
- "Terminación de la petición" → etapa terminal `terminada`.

### Huecos (el doc pide y el seed NO modela)
1. **Bloque completo de tutela embebido**: el doc describe, colgando de NO/PARCIAL, todo el ciclo de tutela (Demanda/Pruebas/Anexos PDF, Radicado de la tutela, "Admitieron la tutela SI/NO", Auto admisorio PDF + fecha, Fallo favorable/desfavorable + sentencia PDF + fecha, Impugnación SI/NO, Fallo de 2ª instancia, Incidente de desacato Ley 393 con fecha/escrito/fallo). El seed NO lo modela aquí: sólo escala vía `crearDerivado` a "Acción de tutela" (ese seguimiento vive en el otro tipo). Es una decisión de diseño, pero queda como hueco respecto al doc.
2. **Variante "RECIBIR – Derecho de Petición"** (peticiones que llegan AL despacho, no que el despacho presenta): el doc trae campos propios (Radicado de ingreso, Fecha de recepción, Persona/entidad peticionaria, Dirección, "Contestación del DdP cargar PDF", "Fecha en que se contestó", envío correo/físico con su PDF). El seed NO tiene esta variante de recepción ni esos campos; sólo modela el DdP saliente.
3. **Variante "RECLAMACIÓN ADMINISTRATIVA"**: el doc la lista como un flujo aparte (estructura casi idéntica al DdP). El seed NO la modela como tipo/variante.
4. **Variante "CONSTITUCIÓN DE RENUENCIA (Ley 393)"**: el doc la lista como flujo propio (entidad, tipo sólo General 15 hábiles, "Anexar contestación", luego Acción de tutela con incidente de desacato). El seed NO la modela.
5. **Fecha de respuesta en NO**: el doc no pide fecha en NO; el seed coincide (sólo `observacionNoRespuesta` opcional). Sin hueco, anotado por completitud.
6. **`recurso.pdf` sin etapa propia**: el doc lista RECURSO como una rama de acción; el seed lo deja sólo como documento opcional en `respondida` (PARCIAL), sin etapa/derivado de recurso. Hueco menor de modelado de proceso.
7. **`fechaRadicado` vs `fechaRadicacion`**: el doc tiene "Fecha de radicado" (elaboración) y "Fecha de radicación proceso" (radicación). El seed los separa bien (`fechaRadicado` referencia vs `fechaRadicacion` desde la que corre el plazo). Sin hueco; coincidencia fiel.
