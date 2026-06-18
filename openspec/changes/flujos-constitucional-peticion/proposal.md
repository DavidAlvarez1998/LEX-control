# flujos-constitucional-peticion

## Por qué

Para el Proceso Laboral construimos mapas de flujo **completos** (grafo + fases + detalle
campo-por-campo + ramas), que sirvieron para revisar y corregir el flujo contra el doc fuente.
Las vistas **ya existentes** de **Acciones Constitucionales** y **Peticiones** (Derecho de
Petición y variantes) NO tienen ese mapa documentado: su flujo vive solo en el seed
(`prisma/seed-tipos.json`) y, parcialmente, en el doc `DERECHO DE PETICIÓN - JUAN DAVID.docx`.

El usuario pidió **documentar los flujos completos de lo ya creado** (constitucional + petición)
con el mismo formato que el laboral, **para poder compararlos** con lo que tenemos y detectar
inconsistencias o huecos. Es una tarea de **documentación/análisis** (no implementación).

## Qué cambia

**Nada de código ni seed.** Se generan **mapas de flujo** (uno por tipo) en `maps/`, con el
mismo formato que el laboral (`design.md`/`flujos-detallados.md` del change
`laboral-doble-instancia`): grafo del flujo, fases, detalle campo-por-campo, documentos y ramas
por opción. Fuente de verdad: el **seed** (lo realmente implementado) + el doc Juan David
(`fuente-juan-david.txt`) donde aplique. Más un `comparacion.md` que contrasta los 9 flujos
entre sí y con el laboral.

### Tipos a mapear (9)
**Peticiones (grupo PETICION):**
1. Derecho de Petición — doc Juan David (sección DdP)
2. Derecho de Petición Recibido — variante "recibido" (somos la entidad que responde)
3. Reclamación Administrativa — (legal; previa a lo laboral/pensional)
4. Constitución de Renuencia — (Ley 393; previa a acción de cumplimiento)

**Acciones constitucionales (grupo CONSTITUCIONAL):**
5. Acción de tutela — doc Juan David (sección tutela)
6. Acción de Tutela (Recibida) — variante "recibida"
7. Acción de cumplimiento
8. Acción popular
9. Acción de grupo

## Impacto

- **Solo documentación** en `openspec/changes/flujos-constitucional-peticion/`. Sin tocar
  seed, API ni cliente.
- Generado con **SDD + agentes en paralelo** (un agente por tipo lee su entrada del seed + el
  doc y escribe su mapa; un agente final sintetiza la comparación).
- Sirve de insumo para una eventual revisión/corrección (como se hizo con el laboral), que
  sería un change aparte si el usuario lo decide.

## Alcance / decisiones
- Es para **comparar**, no para cambiar el comportamiento. Si al mapear aparecen huecos
  (ramas que el doc pide y el seed no modela, o al revés), se **anotan** en cada mapa y en
  `comparacion.md`; la corrección queda para decidir después.
- Módulos fuera de estas dos vistas (laboral ya hecho; judicial/familia/administrativo) quedan
  fuera de este alcance.
