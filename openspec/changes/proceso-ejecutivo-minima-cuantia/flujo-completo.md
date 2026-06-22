# Ejecutivo de mínima cuantía — FLUJO COMPLETO (consolidado · v2 perfeccionada)

> ✅ **APLICADO + VERIFICADO 2026-06-20** (sin commit). Gate: tsc + 459 tests + 4
> flujos del motor simulados + render de las 6 plantillas (0 faltas inesperadas).
> Implementado: schema `Usuario +cedula +tarjetaProfesional` / `Litigante
> +direccion +ciudad` (`pnpm push`); `construirContexto` expone `proceso.responsable.*`
> y `parte.*.{direccion,ciudad}`; `findProcesoConPartes` carga responsable; seed del
> tipo (50 campos, 11 etapas con condicionales) re-seedeado; 6 plantillas en
> `plantillas-seed.ts` (nombres = slot: demanda.pdf/poder.pdf/solicitud-cautelares.pdf/
> memorial.pdf/acuerdo-pago.pdf/solicitud-terminacion.pdf).
>
> **Desviaciones pragmáticas (forzadas por el motor/formulario):**
> 1. **Cautelares:** el multiselect vacío hacía que el motor NO saltara `notifCautelares`
>    (campo vacío = "decisión pendiente"). Se reemplazó por un select **`solicitaCautelares`
>    (Sí/No)** que gatea la etapa (robusto) + booleans `embargoSalarios`/`embargoCuentas`
>    para los `{{#if}}` de la plantilla + `otrasCautelares` (texto) para las demás medidas.
>    (Supera la decisión #2 "multiselect de 7": el form no podía condicionar el `{{#if}}`
>    por opción ni el motor saltar con el multiselect vacío.)
> 2. **Listas:** el formulario no tiene tipo "lista"/"tabla" → `hechos`, `pretensiones`,
>    `pruebas` y el `cronograma` de cuotas van como **`textoLargo`** (la plantilla los
>    inserta como texto, sin `{{#each}}`). Tipos de campo array = feature aparte.

> Integra la guía de 9 pasos (`Proceso_Ejecutivo_Minima_Cuantia.docx`) + los 6
> modelos de escrito, **revisado documento por documento** contra el seed real
> (`seed-tipos.json`, tipo "Proceso ejecutivo de mínima cuantía", 8 etapas) y el
> CGP. Define, por etapa: **qué se pide para avanzar** (gating), qué se puede
> **GENERAR** (plantilla) y qué se **ADJUNTA** (lo emite un tercero).
> Decisiones aplicadas: D1/D2 "de fondo" (abogado en `Usuario`, domicilio en
> `Litigante` **para ambas partes**), D3 flags cautelares, D4 **una sola** plantilla
> de terminación (motivo cumplimiento/pago), D5 hechos/pretensiones/pruebas como
> listas. Estado: **diseño para revisar** (no implementado).
>
> ⚠️ Esta es la fuente de verdad del flujo. `proposal.md` (9 etapas) queda
> **superado** por este documento (8 etapas: acuerdo y desistimiento son *motivos
> de `terminacion`*, no etapas). Ver la tabla de trazabilidad al final.

## Decisiones finales (cerradas con el usuario · 2026-06-20)

1. **Poder:** usar el modelo de ejemplo tal cual (poder general/administrativo) para
   la plantilla. (Nota: no es un poder judicial; queda así por decisión del usuario.)
2. **Cautelares:** se mantienen las 7 opciones del multiselect (medidas reales),
   pero la plantilla `solicitud-cautelares.pdf` solo **redacta salarios + cuentas**
   (las que tienen modelo); otras medidas seleccionadas se marcan para redacción manual.
3. **Audiencia art. 392:** se modela como **etapa propia** `audiencia`
   (`disponibleSi: contesto = Sí`), no como campos dentro de `mandamientoPago`.
4. **Remate:** **etapas dedicadas** `liquidacionCredito` (art. 446) + `avaluoRemate`
   (arts. 444–457), condicionales a la vía de remate.
