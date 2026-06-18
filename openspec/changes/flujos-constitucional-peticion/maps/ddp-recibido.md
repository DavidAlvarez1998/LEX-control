# Derecho de Petición Recibido

Petición que el despacho (o su cliente) **RECIBE** de una persona o entidad y debe **responder** dentro del término legal (art. 23 C.P.; Ley 1755/2015). Aquí el cliente es el lado **receptor/obligado a responder**: el plazo corre **en contra** de quien recibe. Grupo `PETICION`, jurisdicción `CONSTITUCIONAL`, no judicial, cliente opcional.

---

## Fases de este caso

| Fase | Etapas (key) | Qué pasa |
|------|--------------|----------|
| **1. Recepción** | `recepcion` (orden 0) | Se registra la petición entrante y arranca el reloj del término (15/10/30 días háb. según tipo). |
| **2. Respuesta** | `contestacion` (orden 1) | Se documenta si se contestó SÍ / PARCIAL / NO y con qué soporte. |
| **3. Reiteración / Escalamiento** | `reiteracion` (orden 2), `escala_tutela` (orden 2) | Ramas excluyentes según el resultado: el peticionario reitera (nuevo DdP) o se recibe una tutela en contra. |
| **4. Cierre** | `terminada` (orden 3, terminal) | Petición atendida; fin del caso. |

> Nota de altitud: el seed solo define **4 órdenes** (0,1,2,3). No hay sub-flujo de tutela modelado dentro de este tipo: la tutela se materializa como un **proceso derivado** aparte (`crearDerivado` → "Acción de Tutela (Recibida)").

---

## Grafo del flujo

```
0) RECEPCIÓN                                            ⏱ desde fechaRecepcion · días HÁBILES
   campos: radicadoIngreso(auto)+fechaRecepcion+peticionario+tipoPeticion+queSolicita
   doc req: peticion-recibida.pdf
   plazo según tipoPeticion → General 15 · Documental 10 · Consulta 30
        │
        ▼
1) RESPUESTA   (disponible si contestada ∈ {SI, PARCIAL, NO})
   ¿La petición se contestó? [SI / PARCIAL / NO]
        ├ SI      → req: fechaContestacion + medioRespuesta + doc respuesta.pdf
        ├ PARCIAL → req: fechaContestacion + medioRespuesta + doc respuesta.pdf
        │            (opc: recurso.pdf)
        └ NO      → (sin campos/docs adicionales requeridos)
        │
        ▼
2) RAMAS (mismo orden = decisión excluyente)
   ├ REITERACIÓN DEL PETICIONARIO   (si contestada = PARCIAL)
   │     accion: crearDerivado → "Derecho de Petición Recibido"  (nuevo DdP prellenado)
   │
   └ TUTELA EN CONTRA (defensiva)   (si contestada ∈ {NO, PARCIAL})
         accion: crearDerivado → "Acción de Tutela (Recibida)"   ⇒ ESCALAMIENTO
        │
        ▼
3) TERMINACIÓN  (terminal) → "Petición recibida atendida."   └ FIN
```

Docs opcionales de la etapa de respuesta según el medio:
`medioRespuesta = Correo electrónico` → `acuse-correo.pdf` · `medioRespuesta = Físico` → `constancia-envio.pdf`.

---

## Detalle por etapa (campo por campo)

### 0) Recepción `recepcion` (orden 0)
Campos requeridos: `radicadoIngreso` [texto, **auto**], `fechaRecepcion` [fecha], `peticionario` [texto], `tipoPeticion` [select], `queSolicita` [multiselect].
Campos opcionales del formulario: `correo` [listaCorreos], `direccion` [texto], `detalle` [textoLargo], `otroSolicita` [textoLargo — solo si `queSolicita` incluye "Otro", y entonces es requerido].
Documento requerido: **`peticion-recibida.pdf`** (el escrito de la petición entrante).

- **¿Tipo de derecho de petición?** [General / Documental / Consulta] → fija el plazo del término:
  - General → ⏱ **15 días hábiles**
  - Documental → ⏱ **10 días hábiles**
  - Consulta → ⏱ **30 días hábiles**
  - Plazo calculado desde `fechaRecepcion`, `plazoTipoDias = habiles`, vía `plazoDiasPorValorDe`.
- **¿Qué están solicitando?** [multiselect: Información / Copia de documentos / Certificación / Historia laboral / Historia clínica / Estado de trámite / Pago pendiente / Reconocimiento de derecho / Corrección de información / Habeas data / Solicitud laboral / Salud / Seguridad social / Queja / Reclamo / Consulta / Otro]
  - "Otro" → muestra y exige `otroSolicita` [textoLargo].

### 1) Respuesta `contestacion` (orden 1)
Disponible si `contestada ∈ {SI, PARCIAL, NO}` (es decir, una vez se marca el campo de ficha `contestada`).
Campo de control (soloFicha): `contestada` [select SI / PARCIAL / NO].

- **¿La petición se contestó?** [SI / PARCIAL / NO]
  - **SI** → requiere `fechaContestacion` [fecha] + `medioRespuesta` [select] + documento **`respuesta.pdf`**.
  - **PARCIAL** → requiere `fechaContestacion` + `medioRespuesta` + **`respuesta.pdf`**; documento opcional **`recurso.pdf`**.
  - **NO** → no agrega campos ni documentos requeridos (habilita la rama de tutela).
- **¿Medio de envío de la respuesta?** [Físico / Correo electrónico] (visible solo si contestada ∈ {SI, PARCIAL})
  - Correo electrónico → documento opcional `acuse-correo.pdf`.
  - Físico → documento opcional `constancia-envio.pdf`.
