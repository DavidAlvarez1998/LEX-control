# Plan — Proceso verbal (civil ordinario)

> SDD por caso · paraguas: [proposal.md](proposal.md) · doc fuente:
> `roadmap-docs/JURISDICCIÓN ORDINARIO CIVIL- PROCESO VERBAL.docx`
> análisis previo: `openspec/changes/procesos-verbales-civil/{doc-verbal,validacion-vs-doc,validacion,design}.md`

## Estado actual (verificado en seed-tipos.json)

- **144 campos, 16 etapas.** Doble instancia (CGP 368–373), apelable, dos audiencias
  (inicial 372 / instrucción 373). Reconvención, excepciones de mérito y medidas
  cautelares modeladas como campos inline.
- Documentos anclados por campo (grupo JUDICIAL, vía `anclasPorCampo`). Sin plantillas
  generadas (es ficha-only, como el laboral) — **esto es correcto, no una brecha**.
- Validación funcional previa: conforme al doc (28/28 en `validacion.md`), tests verdes.

## Problemas del doc (a reconciliar, no a copiar)

1. **Pretensión determinada → montos**: el doc pide condicional (DETERMINADAS abre montos,
   INDETERMINADAS no). Verificar si `montoPretensiones`/`montoTotal` ya tienen
   `mostrarSi`/`requeridoSi` sobre `tipoPretension`; si no, agregarlo.
2. **Tipos de recurso**: el doc lista apelación/aclaración/corrección/adición/reposición.
   El campo `recursoTipo` los tiene, pero **solo apelación** gatea segunda instancia.
   Confirmar que aclaración/corrección/adición/reposición ruteen al despacho de origen y
   no a 2ª instancia.
3. Granularidad de audiencias: el doc las describe en bloques narrativos; la impl los tiene
   como campos sueltos. **Se queda como está** (validado) — solo documentar la equivalencia.

## Brechas vs. mínima cuantía

- **Consumo de la Rama (la principal):** ver abajo. Hoy el botón no aparece.
- Plantillas: **N/A** (verbal no genera documentos; adjunta). No es brecha.
- Documentos anclados / terminales / motor: ya en paridad.

## Enganche con la Rama Judicial

Estado de llaves: `juzgado` ✅ (campo soloFicha) · `radicado` ❌ · `fechaRadicacion` ❌.
El radicado vive en `proceso.radicado` (header `RadicadoDato`); el despacho en
`proceso.despachoJuzgado` **y además** existe el campo `juzgado` del esquema → **doble
fuente del juzgado** a unificar.

**Aplica la Opción B del paraguas:** generalizar `BotonActualizarRadicado` para que tome el
radicado de la columna canónica y escriba el despacho a `juzgado` (campo) + columna, y la
fecha a `fechaRadicacion` si se decide exponerla. `validarRadicado(23díg)` ya devuelve
`{despacho, fechaProceso}`.

## Tareas

1. **Decidir** A vs. B (paraguas). Asumiendo B.
2. **Unificar juzgado**: resolver `proceso.despachoJuzgado` (columna) vs. `juzgado` (campo
   esquema) — una sola fuente; el autollenado escribe ahí.
3. **Generalizar el botón** para verbal: leer radicado de `proceso.radicado`, autollenar
   juzgado (+ fecha si se modela). Reusar el `RadicadoDato` que ya consulta la Rama.
4. **Condicional de montos** (`tipoPretension` → `montoPretensiones`/`montoTotal`) si falta.
5. **Recursos**: validar ruteo apelación→2ª instancia vs. los demás→mismo despacho.
6. **Verificar** sin regresiones en mínima cuantía; smoke: pegar radicado real → juzgado/
   fecha llegan de la Rama; simular admite/inadmite/subsana/recurso/2ª instancia.