5. **Desistimiento tácito (317):** solo **motivo de cierre** en `terminacion`; v1
   NO enforza el plazo de inactividad (decisión consciente; se puede agregar luego).
6. **Cita legal de cautelares:** **literal/fiel al doc** (se conserva la mención al
   CPC art. 531 del modelo, aunque esté derogado).
7. **Única instancia:** se documenta como **nota** del tipo (mínima cuantía =
   única instancia, juez civil municipal); la UI no ofrece apelación/2ª instancia.

**Estructura resultante (~11 etapas, varias condicionales):**
`radicacion → radicacionJuzgado → calificacion → [subsanacion si inadmite] →
[notifCautelares si hay cautelares] → mandamientoPago → [audiencia si contesta] →
impulsos → [liquidacionCredito + avaluoRemate si vía remate] → terminacion (terminal)`.

## Convenciones

- **GENERAR** = plantilla Handlebars → `DocumentoProceso` (categoria GENERADO);
  se descarga/edita. **ADJUNTAR** = subir archivo real (tecnovapp) — lo produce el
  juzgado/tercero. El **gating** de avance es por `nombre` de archivo.
- Datos: `datos.*` = campos del proceso · `parte.demandante/demandado.*` (incluye
  ahora `direccion`/`ciudad` para **ambas** partes; `telefono`/`email`/`numeroDocumento`
  ya existían) · `proceso.responsable.*` (abogado: nombre, cédula, **lugar de
  expedición**, T.P., correo, **dirección de notificaciones**).
- **Límite del motor:** `{{#if}}` solo evalúa verdad/falsedad (no igualdad ni
  "includes"). Para ramificar texto por valor de un select/multiselect se usan
  **flags booleanos** (`embargoSalarios`, `esAcuerdoCumplido`, …). En cambio el
  **gating de etapas** (`disponibleSi`) SÍ evalúa `contains` sobre multiselect/array
  (`esquema.ts`), por eso `notifCautelares` puede condicionarse al multiselect.

## Flujo por etapa

### 1 · `radicacion` — Radicación de la demanda ejecutiva
- **Para avanzar:** campos `tipoTitulo, claseObligacion, capitalAdeudado,
  fechaExigibilidad, cuantia, hechos[], pretensiones[]` + docs **`poder.pdf`**,
  **`demanda.pdf`**.
  - *(Se agregaron `hechos` y `claseObligacion` al gating: ambos son `requerido:true`
    en el form y la plantilla de demanda los necesita; antes el gating los omitía.)*
- **GENERAR:** 📄 Demanda (`demanda.pdf`) · 📄 Poder (`poder.pdf`, se
  genera→firma el otorgante/cliente) · 📄 Solicitud de medidas cautelares
  (`solicitud-cautelares.pdf`, **solo si `medidasCautelaresSolicitadas` no está vacío**
  — `mostrarSi`/flag, para no generar un escrito mudo).
- **ADJUNTAR:** el poder firmado (si se sube escaneado).
- **Campos extra:** `medidasCautelaresSolicitadas` (multiselect) → flags derivados
  `embargoSalarios`/`embargoCuentas`, `empleadorDemandado`; `tasaInteresMoratorio`,
  `ciudadReparto`, `pruebas[]`.

### 2 · `radicacionJuzgado` — Radicación en el juzgado
- **Para avanzar:** campos `radicado, juzgado, fechaRadicacion` + doc
  **`constancia-radicado.pdf`**.
- **GENERAR:** — (lo asigna el sistema judicial).
- **ADJUNTAR:** 📎 constancia de radicado / acta de reparto.

### 3 · `calificacion` — Calificación (Admite / Inadmite) · *rama*
- **Para avanzar:** campos `decisionCalificacion, fechaAdmision` + doc
  **`auto-calificacion.pdf`**. Si **Inadmite** → `causalInadmision`.