- Campos de ficha adicionales visibles con SI/PARCIAL: `radicadoRespuesta` [texto, opcional], `observacionContestacion` [textoLargo, soloFicha, opcional].

### 2a) Reiteración del peticionario `reiteracion` (orden 2)
Disponible si `contestada = PARCIAL`.
Acción `crearDerivado` → nuevo proceso del **mismo tipo** "Derecho de Petición Recibido", `copiarCliente: true`, copiando: `peticionario, correo, direccion, tipoPeticion, queSolicita, otroSolicita, detalle`.
(No tiene campos propios; abre un DdP nuevo prellenado encadenado al caso.)

### 2b) Tutela en contra (defensiva) `escala_tutela` (orden 2)
Disponible si `contestada ∈ {NO, PARCIAL}`.
Acción `crearDerivado` → "**Acción de Tutela (Recibida)**", `copiarCliente: true`. **Escalamiento**: el sub-flujo de tutela (demanda/pruebas/anexos, admisión, fallo, impugnación, 2ª instancia, desacato) vive en ese otro tipo, no aquí.

### 3) Terminación `terminada` (orden 3, terminal)
Sin campos. `resultado`: "Petición recibida atendida." Cierra el caso.

---

## Desenlaces posibles

1. **Terminación (atendida)** — `terminada`, terminal. Camino normal cuando la petición se contesta (típicamente `contestada = SI` → Terminación).
2. **Reiteración** — `contestada = PARCIAL` → se genera un **nuevo DdP Recibido** derivado y prellenado (el caso continúa en la cadena, no cierra aquí).
3. **Escalamiento a tutela** — `contestada ∈ {NO, PARCIAL}` → se crea una **Acción de Tutela (Recibida)** derivada. Es la salida adversarial.

> No existe un terminal explícito de "archivo/desistimiento" ni un terminal propio para las ramas reiteración/tutela: ambas son acciones de derivación; el cierre formal de este proceso siempre es `terminada`.

---

## Conformidad con el doc Juan David

Sección fuente: **"RECIBIR – DERECHO DE PETICIÓN"** (líneas 63-128).

### Coincidencias
- **Recepción**: Radicado de ingreso (alfanumérico) ↔ `radicadoIngreso` (auto); Fecha de recepción ↔ `fechaRecepcion`; Persona/entidad que realiza la petición ↔ `peticionario`; Correo ↔ `correo`; Dirección ↔ `direccion`; Tipo (General/Documental/Consulta con 15/10/30 días hábiles) ↔ `tipoPeticion` + plazos; "¿Qué están solicitando?" (las 17 casillas) ↔ `queSolicita` con "Otro" → casilla en blanco (`otroSolicita`).
- **Fecha de vencimiento automática** ↔ motor `plazoDiasPorValorDe` (días hábiles desde fechaRecepcion).
- **PDF del documento** ↔ `peticion-recibida.pdf`.
- **Contestación**: "¿La petición se contestó? SI/PARCIAL/NO" ↔ `contestada`; "Fecha en que se contestó" ↔ `fechaContestacion`; "Envío correo/físico → cargar PDF" ↔ `medioRespuesta` + docs opcionales `acuse-correo.pdf`/`constancia-envio.pdf`; "Contestación cargar PDF" ↔ `respuesta.pdf`.
- **PARCIALMENTE → Reiteración (cargar PDF)** ↔ `reiteracion` (derivado a nuevo DdP) + doc opcional `recurso.pdf`.
- **NO / PARCIAL → Acción de tutela (enlace de tutela)** ↔ `escala_tutela` (derivado a "Acción de Tutela (Recibida)").
- **Terminación de la petición** ↔ `terminada` (terminal).

### Huecos (el doc pide y el seed NO modela)
- **"Radicado" de la respuesta como dato de seguimiento**: el doc (línea 80 "Radicado") aparece tras cargar la contestación; el seed sí tiene `radicadoRespuesta` pero es **opcional y soloFicha** — no lo exige al marcar SI/PARCIAL (el doc lo presenta como dato del envío).
- **Sub-flujo de tutela in situ no existe**: el doc despliega bajo NO/PARCIAL un flujo completo de tutela (Demanda/Pruebas/Anexos PDF, Radicado de tutela numérico, "ADMITIERON LA TUTELA SI/NO", Auto admisorio PDF, FALLO favorable/desfavorable + sentencia PDF, IMPUGNACIÓN SI/NO, FALLO DE SEGUNDA INSTANCIA). En el seed **nada de esto** está dentro de "Derecho de Petición Recibido"; se delega vía `crearDerivado` al tipo "Acción de Tutela (Recibida)". Funcionalmente cubierto por derivación, pero el seguimiento NO ocurre dentro de este proceso.
- **Reiteración con sub-resultado anidado**: el doc dice que tras la reiteración se vuelve a preguntar "Contestaron: SI – PARCIAL – NO" y de ahí "RECURSO / Acción de tutela". El seed lo resuelve creando **otro DdP Recibido** (que reproduce sus propias etapas), no como sub-campos anidados — equivalente, pero la cadena es por procesos derivados, no por niveles dentro del mismo proceso.
- **"Requiere poder SI/NO → cargar PDF PODER"**: aparece en las variantes de SOLICITAR/Reclamación/Renuencia, **no** en la sección RECIBIR, y el seed (correctamente) **no** incluye campo de poder aquí. Coherente: quien recibe no actúa por poder.
- **RECURSO como documento del lado receptor**: el seed solo ofrece `recurso.pdf` como opcional bajo PARCIAL; el doc lo lista como acción posterior a la reiteración. Cubierto parcialmente.
- **No hay terminal de "archivo/no respondida vencida"**: el motor calcula vencimiento pero no existe etapa/resultado de petición vencida sin respuesta; el único cierre es `terminada` ("atendida").
