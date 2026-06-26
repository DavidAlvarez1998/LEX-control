# spec (delta) — Autollenado y posicionamiento de etapa desde actuaciones

Delta sobre la capability **rama-judicial**. Define cómo las actuaciones sincronizadas
alimentan la ficha: mapeo data-driven, autollenado de campos y posicionamiento de
etapa SIN gating documental. Se fusiona con el contrato de consulta existente.

## ADDED Requirements

### Requirement: Mapeo actuación→etapa declarado por tipo (`mapeoActuaciones`)

Cada `TipoProceso` PUEDE declarar `mapeoActuaciones`: una lista ordenada de reglas que
asocian texto de actuación a una etapa y a campos a pre-llenar. El motor de hitos DEBE
leer este mapeo del esquema del tipo (no de constantes en código). Si el tipo no
declara `mapeoActuaciones`, el motor NO DEBE autollenar ni posicionar (salvo el
fallback legacy del ejecutivo durante una versión de transición).

Una regla tiene: `etapaKey` (obligatorio), `actuacion` (kw[]), `anotacion` (kw[]),
`excluir` (kw[]), `fechaCampo`, `valorCampo`, `valor` (todos opcionales).

#### Scenario: regla coincide por título o anotación
- **Given** una actuación con `actuacion="Auto decreta medidas cautelares"`
- **And** una regla `{ etapaKey: "notifCautelares", actuacion: ["CAUTELAR","EMBARGO"], fechaCampo: "fechaCautelares" }`
- **When** el motor evalúa la actuación
- **Then** la regla coincide (normalizando tildes/mayúsculas por subcadena)
- **And** propone `etapaKey="notifCautelares"` y pre-llenar `fechaCautelares` con `fechaActuacion`.

#### Scenario: la negación (`excluir`) evita el falso positivo
- **Given** una actuación `actuacion="Auto de sustanciación"`, `anotacion="NIEGA TERMINACION POR PAGO"`
- **And** una regla `{ etapaKey: "terminacion", actuacion: ["TERMINA"], anotacion: ["PAGO"], excluir: ["NIEGA","TRASLADO","SOLICITUD"] }`
- **When** el motor evalúa la actuación
- **Then** la regla NO DEBE coincidir (hay un `excluir` presente en el texto)
- **And** el proceso NO se marca como terminado.

#### Scenario: no re-sugiere lo ya diligenciado
- **Given** una regla con `fechaCampo="fechaMandamiento"`
- **And** `datos.fechaMandamiento` ya tiene valor
- **When** el motor evalúa
- **Then** NO DEBE proponer pre-llenar ese campo (guard "existe y está vacío").

### Requirement: Autollenado de campos derivados en cada sync

`sincronizarProceso` DEBE, tras insertar las actuaciones nuevas, derivar TODOS los
campos (fechas y decisiones) que las reglas resuelvan y fijarlos con la semántica
existente "solo si está vacío" (`fijar()`). NUNCA DEBE sobrescribir un valor cargado
por el abogado.

#### Scenario: sync autollena varias fechas a la vez
- **Given** un radicado con autos de mandamiento, cautelares y liquidación del crédito
- **When** se sincroniza el proceso
- **Then** `fechaMandamiento`, `fechaCautelares` y la fecha de liquidación quedan
  pre-llenadas (las que estaban vacías), en una sola escritura.

### Requirement: Posicionamiento de etapa por Rama (OPT-IN, desactivado por defecto)

El posicionamiento automático de etapa DEBE estar **desactivado por defecto**
(`RAMA_AUTOPOSICION=off`): las actuaciones reflejan el estado del JUZGADO, no el flujo
documental del despacho, y mover/cerrar la etapa por la Rama saltaría etapas
intermedias (docs sin cargar) y cerraría procesos con documentos faltantes. El estado
del juzgado se muestra de forma informativa (timeline + panel de estado), desacoplado
de la etapa del despacho, que el abogado avanza manualmente.

Cuando se habilita explícitamente (`RAMA_AUTOPOSICION=on`), el sync mueve `etapaActual`
a la etapa de mayor `orden` alcanzada, solo hacia adelante y si su `disponibleSi` se
cumple, SIN exigir `camposRequeridos` ni `documentosRequeridos` (los requisitos siguen
computándose como pendientes). El avance manual (`moverEtapa`) DEBE conservar su gating
documental intacto en todos los casos.

#### Scenario: posiciona pero deja documentos pendientes
- **Given** un proceso cuya última actuación es "Auto libra mandamiento ejecutivo"
- **And** la etapa `mandamientoPago` exige el documento del mandamiento
- **When** se sincroniza
- **Then** `etapaActual` pasa a `mandamientoPago`
- **And** el documento del mandamiento sigue listado como **faltante**
- **And** se registra un `EtapaHistorial` con `origen = "RAMA"`.

#### Scenario: nunca retrocede automáticamente
- **Given** `etapaActual = "terminacion"`
- **And** llega/re-evalúa una actuación que mapea a una etapa anterior
- **When** se sincroniza
- **Then** `etapaActual` NO DEBE retroceder por el sync (el retroceso es manual).

#### Scenario: kill-switch desactiva el posicionamiento
- **Given** `RAMA_AUTOPOSICION = off`
- **When** se sincroniza
- **Then** se autollenan campos pero `etapaActual` NO se mueve.
