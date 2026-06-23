# Paridad de procesos + consumo de la Rama Judicial (SDD paraguas)

> Estado: **PLAN (SDD)** · 2026-06-23 · rama `feat/cuenta-clientes`
> Patrón de referencia: **Proceso ejecutivo de mínima cuantía** (`openspec/changes/proceso-ejecutivo-minima-cuantia/`).

## Por qué

El **ejecutivo de mínima cuantía** quedó como el tipo "estándar de oro": flujo fiel a su
doc, documentos anclados por campo, y **consumo de la API de la Rama Judicial** (botón
"Actualizar con la Rama" que, al digitar los 23 dígitos del radicado, autollena el
*juzgado* y la *fecha de radicación* en el formulario — `BotonActualizarRadicado` en
`lex-control-client/src/components/datos-proceso.tsx`).

Los **demás procesos que tienen documento** en `openspec/roadmap-docs/` ya están creados,
**validados y en una etapa de validación muy avanzada** (no son borradores: por eso NO
llevan la nota "no actualizado"). Lo que falta es:

1. **Extenderles el consumo de la Rama** (el botón "Actualizar") donde aplica.
2. **Reconciliar su doc fuente con la implementación** — sabiendo que **los .docx están
   "algo mal"** (campos repetidos, nomenclatura inconsistente, ramas ambiguas): el doc
   **no** es la autoridad ciega; manda lo ya **validado** en la implementación, y el doc
   sirve para detectar faltantes reales.
3. **Limpiar** los campos duplicados/muertos que arrastra cada flujo.

Alcance (los que tienen doc, sin contar el de referencia ya hecho):

| Proceso | Doc fuente (roadmap-docs) | ¿Rama? | Plan |
|---|---|---|---|
| Proceso verbal | `JURISDICCIÓN ORDINARIO CIVIL- PROCESO VERBAL.docx` | Sí (radicado CPNU) | [plan-verbal.md](plan-verbal.md) |
| Proceso verbal sumario | `…- PROCESO VERBAL SUMARIO.docx` | Sí | [plan-verbal-sumario.md](plan-verbal-sumario.md) |
| Proceso Laboral | `PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx` | Sí | [plan-laboral.md](plan-laboral.md) |
| Derecho de Petición (env./recibido) | `DERECHO DE PETICIÓN - JUAN DAVID.docx` | **No** (no judicial) | [plan-derecho-peticion.md](plan-derecho-peticion.md) |

## Hallazgo transversal: por qué el botón de la Rama hoy solo sale en mínima cuantía

`BotonActualizarRadicado` se inyecta bajo el campo del radicado **solo si el esquema del
tipo tiene las 3 llaves**: `radicado` + `juzgado` + `fechaRadicacion` (gate en
`datos-proceso.tsx`). Verificado contra `prisma/seed-tipos.json`:

| Tipo | `radicado` | `juzgado` | `fechaRadicacion` | ¿Botón hoy? |
|---|:--:|:--:|:--:|:--:|
| Ejecutivo mínima cuantía | ✅ | ✅ | ✅ | **Sí** |
| Proceso verbal | ❌ | ✅ | ❌ | No |
| Proceso verbal sumario | ❌ | ✅ | ❌ | No |
| Proceso Laboral | ❌ | ❌ | ✅ | No |
| DdP (env./recibido) | ❌ | ❌ | ✅* | N/A (no judicial) |

En verbal/sumario/laboral el **radicado** no es un campo del formulario: vive en la
**columna canónica** `proceso.radicado` (se edita desde el encabezado de la ficha,
componente `RadicadoDato`) y el juzgado en `proceso.despachoJuzgado`. Esa **doble fuente**
(columna vs. campo `juzgado` del esquema) es justamente uno de los "campos repetidos" a
ordenar.

## Decisión de diseño transversal — RESUELTA ✅

**Elegida la Opción B + se incluye la tutela** (usuario, 2026-06-23). El consumo de la Rama
aplica a **todos los judiciales**: verbal, verbal sumario, laboral y **tutela** (todos van
ante un juez y tienen radicado CPNU de 23 dígitos). El DdP queda fuera (no es judicial).

**IMPLEMENTADO** (sin commit): el botón **"Actualizar con la Rama"** se generalizó sobre el
encabezado del radicado de la ficha (`RadicadoDato` en `procesos/[id]/page.tsx`). Aparece
para los judiciales cuyo radicado vive en el encabezado (verbal/sumario/laboral/tutela) y al
hacer clic llama `sincronizarActuaciones` → trae actuaciones + autollena juzgado/fecha
(columna `despachoJuzgado` + campo si el esquema lo tiene) → recarga. En mínima cuantía el
botón sigue en el formulario de etapa (su radicado es campo del esquema), gateado con
`mostrarActualizar = !esquema.tiene("radicado")` para no duplicar. `tsc` verde.

> Pendiente (flujo, no API): las tareas de reconciliación/limpieza de cada plan (campos
> repetidos, condicionales, reconvención oculta en sumario, sub-flujo muerto en laboral).

### Las dos opciones consideradas (histórico)

- **Opción A — alinear esquemas a mínima cuantía.** Agregar `radicado`+`fechaRadicacion`
  (soloFicha) al esquema de verbal/sumario/laboral y mapear el header `RadicadoDato` a
  esos campos. *Contra:* duplica el radicado (columna + campo) y exige migrar datos.

- **Opción B (recomendada) — generalizar el botón.** Hacer que `BotonActualizarRadicado`
  funcione tomando el radicado de **donde ya vive** (la columna `proceso.radicado`, vía el
  header `RadicadoDato`, que **ya** consulta la Rama al guardar) y escribiendo el juzgado/
  fecha a las **llaves que cada tipo tenga** (`juzgado`/`despachoJuzgado`,
  `fechaRadicacion`). Un único punto, sin tocar 3 esquemas ni migrar datos. El header
  `RadicadoDato` ya hace el 90%: solo falta exponer un botón "Actualizar" explícito (hoy el
  autollenado ocurre al *Guardar*) y, en la ficha de etapa, reflejar juzgado/fecha en el
  form.

> Nota: el header `RadicadoDato` (ficha) **ya** llama `sincronizarActuaciones`/`validarRadicado`
> al guardar un radicado de 23 dígitos y autollena juzgado+fecha. Buena parte del trabajo
> es **unificar** ese comportamiento con el botón de mínima cuantía, no construir de cero.

## Método (SDD)

Un **plan por caso** (este folder). Cada plan: estado actual verificado → problemas del
doc → brechas vs. mínima cuantía → enganche de la Rama → tareas concretas. **No se
implementa hasta aprobar los planes.** Al implementar cada caso, se actualiza su plan y se
archiva la spec correspondiente.

## Fuera de alcance

- Tipos **sin doc** en roadmap-docs (familia, contencioso-administrativo, penal, etc.):
  llevan la nota "no actualizado" y no entran aquí.
- Reescribir flujos validados desde cero: se **reconcilia y limpia**, no se reimplementa.