- **GENERAR:** — (el auto lo emite el juez).
- **ADJUNTAR:** 📎 auto admisorio / inadmisorio.
- **Rama:** Inadmite → etapa 4 (subsanación). Admite → al admitir decreta y libra
  las cautelares **si se pidieron**; sigue a etapa 5 (que solo existe si hubo
  cautelares — ver abajo) o, si no hubo, salta directo a etapa 6.

### 4 · `subsanacion` — Subsanación (solo si Inadmite) · *plazo 5 días hábiles*
- **Para avanzar:** campos `decisionTrasSubsanacion, fechaSubsanacion` + doc
  **`subsanacion.pdf`**. Plazo: 5 días hábiles desde `fechaAdmision`.
- **GENERAR:** — **No hay modelo fuente de subsanación.** La etapa es **solo
  ADJUNTAR** el escrito de subsanación radicado.
  - *(Cambio: antes reusaba la "plantilla Memorial genérica". Se descarta: el
    Memorial fuente es una solicitud de estado del proceso con cuerpo fijo de 5
    peticiones — incoherente para una subsanación. Una subsanación expone la causal
    de inadmisión y la corrección; mientras no haya modelo fuente propio, no se
    genera.)*
- **ADJUNTAR:** 📎 el escrito de subsanación radicado.

### 5 · `notifCautelares` — Notificación de las medidas cautelares · *condicional*
- **`disponibleSi`:** `medidasCautelaresSolicitadas` **contains** alguno de
  `["Embargo de inmuebles","Embargo de muebles","Secuestro","Embargo de cuentas
  bancarias","Embargo de salarios","Embargo de vehículos","Inscripción de la
  demanda"]`. **Si no se pidieron cautelares, esta etapa NO aplica** y el motor la
  salta como nivel N/A definitivo (va directo a `mandamientoPago`).
  - *(Fix de severidad ALTA: antes la etapa exigía siempre `entidadesOficiadas` +
    `oficios-cautelares.pdf`, bloqueando cualquier ejecutivo sin cautelares — que el
    doc trata como opcionales.)*
- **Para avanzar (solo si aplica):** campo `entidadesOficiadas` + doc
  **`oficios-cautelares.pdf`**.
- **GENERAR:** — (los oficios los libra el juzgado; la *solicitud* ya se generó en
  la etapa 1).
- **ADJUNTAR:** 📎 oficios librados / constancias (bancos, Tránsito, registro).

### 6 · `mandamientoPago` — Mandamiento de pago y notificación · *rama, plazo 10 días hábiles*
- **Para avanzar:** campos `fechaMandamiento, fechaNotificacion, contesto` + docs
  **`mandamiento-pago.pdf`**, **`notificacion-demandado.pdf`**.
- **Rama CONTESTA = Sí** → continúa hacia la **audiencia única del art. 392 CGP**
  (en mínima cuantía con excepciones, el ejecutivo se tramita por verbal sumario y
  la audiencia única resuelve excepciones y dicta sentencia):
  - `requeridosSi (contesto = Sí)`: `excepcionesPropuestas`, `fechaAudiencia`,
    `sentenciaExcepciones` (select: *Prosperan* / *No prosperan*) + docs
    **`excepciones.pdf`**, **`acta-audiencia.pdf`**, **`sentencia.pdf`**.
  - Plazo excepciones: 10 días hábiles desde `fechaNotificacion`.
  - *(Cambio: antes la rama "Contesta → audiencia/excepciones" no tenía
    materialización real y todo se diluía en impulsos. Ahora hay campos y docs del
    hito procesal central.)*
- **Rama NO contesta** → queda en firme → sigue la ejecución (a impulsos/remate).
- **GENERAR:** — (mandamiento y notificación son del juzgado).
- **ADJUNTAR:** 📎 mandamiento de pago · notificación al demandado · (si contesta)
  escrito de excepciones · acta de audiencia · sentencia.

