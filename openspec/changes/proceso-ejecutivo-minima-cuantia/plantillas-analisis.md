# Plantillas automáticas — análisis de los 6 modelos (ejecutivo mínima cuantía)

> Estado: **ANÁLISIS para revisar juntos** (vía 6 agentes en paralelo). Nada
> implementado todavía.
> Fuente: `openspec/roadmap-docs/ejecutivo minima cuantia/*.docx`.
> Relacionado: [proposal.md](./proposal.md) (el tipo y sus 8 etapas, ya aplicado).

## 0. Para qué sirve esto

Los 6 modelos `.docx` son **escritos legales reutilizables** → candidatos a
`PlantillaDocumento` (motor Handlebars en `procesos/plantilla.ts`). Se generan
desde la ficha del proceso (`Generar borrador`/`Generar y descargar`) y se anclan
a su etapa por nombre de archivo. Este análisis dice: **qué es cada uno, en qué
etapa va, si conviene plantilla automática, y qué campos faltan** para llenarlos
sin huecos.

## 1. Hallazgos del motor (límites que mandan en el diseño)

Verificado leyendo `plantilla.ts` / `construirContexto` / `schema.prisma`:

- ✅ **`{{#each datos.lista}}` SÍ funciona** sobre un array de objetos en `datos`
  (con `{{this.campo}}` y `{{@index}}` que arranca en **1**). → el **cronograma de
  cuotas del acuerdo de pago es viable**.
- ⛔ **`{{#if}}` solo evalúa verdad/falsedad** de un path. **No hay igualdad ni
  "includes"**. → no se puede preguntar "¿`motivoTerminacion` == Pago total?" ni
  "¿el multiselect contiene 'Embargo de salarios'?". Para ramificar texto hay que
  usar **flags booleanos** (`esPagoTotal`, `embargoSalarios`, …).
- El contexto expone: `datos.*`, `proceso.*` (`radicado`, `despachoJuzgado`,
  `codigoInterno`, `cuantiaValor`, `createdAt`, `etapaActual`),
  `parte.demandante/demandado/cliente`, `partes[]`. Helpers: `moneda`, `enLetras`,
  `fecha`, `mayus`. `[[falta: x]]` marca lo no resuelto (no rompe).
- ⛔ **`Litigante` (las partes) NO tiene domicilio/ciudad/dirección** — solo
  nombre, tipoPersona, tipo/numeroDocumento, email, correos, telefono.
- ⛔ **El contexto NO expone el abogado responsable**, y `Usuario` solo tiene
  `nombre`/`email` (sin cédula ni T.P.). → el bloque de firma del abogado no sale
  solo.
- ⛔ **No hay "última actuación" legible** (la bitácora no se proyecta al contexto).

→ De aquí salen **dos necesidades transversales** que aparecen en varios escritos:
**(A) datos del abogado firmante** (nombre, cédula, T.P., correo, dirección) y
**(B) domicilio/ciudad de las partes**.

## 2. Los 6 documentos — qué es cada uno y dónde va

| # | Documento | Qué es | Etapa | Archivo | ¿Plantilla auto? |
|---|---|---|---|---|---|
| 1 | **Demanda** | Escrito que abre el proceso; pide librar mandamiento de pago | `radicacion` | `demanda.pdf` | **Sí (borrador)** |
| 2 | **Poder especial** | El cliente otorga poder al abogado | `radicacion` | `poder.pdf` | Parcial (borrador para firmar el cliente) |
| 3 | **Medidas cautelares** | Solicitud de embargo de salarios y/o cuentas | `radicacion` + `notifCautelares` | `solicitud-cautelares.pdf` | **Sí (borrador)** |
| 4 | **Memorial** | Escrito de impulso (pide estado del proceso) | `impulsos` | `memorial.pdf` | **Sí** |
| 5 | **Acuerdo de pago** | Convenio deudor-acreedor con cronograma de cuotas | `impulsos` → lleva a `terminacion` | `acuerdo-pago.pdf` | **Sí (con `#each` de cuotas)** |
| 6 | **Terminación** | El abogado **solicita** terminar por cumplimiento | `terminacion` | `solicitud-terminacion.pdf` | Parcial |

**Aclaración importante (doc 6):** la *solicitud* de terminación la presenta el
abogado (se **genera**); el **`auto-terminacion.pdf`** lo emite el juez (se
**adjunta**). Son dos documentos distintos en la misma etapa.

## 3. Detalle por documento (variables + campos nuevos)

### 1) Demanda → `radicacion` / `demanda.pdf` — candidato fuerte
- Mapea solo: `parte.demandante/demandado.*`, `datos.cuantia/capitalAdeudado/
  tasaInteresMoratorio/fechaExigibilidad`, `hechos`, `pretensiones`.
- **Campos nuevos:** `ciudadReparto`, `ciudadDemandante`, `direccionDemandado`,
  `ciudadDemandado`, `pruebas` (lista), + abogado firmante (transversal A).
- Nota: `hechos`/`pretensiones` lucen mejor como **listas** (`#each`); hoy son
  `textoLargo`. Decisión D6.

### 2) Poder especial → `radicacion` / `poder.pdf` — parcial
- Lo firma el **cliente** (otorgante) → generar **borrador para descargar y
  firmar**, no autoadjuntar.
