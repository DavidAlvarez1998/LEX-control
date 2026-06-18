# tutela-seguimiento-flujo

## Por qué

Complemento de [[tutela-creacion-simple]]. Aquél dejó la **creación** de la tutela como el
doc Juan David la pide (cliente → subir Demanda/Pruebas/Anexos). El usuario aclara
(2026-06-17) que **todo lo demás del doc va en la vista siguiente con los pasos a seguir,
como ya funcionan las peticiones**: el radicado de la tutela (cuando el juzgado responde, no
al enviarla), ¿admitieron? Sí/No, el auto admisorio (un documento → opción para adjuntarlo),
el fallo (Favorable/Desfavorable + subir el fallo), la impugnación Sí/No (con Sí → fecha),
el fallo de segunda instancia, y el incidente de desacato (fecha + escrito/fallo). Pidió
**aterrizar el flujo de la vida real con el documento**.

La ficha de proceso (`procesos/[id]`, reutilizada por peticiones y acciones
constitucionales) **ya** renderiza el stepper de etapas + el formulario condicional
(`DatosProceso`). PERO los **bloques de subida de documentos con nombre** (auto admisorio,
sentencia, impugnación, desacato…) se anclan a campos `requierePoder` / `queSolicita` /
`contestaron` / `contestada` que **la tutela no tiene**. Resultado: el seguimiento de la
tutela **no tiene dónde subir esos PDF inline** — solo quedaba adjuntar-por-URL o generar de
plantilla en la tarjeta lateral. Ese es el hueco a cerrar.

## Flujo real de la tutela (Decreto 2591/1991) aterrizado con el doc

| Paso (etapa) | Vida real | Campos / documentos |
| --- | --- | --- |
| Radicación y reparto | Se presenta la tutela; se radica y reparte. El juez tiene 10 días háb. para fallar | `fechaPresentacion`; **Demanda** (oblig.), Pruebas, Anexos; luego `radicadoTutela` (lo asigna el juzgado) |
| Admisión y traslado | El juez avoca, admite y corre traslado al accionado | `admitida` Sí/No → si Sí: `fechaAutoAdmisorio` + **Auto admisorio** (adjuntar) |
| Fallo de 1ª instancia | Dentro de los 10 días | `falloPrimera` Favorable/Desfavorable → `fechaFallo` + **Sentencia** (adjuntar) |
| Impugnación | Cualquiera de las partes, 3 días háb. desde la notificación | `impugnada` Sí/No → si Sí: **`fechaImpugnacion`** (nuevo) + **Impugnación** (adjuntar) |
| Fallo de 2ª instancia | El superior decide en 20 días | `falloSegunda` Favorable/Desfavorable + **Sentencia 2ª** (adjuntar) |
| Remisión a Corte Const. | Todo fallo se remite para eventual revisión | (etapa de seguimiento) |
| Incidente de desacato | Si no cumplen, se promueve; el juez requiere y sanciona | `incidenteDesacato` Sí/No → si Sí: `fechaIncidenteDesacato` + **Escrito** y **Fallo** del desacato (adjuntar) |

## Qué cambia

### 1. La ficha muestra los adjuntos con nombre para tipos sin anclas DdP (frontend)
`components/datos-proceso.tsx`: además de los bloques anclados a `requierePoder`/
`contestaron` (DdP), se renderiza un bloque **"Documentos del proceso"** con los documentos
(requeridos + opcionales) de las etapas que **no quedaron anclados** a ningún campo. Para la
tutela —que no tiene esos campos— ahí caen todos sus adjuntos, subibles inline con el mismo
`BotonSubirDoc` (subida real a tecnovapp). Para el DdP el conjunto sin-anclar es vacío → **no
cambia**. La lista **crece según el avance** (usa `documentos…DeEtapas(etapas, borrador)`).

### 2. Documentos del seguimiento = contextuales (catálogo, `seed-tipos.json`)
Los documentos de las etapas de la tutela pasan de requeridos fijos a **opcionales
condicionados** (`opcionalesSi`), para que aparezcan como "opción para adjuntar" cuando
corresponde, en línea con el doc:
- `admision`: `auto_admisorio.pdf` solo si `admitida = SI`.
- `falloPrimeraInstancia`: `sentencia.pdf` solo si `falloPrimera ∈ {Favorable, Desfavorable}`.
- `impugnacion`: `impugnacion.pdf` opcional (la etapa ya está condicionada a `impugnada = SI`).
- `falloSegundaInstancia`: `sentencia_segunda.pdf` solo si `impugnada = SI` (+ escrito/fallo
  de desacato si `incidenteDesacato = SI`, ya existente).
- `radicacion`: **`demanda.pdf` sigue siendo obligatorio** (sin él no se presenta la tutela);
  `pruebas.pdf`/`anexos.pdf` opcionales (sin cambios).

### 3. Campo nuevo: fecha de la impugnación (catálogo)
`fechaImpugnacion` (`fecha`, `soloFicha`, `mostrarSi impugnada = SI`) — el "si entra con un Sí
crea los campos para poner la fecha" que pidió el usuario y que el doc lista bajo IMPUGNACIÓN.

## Impacto
- **Frontend**: `components/datos-proceso.tsx` (bloque de documentos sin-anclar en la ficha).
  La creación (`procesos/nuevo`) ya usaba el bloque fallback → sin cambios extra.
- **Catálogo**: `prisma/seed-tipos.json` solo el tipo "Acción de tutela" (1 campo nuevo + 4
  etapas con documentos `opcionalesSi`). Re-seed con `pnpm seed:catalogo`.
- **Schema / backend**: sin cambios. El Zod del catálogo strippea `soloFicha`/`opcionalesSi`
  (el seed guarda el JSON crudo), así que `seed-tipos.test` sigue verde.

## Fuera de alcance
- Los campos sustantivos (`hechos`, `pretension`, `derechosFundamentales`, `juramento`…) que
  alimentan la plantilla `DEMANDA_TUTELA` siguen `soloFicha` (decisión híbrida de
  [[tutela-form-hibrida]]); se ven en la ficha para quien quiera generar la demanda. Si se
  quiere ocultarlos del seguimiento, va aparte.
- "Acción de Tutela (Recibida)" (defensiva): intacta.
- El incidente de desacato se modela como campos + adjuntos (no como etapa propia del
  stepper), igual que en el doc.

## Decisiones del usuario (2026-06-17)
- **Creación = solo subir Demanda/Pruebas/Anexos**; el radicado de la tutela y el resto del
  tracking van en la vista siguiente (los pasos), como las peticiones.
- **Documentos como "opción para adjuntar"** que aparecen al avanzar (no gates duros salvo la
  demanda).
- **Impugnación Sí → fecha**.
- **Aterrizar el flujo real con el doc** (tabla de arriba).
