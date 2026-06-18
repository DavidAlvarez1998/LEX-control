# laboral-doble-instancia

## Por qué

El flujo del **Proceso Laboral · DEMANDANTE · DOBLE INSTANCIA** (Ley 2452/2025, CPTSS) ya
existe (change aplicado `laboral-flujo-doc`, ver [[laboral-flujo-doc]]), pero al trazarlo
contra el doc fuente `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`
con el usuario (abogado, rol JURIDICO) aparecieron **tres correcciones** y **un vacío
procesal de fondo**:

1. **Rechazo tras subsanar archiva de una, sin recurso.** Hoy `decisionTrasSubsanacion =
   RECHAZAR` cierra el proceso directo. El doc repite el bloque de rechazo dos veces (rechazo
   directo del auto **y** rechazo después de subsanar) y **ambos llevan recurso**
   (reposición/apelación → favorable sigue / desfavorable archiva). El auto que rechaza la
   demanda pone fin al proceso y **es recurrible** — archivarlo sin recurso es un error
   procesal.

2. **No se captura el auto admisorio tras la subsanación.** El doc pide, cuando el juez
   admite tras subsanar, **fecha del auto de admisión + auto PDF**; hoy solo se guarda la
   fecha en que se subsanó y el escrito.

3. **Orden Preparación↔Citación invertido en doble instancia.** El doc, en doble, ordena
   *Contestación → Preparación de audiencia → Citación → art. 77 → art. 80*. Hoy el sistema
   pone Citación **antes** de Preparación (correcto solo para única instancia).

4. **La "doble instancia" se queda en primera instancia.** El flujo termina la apelación en
   un único campo `decisionApelacion: FAVORABLE/DESFAVORABLE`. Pero el sentido de un proceso
   *de doble instancia* es que, **concedida** la apelación, hay una **segunda instancia real**
   ante el Tribunal Superior (Sala Laboral): remisión → sustentación → audiencia → sentencia
   de 2ª instancia (confirma/revoca/modifica). Hoy ese tramo entero está colapsado.

El doc se **detiene a propósito** en "decisión apelación" (no desarrolla 2ª instancia,
consulta ni casación). El usuario decidió **extender solo a la segunda instancia real**
(no consulta art. 69 ni casación, por ahora). Aclaración legal confirmada con el usuario:
única vs doble **no es progresión** — son rieles excluyentes fijados por la **cuantía** al
radicar; no se pasa de una a otra.

## Modelo / arquitectura — un formulario, 4 caminos, sub-ramas por decisión

El "Proceso Laboral" es **un único `TipoProceso`** (un solo `esquemaFormulario` y una sola
lista de etapas), no cuatro tipos distintos. La aparente complejidad se resuelve por capas:

```
                 UN SOLO "Proceso Laboral"   (1 TipoProceso · 1 esquema · 1 formulario)
                                │
       ┌───────────── se elige al crear ─────────────┐
       │  eje A: ROL (Demandante / Demandado)         │
       │  eje B: INSTANCIA (Única / Doble)            │
       └───────────────────────┬─────────────────────┘
                                ▼
            4 CAMINOS  (las 4 combinaciones rol × instancia)
   Demte·Única · Demte·Doble · Demdo·Única · Demdo·Doble
                                │
        y CADA camino se vuelve a ramificar según las respuestas:
        decisionAuto (ADMISIÓN/INADMISIÓN→subsanar/RECHAZO→recurso) ·
        ¿retiro? · ¿contestaron? · ¿reconvención?→admitir/inadmitir/rechazar ·
        ¿apela?→¿el juez concede?→segunda instancia
```

- **Los 4 caminos no son tipos separados:** se seleccionan al crear con `rol` +
  `tipoInstancia`, y el motor enciende/apaga **etapas** con `disponibleSi` y **campos** con
  `mostrarSi`, usando condiciones compuestas `{todas}` (AND) / `{alguna}` (OR).
- **Los sub-caminos** son el mismo mecanismo, condicionado a lo que se va respondiendo
  (`decisionAuto`, `decisionTrasSubsanacion`, `hayReconvencion`, `concedeApelacion`, …): cada
  respuesta abre o cierra ramas.
- **Consecuencia:** el usuario nunca ve todo a la vez — el formulario es uno, pero solo muestra
  lo que aplica a *su* combinación rol×instancia y a las decisiones tomadas hasta ese punto.
- **Las fases** (ver `fases.md`) son la capa de presentación que agrupa las etapas para lectura
  y navegación (stepper); cada camino "enciende" solo las fases que le aplican (p. ej. los
  única no tienen Fase 5 · Segunda instancia). El motor ignora la etiqueta `fase`.

Este diseño es coherente con el módulo de trámites legales (metadata-driven, ver
[[tramites-legal-module-design]]): catálogo + formularios dinámicos + workflow por etapas con
ramas. El motor (`esquema.ts`) **ya** soporta todo lo anterior; este change solo ajusta datos
del seed y el render del cliente.

## Qué cambia

### 1. Recurso tras subsanar (corrección 1)
El rechazo tras la subsanación pasa por el **mismo** recurso que el rechazo directo
(reposición/apelación, 3 días) → FAVORABLE continúa el proceso / DESFAVORABLE (o sin recurso)
archiva. Se **reutilizan** los campos de recurso existentes (`recursoRechazo`,
`fechaRecursoRechazo`, `decisionRecursoRechazo`, `observacionesRecursoRechazo`): un proceso es
rechazo-directo **XOR** rechazo-tras-subsanar, nunca ambos.

### 2. Auto admisorio tras subsanar (corrección 2)
Nuevos campos `fechaAdmisionTrasSubsanacion` (fecha) + documento
`auto-admision-tras-subsanacion.pdf`, requeridos cuando `decisionTrasSubsanacion = ADMITIR`.

