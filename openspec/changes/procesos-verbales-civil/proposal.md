# procesos-verbales-civil

## Por qué

Los dos procesos declarativos de **jurisdicción ordinaria civil** —**Proceso (declarativo)
verbal** y **Proceso verbal sumario**— existen en el catálogo (`prisma/seed-tipos.json`) pero
están como **esqueleto**: tienen algunos campos sustantivos, pero **sin documentos anclados,
sin ramas de calificación, sin recursos/2ª instancia y con plazos sin tipo de día**. No
reflejan el trámite real del **Código General del Proceso (CGP, Ley 1564/2012)**.

El usuario pidió **dejarlos "full"** (flujo completo, fiel al CGP, con los campos a usar y el
grafo) **antes de pasar a la implementación**, usando el mismo modelo maduro que ya validamos
en el Proceso Laboral (un solo `TipoProceso` → ramas por opción vía `disponibleSi`/`mostrarSi`,
fases, plazos hábiles, documentos anclados, terminales diferenciados).

> Nota de fuente: **no hay un .docx específico** para estos dos (a diferencia del laboral). La
> fuente de verdad es el **CGP** (arts. 368–373 para el verbal; 390–392 para el sumario) +
> el esquema ya sembrado + el patrón del laboral. Donde el CGP calle el tipo de día, se
> **pregunta** (ver [[plazos-dias-habiles-creele-al-doc]]).

## Qué cambia

**Esto es solo el PLAN** (proposal + design + tasks). **No se implementa nada** todavía (la API
está en reestructuración). Cuando se aplique, será reescribir las dos entradas del seed
(`Proceso verbal` y `Proceso verbal sumario`) con:

### 1. Proceso verbal — CGP 368–373
- **Doble instancia** (apelable), **2 audiencias** (inicial art. 372 + instrucción y
  juzgamiento art. 373).
- Ramifica por **rol** (Demandante/Demandado) y por decisiones (calificación, contestación con
  reconvención/excepciones, apelación → 2ª instancia). Traslado **20 días hábiles**.

### 2. Proceso verbal sumario — CGP 390–392
- **Única instancia** (NO apelable), **1 sola audiencia** (art. 392). Traslado **10 días
  hábiles**. Sin reforma, reconvención, excepciones previas, incidentes, acumulación, suspensión
  de común acuerdo ni terceros (art. 392). **La sentencia queda EN FIRME** — NO procede
  apelación NI reposición contra el fallo (CGP art. 318).

### 3. En ambos
- **Documentos anclados** (demanda/pruebas/anexos/poder/auto/notificación/sentencia…) — hoy no
  hay ninguno.
- **Calificación con ramas** (admite / inadmite→subsanar 5 días / rechaza→recurso).
- **Plazos con `plazoTipoDias`** (CGP art. 118 = días hábiles salvo norma especial).
- **Terminales diferenciados**: conciliación, archivo (rechazo/retiro), sentencia en firme,
  (verbal) 2ª instancia.

## Impacto

- **Solo documentación** en este change. La implementación futura toca **solo el seed**
  (`prisma/seed-tipos.json`, dos tipos) + re-seed (`pnpm seed:catalogo`). El **motor no cambia**
  (ya soporta `{todas}`/`{alguna}`, fases, plazos, terminales). El **cliente no cambia** (la
  ficha genérica los renderiza; el stepper por fases ya es genérico para judiciales).
- **Reusa** la infraestructura del laboral (mismo patrón de etapas/ramas/2ª instancia).

## Alcance — nos limitamos a lo que dicta el CGP (decisión del usuario)

NO se agregan enriquecimientos fuera del flujo que el CGP impone. **Excluidos** (quedan fuera
de este diseño): desistimiento expreso/tácito, casación, sentencia anticipada como rama,
conciliación-como-requisito que gatee, y terminales diferenciados por resultado. Se modela el
**trámite tal como dicta el código**:
- **Plazos** (CGP art. 118 = días hábiles): traslado 20 (verbal) / 10 (sumario), subsanación 5,
  apelación 3.
- **2ª instancia del verbal**: completa (remisión→sustentación→audiencia→sentencia 2ª), porque
  el verbal **es de doble instancia** por definición (CGP).
- **Verbal sumario**: única instancia → **sentencia en firme, sin recurso** contra el fallo.
- **`rol` (Demandante/Demandado)** y **`cuantiaTipo`**: se modelan (son parte real del trámite);
  la calificación es solo del demandante.