> **Decisión pendiente:** modelar la audiencia como **etapa propia** (`audiencia`,
> `disponibleSi: contesto = Sí`) en lugar de campos en `mandamientoPago`. Aquí se
> aplicó la opción mínima (campos+docs en `requeridosSi`); la etapa separada es más
> fiel pero cambia la estructura del seed → ver `decisionesParaUsuario`.

### 7 · `impulsos` — Impulsos procesales (incluye liquidación, avalúo y remate)
- **Para avanzar:** campo `descripcionImpulso`.
- **Rama remate (tras sentencia de "seguir adelante la ejecución"):** se modela la
  secuencia del CGP antes del cierre efectivo:
  - **Liquidación del crédito (art. 446):** campo `valorLiquidacion` + doc
    **`liquidacion-credito.pdf`**.
  - **Avalúo y remate (arts. 444–457):** campos `valorAvaluo`, `fechaRemate` + docs
    **`avaluo.pdf`**, **`acta-remate.pdf`**.
  - *(Cambio: antes avalúo/remate eran solo `documentosOpcionales` sin ningún campo
    de datos y no existía liquidación del crédito.)*
- **GENERAR:** 📄 Memorial (`memorial.pdf` — **solicitud de estado del proceso**,
  fiel al modelo fuente, con cuerpo fijo de 5 peticiones) · 📄 Acuerdo de pago
  (`acuerdo-pago.pdf`, con cronograma de cuotas `{{#each}}`).
