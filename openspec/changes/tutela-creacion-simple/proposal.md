# tutela-creacion-simple

## Por qué

El change [[tutela-form-hibrida]] ya acortó el **contenido** del formulario de tutela
(campos sustantivos + tracking → `soloFicha`), pero el formulario de creación de
`procesos/nuevo` sigue mostrando el **andamiaje judicial genérico** que la tutela hereda
por ser `esJudicial` (default `true`):

1. **"Rol procesal del cliente"** (select DEMANDANTE/DEMANDADO/EJECUTANTE/…): en una tutela
   el cliente es **siempre el accionante**; elegir rol no aporta y confunde.
2. **"Datos judiciales (opcional)"**: radicado de 23 dígitos, juzgado, **cuantía** y valor.
   Una tutela **no tiene cuantía**, y su "radicado de la tutela" es un campo de seguimiento
   (`radicadoTutela`, `soloFicha`) que se llena después, no el radicado de 23 dígitos.
3. **"Contraparte y otras partes"** (litigantes con `rol` procesal): el accionado de la
   tutela ya se captura en el campo de texto **`entidadAccionada`** ("Autoridad o particular
   accionado"). El doc no modela litigantes con rol para la tutela.

La fuente de verdad —`openspec/roadmap-docs/"DERECHO DE PETICIÓN - JUAN DAVID.docx"`, sección
final "ACCIÓN DE TUTELA"— describe un formulario **mucho más simple**: se elige el cliente
(accionante) y, acto seguido, se **suben los adjuntos `Demanda PDF`, `Pruebas PDF`,
`Anexos PDF`**, seguidos del tracking (radicado → admitieron → auto admisorio → fallo →
impugnación → 2ª instancia → incidente de desacato). Nunca pide rol, cuantía ni contraparte.

Pedido textual del usuario (2026-06-17): *"el form se ve bastante simple en comparación con el
que está actualmente en la app; rol de demandante ni está; una vez selecciona el cliente
debería estar la opción de subir adjuntos demanda, pruebas, anexos"*. Usa SDD.

## Qué cambia

Solo el formulario de creación del portal cliente (`procesos/nuevo/page.tsx`). **Sin cambios
de catálogo, schema ni backend**: el catálogo ya modela `demanda.pdf` (requerido) +
`pruebas.pdf`/`anexos.pdf` (opcionales) en la etapa `radicacion`, y el tracking como
`soloFicha`.

Se introduce el concepto de **tutela ofensiva** en el form:
`esTutelaOfensiva = tipo.grupo === "CONSTITUCIONAL" && !tipo.clienteOpcional`
(la "Acción de tutela" que presentamos; deja fuera la "Acción de Tutela (Recibida)"
defensiva, que tiene `clienteOpcional: true`).

Para `esTutelaOfensiva`:
1. **Se oculta el select "Rol procesal del cliente"**. Al guardar, el rol del cliente se fija
   en **`ACCIONANTE`** (antes `tipo.esJudicial ? clienteRol : "OTRO"`).
2. **Se oculta la tarjeta "Datos judiciales"** (radicado 23díg/juzgado/cuantía/valor).
3. **Se oculta la tarjeta "Contraparte y otras partes"**. El accionado vive en
   `entidadAccionada`.

Con esto el flujo queda, en orden: **Cliente (accionante) → "Autoridad o particular
accionado" → Documentos (Demanda \* / Pruebas / Anexos) → Responsable**, espejo del doc.

4. **Los adjuntos opcionales se suben al crear.** Hoy el bucle de subida tras crear solo
   recorre `documentosRequeridosDeEtapas`, así que `pruebas.pdf`/`anexos.pdf` adjuntados al
   crear se perdían. Pasa a recorrer **requeridos + opcionales** (todo `archivo` adjunto que
   aplique según los datos), para que "subir Demanda, Pruebas y Anexos" funcione de verdad en
   la creación.

## Impacto

- **Frontend cliente**: `src/app/(dashboard)/procesos/nuevo/page.tsx` (tres `&&` de gating, el
  `rolCliente` al guardar, y el bucle de subida que incluye opcionales).
- **Catálogo / schema / backend / plantillas**: **sin cambios**. `DEMANDA_TUTELA` intacta.
- **Re-seed**: no requerido (no toca `seed-tipos.json`).

## Fuera de alcance

- **"Acción de Tutela (Recibida)"** (defensiva, `clienteOpcional: true`): no se toca. Ahí el
  despacho representa al accionado y la contraparte (accionante) sí puede importar.
- Los demás judiciales (civil, laboral…) conservan rol, datos judiciales y contraparte.
- El contenido del esquema (campos `soloFicha`, tracking) ya lo fijó [[tutela-form-hibrida]].

## Decisiones del usuario (2026-06-17)

- **Doc = fuente de verdad**: la tutela se modela como adjuntar + tracking; el form de
  creación debe verse tan simple como el doc.
- **Sin rol**: el cliente de la tutela es el accionante; no se ofrece elegir rol.
- **Adjuntos tras elegir cliente**: Demanda (obligatoria) + Pruebas + Anexos, subibles al
  crear.
- **Gate por tutela ofensiva** (`CONSTITUCIONAL && !clienteOpcional`): deja intacta la
  recibida (defensiva), consistente con el "fuera de alcance" de [[tutela-form-hibrida]].
