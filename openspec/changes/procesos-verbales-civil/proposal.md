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
(`Proceso declarativo verbal` y `Proceso verbal sumario`) con:

### 1. Proceso (declarativo) verbal — CGP 368–373
- **Doble instancia** (apelable), **2 audiencias** (inicial art. 372 + instrucción y
  juzgamiento art. 373).
- Ramifica por **rol** (Demandante/Demandado) y por decisiones (calificación, contestación con
  reconvención/excepciones, apelación → 2ª instancia). Traslado **20 días hábiles**.

### 2. Proceso verbal sumario — CGP 390–392
- **Única instancia** (NO apelable), **1 sola audiencia** (art. 392). Traslado **10 días
  hábiles**. Sin reconvención, sin excepciones previas separadas, sin intervención de terceros.
  Recurso = **reposición**.

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

## Alcance / decisiones a confirmar
1. **Modelar `rol` (Demandante/Demandado)** en el verbal como en el laboral (la calificación es
   solo del demandante; el demandado recibe). ¿OK, o lo dejamos solo demandante por ahora?
2. **Cuantía**: verbal = mayor/menor (ambas doble instancia); sumario = mínima + asuntos del
   art. 390. ¿Capturamos `cuantiaTipo` o basta el monto?
3. **Plazos**: traslado 20 (verbal) / 10 (sumario) días hábiles; subsanación 5; apelación 3.
   ¿Confirmas hábiles (CGP 118)?
4. **2ª instancia del verbal**: ¿la modelamos completa (remisión→sustentación→audiencia→
   sentencia 2ª) como en el laboral, o la dejamos como un único resultado?
