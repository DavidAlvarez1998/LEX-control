# spec (delta) — Etapa posicionada por la Rama vs. confirmada por el abogado

Delta sobre la capability **proceso-vencimientos**. Precisa la semántica cuando la
etapa la mueve la Rama (sync) en lugar del abogado, y cómo eso convive con el cálculo
de vencimientos y con los requisitos documentales (que NO se relajan). Se fusiona con
el contrato de vencimientos existente.

## ADDED Requirements

### Requirement: Distinción "posicionada por Rama" vs "confirmada por el abogado"

El avance de etapa tiene dos orígenes y DEBEN distinguirse en el historial
(`EtapaProceso`): `MANUAL` (el abogado movió la etapa con su gating documental intacto)
y `RAMA` (el sync la posicionó desde las actuaciones del juzgado). El origen DEBE quedar
registrado (hoy se codifica en `EtapaProceso.nota`, p. ej. "Posicionado automáticamente
desde la Rama"); NO se agrega columna/enum dedicado en esta versión.

El posicionamiento por Rama DEBE estar **desactivado por defecto** (`RAMA_AUTOPOSICION=off`):
con el kill-switch en `off`, el sync autollena campos pero NO mueve `etapaActual`.

#### Scenario: avance manual conserva su origen
- **Given** el abogado mueve la etapa con `moverEtapa`
- **When** se registra el cambio
- **Then** el `EtapaProceso` queda con origen `MANUAL`
- **And** el gating documental (`camposRequeridos` + `documentosRequeridos`) se exige
  como hasta ahora (sin cambios).

#### Scenario: kill-switch desactiva el posicionamiento por Rama
- **Given** `RAMA_AUTOPOSICION = off`
- **When** se sincroniza el proceso
- **Then** se autollenan las fechas vacías pero `etapaActual` NO se mueve.

### Requirement: La etapa posicionada por Rama NO relaja los requisitos

Cuando `RAMA_AUTOPOSICION=on` y el sync mueve `etapaActual` a la etapa de mayor `orden`
alcanzada (solo hacia adelante y si su `disponibleSi` se cumple), los
`camposRequeridos`/`documentosRequeridos` de esa etapa DEBEN seguir computándose como
**pendientes**. El posicionamiento por Rama refleja el estado del JUZGADO; NO confirma
que el despacho cargó los soportes. El `fechaLimite` DEBE recalcularse para la nueva
etapa según las reglas de vencimiento vigentes.

#### Scenario: posiciona pero deja documentos pendientes
- **Given** la última actuación mapea a la etapa `mandamientoPago`
- **And** esa etapa exige el documento del mandamiento
- **When** se sincroniza con `RAMA_AUTOPOSICION=on`
- **Then** `etapaActual` pasa a `mandamientoPago` con un `EtapaProceso` de origen `RAMA`
- **And** el documento del mandamiento sigue listado como **faltante**
- **And** `fechaLimite` se recalcula para `mandamientoPago`.

#### Scenario: nunca retrocede automáticamente
- **Given** `etapaActual` está en una etapa de mayor `orden` que la que mapearía una
  actuación
- **When** se sincroniza
- **Then** `etapaActual` NO DEBE retroceder (el retroceso es manual).

### Requirement: Consciencia en la ficha sin acción automática (autofill-only)

Con el flujo por defecto (autofill-only, sin posicionamiento), la ficha DEBE hacer
**visible** lo que el sync derivó, sin reintroducir un panel de "¿avanzar?" accionable:
(a) qué campos completó la Rama, (b) hasta qué etapa va el juzgado si está por delante
de la etapa del despacho, y (c) las fechas donde la Rama difiere de lo cargado por el
abogado (divergencia O2). La divergencia O2 DEBE ser **no bloqueante** y NUNCA sobrescribir
el valor del abogado.

#### Scenario: divergencia de fecha se muestra sin pisar
- **Given** `datos.fechaMandamiento = "2026-03-01"` (cargada por el abogado)
- **And** la actuación de mandamiento en la Rama tiene fecha `2026-03-15`
- **When** se abre/sincroniza la ficha
- **Then** se muestra un hint no bloqueante "la Rama dice 15 de marzo de 2026 · vos
  tenés 1 de marzo de 2026"
- **And** `datos.fechaMandamiento` NO cambia.