- **Campos nuevos:** `apoderadoNombre`, `apoderadoDocumento`,
  `apoderadoTarjetaProfesional`, `repLegalNombre`, `repLegalDocumento`,
  `ciudadFirmaPoder`, `fechaPoder`. `{{#if datos.repLegalNombre}}` distingue
  sociedad vs persona natural.

### 3) Medidas cautelares → `radicacion`/`notifCautelares` / `solicitud-cautelares.pdf`
- Lista de ~25 bancos = **texto fijo** en la plantilla.
- ⛔ No se puede condicionar por el multiselect → **flags** `embargoSalarios` /
  `embargoCuentas` (derivables del multiselect al guardar).
- **Campos nuevos:** `embargoSalarios`, `embargoCuentas`, `empleadorDemandado`,
  `domicilioDemandante` (transversal B) + abogado firmante (A).

### 4) Memorial → `impulsos` / `memorial.pdf` — candidato fuerte
- Recomendación: **una plantilla "Memorial" genérica** con `asuntoMemorial`
  variable (el encabezado/firma es igual para cualquier memorial), con preset
  "Solicitud de estado".
- **Campos nuevos:** `ultimaActuacion`, `asuntoMemorial` (opcional).

### 5) Acuerdo de pago → `impulsos` / `acuerdo-pago.pdf` — candidato fuerte
- **El cronograma de cuotas se hace con `{{#each datos.cuotas}}`** (array de
  `{numero, fecha, monto}`). Viable nativo.
- **Campos nuevos:** `numeroCredito`, `numeroCuotas`, `cuotas` (**array**),
  `titularRecaudo`, `contactoSoporte`, `ciudadFirma`, `fechaAcuerdo`.

### 6) Terminación (solicitud) → `terminacion` / `solicitud-terminacion.pdf` — parcial
- Bloqueo: bloque del abogado firmante (transversal A).
- Ramificar por motivo (pago vs desistimiento) exige **flags** (`esPagoTotal`,
  `esDesistimientoTacito`, `esAcuerdoCumplido`) o **una plantilla por motivo**
  (los fundamentos jurídicos divergen mucho entre pago y desistimiento art. 317).

## 4. Necesidades transversales (aparecen en varios documentos)

### A) Abogado firmante — `datos.abogado*` vs. modelo `Usuario`
Aparece en Demanda, Cautelares, Terminación (y el apoderado del Poder).
- **Opción rápida:** campos `datos.abogadoNombre/abogadoCedula/abogadoTarjeta/
  abogadoCorreo/abogadoDireccion` en el tipo (se re-teclean por proceso).
- **Opción de fondo (recomendada a futuro):** añadir `cedula` y
  `tarjetaProfesional` a `Usuario` y **exponer `proceso.responsable.*`** en
  `construirContexto`. No se re-teclea; sirve para TODOS los tipos. Es cambio de
  schema + motor. → Decisión D1.

### B) Domicilio/ciudad de las partes — `datos.*` vs. modelo `Litigante`
Aparece en Demanda y Cautelares.
- **Opción rápida:** campos `datos.ciudadDemandante/direccionDemandado/...`.
- **Opción de fondo (recomendada):** añadir `direccion`/`ciudad` a `Litigante`
  (cambio de schema, reutilizable en todos los tipos y partes). → Decisión D2.

## 5. Decisiones para resolver juntos

- **D1 — Abogado firmante:** ¿campos `datos.*` por proceso (rápido) o extender
  `Usuario`(cédula/T.P.) + exponer `proceso.responsable` (de fondo, no re-teclea)?
- **D2 — Domicilio de partes:** ¿campos `datos.*` (rápido) o extender `Litigante`
  con dirección/ciudad (de fondo, global)?
- **D3 — Medidas cautelares:** ¿derivar flags `embargoSalarios/embargoCuentas`
  del multiselect existente, o checkboxes propios?
- **D4 — Terminación:** ¿flags por motivo en una sola plantilla, o **una plantilla
  por motivo** (pago / acuerdo / desistimiento)?
- **D5 — Hechos/pretensiones (demanda):** ¿pasarlos a **listas** (mejor con
  `#each`) o dejarlos como texto largo?
- **D6 — Alcance ahora:** ¿sembramos las **6** plantillas de una vez, o por
  prioridad? (sugerencia: 1-Demanda, 3-Cautelares, 5-Acuerdo, 4-Memorial primero;
  2-Poder y 6-Terminación después por depender de campos del firmante).

## 6. Si aprobamos — plan (aún NO ejecutado)

1. Agregar los **campos nuevos** al `esquemaFormulario` del tipo en
   `seed-tipos.json` (agrupados por etapa), + flags derivados según D3/D4.
2. (Si D1/D2 = "de fondo") cambios de schema (`Usuario`, `Litigante`) + exponerlos
   en `construirContexto` (con `pnpm push`, no migrate).
3. Sembrar las `PlantillaDocumento` (en `plantillas-seed.ts`) con los borradores
   Handlebars de cada agente, ancladas por nombre de archivo a su etapa.
4. **Verificar:** generar cada plantilla contra un proceso de prueba (render) y
   revisar que no queden `[[falta:]]` inesperados; 456 tests + build.

> Los borradores Handlebars completos de cada documento están en el resultado de
> los agentes; se transcriben a `plantillas-seed.ts` al implementar.