### 3. Orden Preparación → Citación en doble (corrección 3)
Se separan las etapas `preparacionAudiencia`/`citacionAudiencia` por instancia: la variante
de **única** mantiene Citación(antes)→Preparación; se agregan variantes de **doble**
(`preparacionAudiencia_doble`, `citacionAudiencia_doble`) con el orden invertido. Cliente
`datos-proceso.tsx`: títulos de sección instance-aware (mismo patrón que ya usan
`audienciaArt77`/`audienciaArt80`).

### 4. Apelación en dos pasos (preludio de la 2ª instancia)
La apelación deja de ser un único resultado: **¿se interpone?** → forma (audiencia/escrito 3
días) → **¿el juez la concede?**. Si la niega o no se interpone → Terminación (1ª inst. en
firme). Si la concede → **Segunda instancia**.

### 5. 🆕 Segunda instancia real (Tribunal Superior — Sala Laboral)
Cuatro etapas nuevas, solo alcanzables si la apelación fue concedida:
- **S1 Remisión al Tribunal** — fecha de remisión/reparto + N.º radicado 2ª instancia.
- **S2 Sustentación del recurso** — fecha + `escrito-sustentacion.pdf` + `auto-2inst.pdf`.
- **S3 Audiencia de 2ª instancia** — fecha + `acta-2inst.pdf` (opc) + alegatos.
- **S4 Sentencia de 2ª instancia** — fecha + `sentencia-2inst.pdf` + decisión
  `CONFIRMA / REVOCA / MODIFICA` → Terminación (ejecutoriada).

### 6. Consistencia entre los 4 flujos (rol × instancia)
Las correcciones se aplican de forma coherente a los 4 casos (Demandante/Demandado ×
Única/Doble). Mapas completos en `flujos-4-casos.md`. Ajustes de consistencia: la
**calificación con decisión** (subsanación/recurso de rechazo) queda **solo para demandante**;
el **demandado·doble** registra la admisión sin decisión; la **2ª instancia** aplica a
**ambos doble**; el orden Preparación↔Citación se respeta por instancia en ambos roles.

### 7. Fases (esqueleto de alto nivel + base del panel visual)
El flujo se organiza en **6 fases** (Demanda y admisión · Traslado y contestación ·
Audiencias · Sentencia y recurso · Segunda instancia · Terminación/archivo). Ver `fases.md`.
Las fases agrupan etapas sin cambiar la lógica; sirven al documento (contexto "perfecto") y,
opcionalmente, al stepper agrupado del panel (`fase` en el esquema de etapas).

### 8. Renumeración del `orden` (interno, sin cambio visible)
El motor (`siguienteEtapaAuto`) camina por niveles de `orden` estrictamente mayores al actual.
Hoy `subsanacion` y `recurso_rechazo` comparten `orden = 2`, así que el recurso **no es
alcanzable desde la subsanación**. Se renumera: `subsanacion = 2`, `recurso_rechazo = 3`, y el
resto se desplaza; las etapas de 2ª instancia van al final (después de `recurso`/apelación).

### 9. UX / visual (detalle en `ux-visual.md`)
Este change **modifica el formulario ya existente** y sus fases (no crea uno nuevo). Lo visual
**reutiliza** el change [[transiciones-suaves]]: View Transitions para la ruta (morph del
título lista→ficha vía `vtName`) y el keyframe `.lex-campo-reveal` para la aparición suave de
los campos condicionales. Propio del laboral: (a) cuando una opción **abre otro camino**, sus
campos se envuelven en un **bloque de rama** (`.lex-rama`: acento lateral + sangría por nivel +
chip *"Porque elegiste «X»"*) que entra animado, dejando claro que dependen de esa decisión; y
(b) **orden canónico** de los campos por etapa: pregunta/decisión → **fecha → documento(s)** →
sub-decisión/observaciones (fecha siempre antes que el PDF).

## Impacto

- **Alcance:** solo el `TipoProceso` "Proceso Laboral" (seed `prisma/seed-tipos.json`,
  `tipo[20]`). El motor **no cambia** (ya soporta `{todas}`/`{alguna}` y niveles de `orden`);
  solo cambian datos del seed + render del cliente.
- **Specs:** `tramite-catalog` (campos/etapas nuevos: recurso reusado, auto tras subsanar,
  variantes prep/citación por instancia, apelación en 2 pasos, 4 etapas de 2ª instancia) y
  `tramite-management` (gating/ramas: recurso tras subsanar, orden por instancia, segunda
  instancia condicionada a apelación concedida).
- **Cliente:** `lib/procesos.ts` (sin cambios de motor), `components/datos-proceso.tsx`
  (`TITULO_SECCION_LABORAL` + `tituloEtapa`/`tituloCampo` instance-aware para prep/citación y
  secciones de 2ª instancia), `procesos-laborales/[id]/page.tsx` (consume el esquema; sin
  lógica nueva).
- **Compatibilidad:** procesos laborales ya creados no se rompen (campos nuevos opcionales;
  los reusados ya existían). No hay migración (entorno demo). Re-seed por
  `pnpm seed:catalogo` (upsert + `esquemaVersion++`).
- **Fuera de alcance (decidido con el usuario):** grado de consulta art. 69 CPT y recurso de
  casación. El doc no los desarrolla; se dejan para un change futuro si el usuario lleva casos
  hasta ese nivel.

## Decisiones confirmadas con el usuario
1. Las 3 correcciones, todas **doc-fiel** (recurso tras subsanar / auto admisorio tras subsanar
   / orden prep→citación en doble). ✅
2. Extender a **2ª instancia real** (no consulta ni casación). ✅
3. Reutilizar los campos de recurso (no crear paralelos) para el rechazo tras subsanar. ✅
