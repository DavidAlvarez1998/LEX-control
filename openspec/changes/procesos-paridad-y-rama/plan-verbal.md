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

## Tareas — estado (2026-06-23)

El verbal estaba **más sano de lo previsto**. Auditoría: sin campos duplicados, sin
referencias rotas en `mostrarSi`/etapas (144 campos, todo consistente).

1. ✅ **Rama (Opción B)** — cubierto por el trabajo transversal: `radicadoJudicial→radicado`
   (espejo refleja a la columna), botón "Actualizar con la Rama" en el formulario de etapa y
   en el de creación, y la contraparte se agrega como sujeto procesal. Verbal es grupo
   JUDICIAL con `radicado`+`juzgado` → todo aplica igual que al sumario.
2. ✅ **Unificar juzgado** — `espejoColumnasDesdeDatos` ya refleja el campo `juzgado` → columna
   `proceso.despachoJuzgado`. Una sola fuente efectiva.
3. ✅ **Condicional de montos** — ya estaba: `montoPretensiones`/`montoTotal` con
   `mostrarSi: tipoPretension == "Determinadas"`. Nada que cambiar.
4. ✅ **Ruteo de recursos** — ya estaba correcto: `segunda_instancia` exige
   `recursoTipo == "Apelación"` + `apConcedido == "Sí"`; `recurso_mismo_despacho` exige los
   otros 4 (Aclaración/Corrección/Adición/Reposición). Fiel al CGP.
5. ✅ **Verificado** — `createProceso` de un verbal crea OK (incluye el fix del bug de
   `cuantia` categoría → Decimal); 12/12 tests de flujos verbales verdes; reconvención del
   verbal **intacta** (sí aplica, a diferencia del sumario).

**Conclusión:** el verbal no requiere cambios de seed; queda al estándar de la mínima cuantía
con la Rama integrada. Pendiente solo el smoke en vivo (pegar radicado real en la UI).