- **ADJUNTAR:** 📎 liquidación, avalúo, acta de remate, otros memoriales/oficios.
- **Campos para las plantillas (no requeridos para avanzar, sí para generar sin
  `[[falta:]]`):** `asuntoMemorial` (preset por defecto = *"Solicitud de información
  sobre el estado del proceso de la referencia"*), `ultimaActuacion`; y los del
  acuerdo (ver §Campos nuevos).

### 8 · `terminacion` — Terminación · *TERMINAL (cerrar con motivo)*
- **Para cerrar:** campos `motivoTerminacion, fechaTerminacion` + doc
  **`auto-terminacion.pdf`** (requerido — evidencia del cierre que emite el juez).
- **`motivoTerminacion`** (select): *Pago total* / *Sentencia: seguir adelante la
  ejecución y remate* / *Acuerdo de pago cumplido* / *Desistimiento tácito (art.
  317 CGP)*.
  - **"Sentencia: seguir adelante la ejecución y remate" NO cierra el proceso:**
    encamina a la **rama de remate (etapa 7)** — liquidación → avalúo → remate —
    antes del cierre efectivo. El proceso solo se da por CERRADO con el pago
    (con producto del remate), pago total, acuerdo cumplido o desistimiento.
    *(Fix: antes este motivo ponía estado=CERRADO sobre un proceso que legalmente
    sigue vivo.)*
- **Flags derivados** (el motor no compara strings): `esPagoTotal`,
  `esAcuerdoCumplido`, `esDesistimientoTacito`. Cuando
  `motivoTerminacion = "Acuerdo de pago cumplido"` → `esAcuerdoCumplido = true`
  (habilita la rama de cierre por acuerdo; idealmente exige que exista ya
  `acuerdo-pago.pdf`).
- **GENERAR:** 📄 **Una sola** Solicitud de terminación (`solicitud-terminacion.pdf`)
  fiel al único modelo fuente, redactada para el **motivo de cumplimiento/pago**.
  - *(Fix de severidad ALTA: antes se proponían 3 plantillas por motivo. Solo existe
    documento fuente para cumplimiento/pago. "Acuerdo cumplido" y "Desistimiento
    tácito" NO tienen modelo fuente — generarlas sería inventar contenido legal,
    especialmente el desistimiento art. 317, cuyos fundamentos divergen por
    completo. Esos dos motivos se cubren **solo con ADJUNTAR** el auto del juez.)*
- **ADJUNTAR:** 📎 auto / sentencia de terminación; para acuerdo cumplido y
  desistimiento tácito, el respectivo auto del juez es la única evidencia generable.

> **Nota desistimiento tácito (art. 317 CGP):** hoy es solo un valor de
> `motivoTerminacion`, **sin enforcement** del término de inactividad ni del
> requerimiento previo + 30 días que exige el art. 317. Se documenta como decisión
> consciente (no se enforza el plazo) → ver `decisionesParaUsuario`.

## Resumen de ramas

```
1 radicacion → 2 radicacionJuzgado → 3 calificacion
       ├─ INADMITE → 4 subsanacion → vuelve a 3
       └─ ADMITE → (¿cautelares?) ──Sí──> 5 notifCautelares ─┐
                                  └──No──────────────────────┴─> 6 mandamientoPago
6 mandamientoPago
       ├─ CONTESTA → audiencia única art. 392 (excepciones + sentencia) → 7 impulsos
       └─ NO CONTESTA → ejecución → 7 impulsos
7 impulsos
       ├─ acuerdo de pago → 8 terminacion (Acuerdo cumplido)
       └─ "seguir adelante" → liquidación (446) → avalúo/remate (444-457) → 8 terminacion (pago con remate)
8 terminacion (TERMINAL · CERRADO): Pago total / Acuerdo cumplido / Desistimiento tácito / pago por remate
```

## Resumen de plantillas generables (5)

| Plantilla | Archivo | Etapa(s) | Quién firma |
|---|---|---|---|
| Demanda ejecutiva | `demanda.pdf` | 1 radicacion | abogado |
| Poder | `poder.pdf` | 1 radicacion | **otorgante/cliente** (generar→firmar) |
| Solicitud medidas cautelares | `solicitud-cautelares.pdf` | 1 radicacion (solo si hay cautelares) | abogado |
| Memorial (solicitud de estado) | `memorial.pdf` | 7 impulsos | abogado |
| Acuerdo de pago | `acuerdo-pago.pdf` | 7 impulsos | deudor (demandado) + acreedor (demandante) |
| Solicitud de terminación (motivo cumplimiento/pago) | `solicitud-terminacion.pdf` | 8 terminacion | abogado |

> Bajó de 6 a 5 entradas generables: la subsanación dejó de usar el Memorial
> (etapa 4 = solo ADJUNTAR) y terminación dejó de tener 3 plantillas (solo 1,
> motivo cumplimiento).

### Notas de fidelidad por plantilla

- **Demanda (`demanda.pdf`):**
  - NOTIFICACIONES del **demandado**: `parte.demandado.direccion`,
    `parte.demandado.ciudad`, `parte.demandado.telefono`, `parte.demandado.email`.
  - NOTIFICACIONES del **demandante**: `parte.demandante.direccion` (¡dirección, no
    ciudad!) y `parte.demandante.email`/`correos`.
  - Encabezado del juez parametrizado: `JUEZ CIVIL MUNICIPAL DE {{mayus datos.ciudadReparto}} (REPARTO)`
    (default opcional Pereira, editable). **No** hardcodear "PEREIRA".
  - **Texto fijo** (no huecos): REFERENCIA = "PROCESO EJECUTIVO DE MÍNIMA CUANTÍA";
    "Se trata de un proceso," → "ejecutivo de mínima cuantía".
  - `hechos[]`/`pretensiones[]`/`pruebas[]` con `{{#each}}` + `{{@index}}` (arranca
    en 1) para reproducir "Primero/Segundo…".
  - `tipoTitulo`/`capitalAdeudado`/`tasaInteresMoratorio`/`fechaExigibilidad` son
    **campos de gating/seguimiento**, no variables obligatorias del cuerpo del
    escrito (el modelo no tiene huecos para ellos) → opcionales en la plantilla.
- **Poder (`poder.pdf`):** ver decisión pendiente (el modelo fuente es un poder
  GENERAL/administrativo de representante legal de sociedad, no un poder judicial).
  Bloque de firma único = OTORGANTE (`repLegalNombre` + C.C. `repLegalDocumento`),
  sin firma del apoderado. Redacción neutra de género ("identificado(a)").
- **Cautelares (`solicitud-cautelares.pdf`):**
  - Encabezado al juez de reparto: usa `datos.ciudadReparto` (compartido con la
    demanda; mapear también aquí, no solo en la demanda).
  - Bloque salarios: nombre del empleado + `empleadorDemandado`. Bloque cuentas:
    nombre + **cédula del demandado** = `parte.demandado.numeroDocumento` (mapear
    explícito, si no sale `[[falta:]]`).
  - Texto fijo literal: base legal (art. 531 ss. CPC en encabezado / art. 599 ss.
    CGP al cierre, tal como trae el modelo) y la **lista completa de ~25 bancos**.
  - El multiselect ofrece 7 medidas pero **el modelo fuente solo redacta 2**
    (salarios + cuentas) → ver decisión pendiente.
- **Memorial (`memorial.pdf`):** encabezado fiel (Demandante / Demandado / Asunto);
  cuerpo = 5 peticiones de estado (texto fijo) atado al preset
  `asuntoMemorial`; el blanco "última actuación la ___" = `{{datos.ultimaActuacion}}`
  (si vacío, marcador `[[falta: ultimaActuacion]]`). **Añadido sobre el modelo
  fuente:** bloque de firma `proceso.responsable.*` (nombre, cédula, T.P.) para que
  sea radicable (el modelo fuente termina en "Muchas gracias", sin firma).
- **Acuerdo de pago (`acuerdo-pago.pdf`):**
  - DEUDOR = `parte.demandado` (nombre + tipoDocumento=cédula + `numeroDocumento`).
    ACREEDOR = `parte.demandante` (nombre + **NIT**).
  - Cronograma: cabecera `NÚMERO DE CUOTA | FECHA DE PAGO | PAGO TOTAL`;
    `{{#each datos.cuotas}}` → `{{this.numero}}`, `{{fecha this.fecha}}`,
    `{{moneda this.monto}}` (interno `monto`, rótulo visible "PAGO TOTAL").
  - "en ___ cuotas" se **deriva de `cuotas.length`** (no usar `numeroCuotas` como
    segunda fuente de verdad).
  - Cláusula TERCERA (Paz y Salvo) "a nombre de ___" = `parte.demandado.nombre`
    (default; campo `titularPazSalvo` solo si por negocio difiere).
  - Cláusulas CUARTA (incumplimiento) y QUINTA (aceleratoria: eventos a y b) =
    **texto fijo literal** del modelo.
  - `numeroCredito` se reusa en título + cláusula PRIMERA + cláusula TERCERA.
- **Terminación (`solicitud-terminacion.pdf`):** poderdante
  `actuando como apoderado(a) de {{parte.demandante.nombre}}`; encabezado
  DEMANDANTE/DEMANDADO/RADICADO desde `parte.*`/`proceso.radicado`. Bloque del
  firmante: `C.C. No {{responsable.cedula}} de {{responsable.lugarExpedicionCedula}}`,
  `T.P. No {{responsable.tarjetaProfesional}} del Consejo Superior de la
  Judicatura`, correo de notificación, y firma con Nombre + C.C. +
  `{{responsable.direccionNotificaciones}}`. Redacción neutra de género.

## Documentos que se ADJUNTAN (de terceros / juez)

`constancia-radicado.pdf` · `auto-calificacion.pdf` · `subsanacion.pdf` (escrito
radicado) · `oficios-cautelares.pdf` · `mandamiento-pago.pdf` ·
`notificacion-demandado.pdf` · `excepciones.pdf` · `acta-audiencia.pdf` ·
`sentencia.pdf` · `liquidacion-credito.pdf` · `avaluo.pdf` · `acta-remate.pdf` ·
`auto-terminacion.pdf`.

## Campos nuevos necesarios (resumen)

- **En `Usuario` (D1, de fondo):** `cedula`, `lugarExpedicionCedula`,
  `tarjetaProfesional`, `direccionNotificaciones` → expuestos como
  `proceso.responsable.*`.
- **En `Litigante` (D2, de fondo, AMBAS partes):** `direccion`, `ciudad` →
  `parte.demandante.*` y `parte.demandado.*` (`telefono`/`email`/`numeroDocumento`
  ya existen).
- **En el tipo (`datos.*`):**
  - cautelares: flags `embargoSalarios`/`embargoCuentas`, `empleadorDemandado`.
  - calificación/subsanación: `causalInadmision`.
  - notif. cautelares: `entidadesOficiadas`.
  - mandamiento/audiencia: `contesto`, `excepcionesPropuestas`, `fechaAudiencia`,
    `sentenciaExcepciones`.
  - impulsos/remate: `descripcionImpulso`, `valorLiquidacion`, `valorAvaluo`,
    `fechaRemate`.
  - terminación: `motivoTerminacion`, `fechaTerminacion` + flags `esPagoTotal`,
    `esAcuerdoCumplido`, `esDesistimientoTacito`.
  - acuerdo: `numeroCredito`, `cuotas[]` (`{numero, fecha, monto}`),
    `titularRecaudo`, `contactoSoporte`, `ciudadFirma`, `fechaAcuerdo`
    (`titularPazSalvo` opcional). *(`numeroCuotas` se descarta: derivable de
    `cuotas.length`.)*
  - memorial: `ultimaActuacion`, `asuntoMemorial` (con preset por defecto).
  - demanda: `hechos[]`, `pretensiones[]`, `pruebas[]`, `ciudadReparto`.

## Trazabilidad — guía de 9 pasos → 8 etapas del seed

| Paso (doc fuente) | Etapa-seed (1..8) | Notas |
|---|---|---|
| 1 · Radicar demanda + cautelares (solicitud) | 1 `radicacion` | demanda/poder/solicitud cautelares se GENERAN aquí |
| 2 · Radicación en el juzgado | 2 `radicacionJuzgado` | constancia/radicado/juzgado |
| 3 · Calificación admite/inadmite | 3 `calificacion` | rama; admite decreta cautelares si se pidieron |
| 4 · Subsanación (si inadmite) | 4 `subsanacion` | solo ADJUNTAR (sin modelo fuente) |
| 5 · Notif. cautelares (libra oficios) | 5 `notifCautelares` | **condicional** (`disponibleSi` cautelares) |
| 5/6 · Mandamiento + contestación → audiencia | 6 `mandamientoPago` | rama contesta=Sí → audiencia art. 392 |
| 6 · Impulsos + avalúo/remate | 7 `impulsos` | incluye liquidación (446) y avalúo/remate (444-457) |
| 7 · Acuerdo de pago | 7 `impulsos` → 8 `terminacion` | acuerdo se genera en 7; cierra en 8 (motivo) |
| 8 · Terminación (pago / seguir-rematar) | 8 `terminacion` | "seguir y rematar" NO cierra: pasa por la rama de remate |
| 9 · Desistimiento tácito (art. 317) | 8 `terminacion` | motivo de terminación (sin enforcement de plazo) |

> **Metadata del tipo:** mínima cuantía (hasta 40 SMLMV) ante juez civil municipal
> es de **única instancia** (arts. 17/18 CGP). El seed trae
> jurisdiccion/categoriaSlug/areaSlugs pero no un flag explícito de instancia;
> registrar/dejar nota de "única instancia" para que la UI no ofrezca segunda
> instancia/apelación → ver `decisionesParaUsuario`.

> Próximo paso al aprobar: aplicar D1/D2 (schema + `construirContexto`), agregar los
> campos al `seed-tipos.json` (incluido `disponibleSi` de `notifCautelares` y la
> rama de remate/audiencia), sembrar las 5 plantillas en `plantillas-seed.ts`,
> simular los flujos (con/sin cautelares · contesta/no contesta · seguir-rematar ·
> acuerdo · desistimiento) y verificar generación sin `[[falta:]]` inesperados.