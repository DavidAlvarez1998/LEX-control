# procesos-laborales

## Por qué

El portal cliente agrupa los asuntos en tres secciones según `TipoProceso.grupo`:
**Procesos** (JUDICIAL), **Peticiones** (PETICION) y **Acciones Constitucionales**
(CONSTITUCIONAL). El despacho necesita una **cuarta sección dedicada, "Procesos
Laborales"**, debajo de Acciones Constitucionales, que modele el **procedimiento
laboral ordinario** colombiano (Ley 2452 de 2025; Código Procesal del Trabajo y de la
Seguridad Social / CST) con su flujo real de etapas, plazos en días hábiles y documentos.

Hoy el catálogo solo tiene stubs laborales superficiales (p. ej. "Proceso ordinario
laboral de primera instancia", 5 etapas planas sin ramas ni plazos derivados). El
documento de requerimientos `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO
15 DE JUNIO.docx` (fuente de verdad legal) describe un flujo mucho más rico: arranca con
dos elecciones — **rol** (Demandante / Demandado) y **tipo de instancia** (Única / Doble)
— que ramifican toda la tramitación (admisión con subsanación/rechazo, traslado y
contestación, reforma y reconvención, audiencias art. 77 y 80, sentencia y recursos).

## Qué cambia

### 1. Modelado: UN solo "Proceso Laboral" con dos selects que ramifican (data-driven)
En vez de cuatro tipos casi idénticos, el catálogo gana **un único `TipoProceso`
"Proceso Laboral"** cuyo formulario abre con dos campos `select` obligatorios — `rol`
(Demandante/Demandado) y `tipoInstancia` (Única instancia/Doble instancia) — que dirigen
el resto del flujo. Es lo más fiel al documento ("ELIJE: DEMANDANTE/DEMANDADO" →
"ÚNICA/DOBLE INSTANCIA") y evita duplicar el 80 % del flujo en cuatro definiciones.

**Sin cambios en el motor.** El evaluador de condiciones (`esquema.ts`) es solo de
igualdad (sin AND/OR). El árbol se diseñó para que **ningún gate necesite rol y instancia
a la vez**: las **etapas** se ramifican por `tipoInstancia` (`disponibleSi`, una sola
condición) y los **campos** por `rol`/decisiones puntuales (`mostrarSi`, una sola
condición). Reconvención/reforma/contestación-detalle y la doble audiencia (art. 77 +
art. 80) viven solo en **Doble instancia**; la audiencia única y el recurso de reposición
solo en **Única instancia**. Todo cabe en `seed-tipos.json` + `reglas`/`requeridosSi`/
`opcionalesSi`/`plazoDesdeCampo`, igual que el Derecho de Petición.

### 2. Taxonomía: nuevo grupo `LABORAL` + su propia sección y ruta
- **Schema**: agregar `LABORAL` al enum `GrupoProceso` (`schema.prisma`). El nuevo
  "Proceso Laboral" se siembra con `grupo = "LABORAL"`, `jurisdiccion =
  "ORDINARIA_LABORAL"`, `esJudicial = true`.
- **Frontend cliente**: `SECCION_RUTA["LABORAL"] = "/procesos-laborales"` en
  `lib/procesos.ts`; nuevo ítem de nav "Procesos Laborales" **debajo de "Acciones
  Constitucionales"** (`roles: ["JURIDICO"]`); nueva ruta `(dashboard)/procesos-laborales/`
  (`page` lista + `nuevo` con tipo bloqueado, estilo `/peticiones?tipo=ID` + `[id]` ficha).
- El wizard genérico `/procesos/nuevo` (que agrupa los judiciales por jurisdicción) deja
  de ofrecer los tipos `LABORAL` (filtra `esJudicial && grupo === "JUDICIAL"`); los
  laborales se crean desde su propia sección.

### 3. Reglas de plazo en días hábiles (reusa el motor existente)
- Contestación: **10 días hábiles** desde la fecha de notificación del traslado.
- Subsanación tras inadmisión: **5 días hábiles** desde la fecha de inadmisión.
- Recurso de reposición/apelación por escrito: **3 días calendario** (el documento no los
  califica como hábiles; decisión del usuario: calendario).
Reusa `diasHabiles.ts` (festivos CO Emiliani+Meeus) y `derivarFechaLimite` vía
`plazoDesdeCampo`/`plazoTipoDias` (`"habiles"` para 10 y 5; `"calendario"` para 3), sin código nuevo.

## Impacto
- **Schema**: 1 valor de enum nuevo (`GrupoProceso.LABORAL`). Sin tablas ni columnas
  nuevas. Se aplica con `pnpm push` (la BD no usa migrate). Reusa `Proceso`/`TipoProceso`/
  `EtapaProceso`/`DocumentoProceso`/`datos` (Json).
- **Catálogo (`seed-tipos.json`)**: +1 tipo "Proceso Laboral" (rico, ramificado). El stub
  "Proceso ordinario laboral de primera instancia" queda **superado** (se elimina o se
  marca; ver design).
- **Backend**: sin endpoints nuevos. Reusa los routers de procesos/etapas/documentos.
- **Frontend cliente**: +1 sección/ruta `/procesos-laborales` (lista + nuevo + ficha),
  +1 ítem de nav, +1 entrada en `SECCION_RUTA`; el wizard `/procesos/nuevo` excluye LABORAL.
- **Motor de esquema/condiciones**: **sin cambios** (el diseño evita la necesidad de AND).

## Fuera de alcance (v1)
- Plantillas de documento laborales (generación de demanda/contestación) — el flujo
  gestiona/adjunta PDFs; la generación desde plantilla se deja para un change aparte.
- Liquidación automática de pretensiones/cuantía (cálculos) — se capturan como datos.
- Procesos laborales especiales (ejecutivo, fuero sindical, pensión de invalidez) — sus
  stubs actuales se mantienen tal cual; este change cubre el **ordinario** del documento.
- Recordatorios/notificaciones automáticas de vencimientos (ya existe `proceso-vencimientos`).

## Decisiones del usuario (2026-06-16)
- **Modelado = Opción 1**: un solo "Proceso Laboral" con selects `rol` + `tipoInstancia`
  que ramifican (vs. 2 tipos por instancia o 4 tipos). Confirmado.
- **Alcance = diseño primero**: este change entrega proposal + design + spec + tasks para
  revisión; la implementación (seed + frontend) va en el paso siguiente con su OK.
