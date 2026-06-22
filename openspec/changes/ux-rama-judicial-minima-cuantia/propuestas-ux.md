# Propuestas de mejora UI/UX — mínima cuantía + Rama Judicial

Cada propuesta: **problema** → **propuesta** → **valor / esfuerzo** → **qué la habilita** (API/back).
Bocetos en ASCII. Al final: matriz de prioridad + roadmap por fases. **Nada implementado.**

---

## A. Visibilidad de novedades (el gap #1)

### P1 — Señal de novedades en la LISTA de procesos · ⭐⭐⭐ alto / esfuerzo medio
**Problema (gap A):** el abogado no sabe qué procesos tienen actuaciones nuevas sin abrir cada ficha.
**Propuesta:** columna/píldora "novedades" en la tabla + filtro "Con novedades" + un contador global
en el header ("3 procesos con novedades del juzgado").
```
 Proceso                         Cliente     Etapa          Vence       Novedades
 Ejecutivo mín. — X vs Y         Finova      Mandamiento    12-jul 🟡   🟢 2 nuevas
 Rad. 660014003002202600704      …                                      ────────────
 Ejecutivo mín. — A vs B         …           Audiencia      —           ·
```
**Habilita:** ya existe `Proceso.actuacionesVistasAt` y `ActuacionProceso.createdAt` → la lista puede
traer `count(createdAt > vistasAt)` por proceso (un campo derivado en el endpoint de lista). Sin API
nueva de la Rama (usa lo ya sincronizado).

### P2 — "Centro de novedades" / cockpit del día · ⭐⭐ medio / medio
**Propuesta:** una vista "Para hoy" (al estilo del cockpit comercial) que liste **novedades del juzgado
sin leer** + vencimientos próximos, accionable. Reusa el patrón [[comercial-seguimiento-accionable]].

---

## B. Distinguir las dos líneas de tiempo (gap L/B)

### P3 — Reetiquetar y separar visualmente "despacho" vs "juzgado" · ⭐⭐⭐ alto / esfuerzo BAJO
**Problema:** el stepper de **etapas internas** y el panel de **actuaciones del juzgado** se ven igual.
**Propuesta (solo copy + estilo):**
- Stepper → encabezado "**Avance en el despacho** (lo que gestionas tú)".
- Panel Rama → "**Lo que publica el juzgado** (Rama Judicial)" con un acento de color/ícono distinto
  (p. ej. 🏛️) para que se lea como "fuente externa".
- Microcopy de una línea explicando la diferencia.
**Valor:** elimina la confusión conceptual sin tocar lógica.

### P4 — Conectar actuación → etapa en el propio timeline · ⭐⭐ medio / medio
**Propuesta:** llevar las "Sugerencias de la Rama" al lado de la actuación que las dispara: en la
actuación "LIBRA MANDAMIENTO DE PAGO", inline → "↳ ¿avanzar a *Mandamiento de pago*? [Usar fecha]".
Así el abogado ve causa (actuación) y efecto (etapa) juntos. (Hoy las sugerencias van en una card aparte.)

---

## C. Frescura y confianza (gap C/M + validación legal)

### P5 — Indicador de frescura ("última sync / última actuación") · ⭐⭐⭐ alto / esfuerzo BAJO
**Problema:** no se sabe qué tan al día está la info.
**Propuesta:** bajo el botón "Actualizar": "Sincronizado hace 2 h · última actuación 17-jun".
```
 Actuaciones del juzgado 🏛️                      [ Actualizar ↻ ]
 Sincronizado hace 2 h · última actuación: 17-jun-2026
```
**Habilita:** guardar un `Proceso.actuacionesSyncAt` (timestamp del último sync). Pequeño campo nuevo.

### P6 — Estados persistentes "reservado / no publicado" en el header · ⭐⭐ medio / bajo
**Problema (gap M):** "reservado" solo aparece tras "Actualizar".
**Propuesta:** badge fijo en el header del proceso: `🔒 Reservado en la Rama` o `⏳ Aún no publicado`
(con tooltip: "puede tardar días en aparecer"). Persistente.

### P7 — Disclaimer de confianza · ⭐⭐ medio / esfuerzo BAJO
**Propuesta:** nota discreta al pie del panel: *"La información de la Rama no es en tiempo real y
algunos juzgados publican con retraso. Para términos y decisiones críticas, verifica con el juzgado."*
(Fundamentado en [[rama-judicial-actuaciones]] validación-ley-y-realidad, B2/B4/B5.)

### P8 — Origen de cada dato autollenado · ⭐ bajo / bajo
**Propuesta (gap N):** junto a juzgado/fecha: etiqueta `de la Rama` (o `manual`), para saber qué pisó qué.

---

## D. Aprovechar la superficie completa de la API (alto valor)

### P9 — IMPORTAR los documentos del expediente (PDF reales) · ⭐⭐⭐ alto / esfuerzo ALTO
**Problema (gap K):** no se pueden traer los documentos que publica el juzgado.
**Propuesta:** botón "Traer documentos del juzgado" → lista (Endpoint *Documentos*) con descripción y
fecha → descargar (Endpoint *Descarga* → PDF) y guardarlos como `DocumentoProceso` (tecnovapp). En el
timeline, las actuaciones con `conDocumentos` muestran 📎 y permiten abrir/guardar su PDF.
```
 09-mar  RECIBE MEMORIALES ONLINE                         📎 1 doc
         ↳ Certificación bancaria parte demandante   [ ver PDF ] [ guardar al proceso ]
```
**Habilita:** Endpoints E/F (verificados: PDF 200). **Depende de** [[documental-storage]] y de respetar
el §4 anti-bloqueo (cada doc = 1 request). Es la mejora de **mayor impacto** funcional.

### P10 — Autopoblar Partes desde Sujetos · ⭐⭐ medio / medio
**Propuesta:** al validar el radicado, ofrecer "Importar partes del juzgado": Demandante/Demandado con
identificación (Endpoint *Sujetos*), para crear/cotejar las `ParteProceso`. No pisa lo existente: sugiere.

### P11 — Card "Estado oficial en el juzgado" (Detalle) · ⭐⭐ medio / medio
**Propuesta:** un bloque compacto con datos vivos del Endpoint *Detalle*: **ubicación** ("Secretaría"),
tipo/clase, ponente, última actualización. Es el "snapshot" del expediente oficial.
```
 🏛️ Estado en el juzgado            (sincronizado hace 2 h)
 Juzgado: 002 Civil Municipal de Pereira   ·   Ubicación: Secretaría
 Tipo: Ejecutivo · Mínima cuantía           ·   Últ. actualización Rama: 17-jun
```

---

## E. Flujo del radicado (gap D/I)

### P12 — Validación en vivo + preview antes de vincular · ⭐⭐ medio / medio
**Propuesta:** al teclear 23 dígitos (debounced) consultar la Rama y mostrar un **preview** para
confirmar antes de vincular:
```
 Radicado [ 6600140030022026007040… ]  ✓ 23 dígitos
 ┌ Encontrado en la Rama ─────────────────────────────┐
 │ JUZGADO 002 CIVIL MUNICIPAL DE PEREIRA · radicó 04-jun │
 │ Demandante: FINOVA SAS · Demandado: ELDER … │
 │           [ Vincular y traer datos ]                │
 └─────────────────────────────────────────────────────┘
```
Evita vincular un radicado equivocado y hace el autollenado **explícito** (el usuario confirma).

### P13 — Contador más visible + feedback de sync persistente · ⭐ bajo / esfuerzo BAJO
**Propuesta (gap D):** subir el tamaño del contador (de `xs` a `sm`), y que el resultado del sync
("✓ Juzgado y fecha autocompletados a las 14:08") **no desaparezca**: quede como nota hasta el próximo cambio.

---

## F. UX específica del ejecutivo (gap H/E)

### P14 — Mínima cuantía: cuantía implícita · ⭐ bajo / bajo
**Propuesta (gap H):** para este tipo, preseleccionar `cuantía = MINIMA` y mostrar nota
"Mínima cuantía (≤ 40 SMLMV · única instancia)" en vez de pedir elegir. (Coherente con la validación legal.)

### P15 — Documentos: separar "del juicio" vs "pruebas" · ⭐ bajo / bajo
**Propuesta (gap E):** agrupar visualmente Documentos obligatorios del juicio (demanda/poder) vs
Pruebas anexas (nombre libre) vs Documentos del juzgado (importados, P9), cada grupo con su rótulo.

---

## G. Productividad transversal

### P16 — "Actualizar todos mis procesos" (disparo manual del barrido) · ⭐⭐ medio / bajo
**Propuesta:** botón en la lista para correr el sync masivo on-demand (además del cron), con resumen
("12 procesos · 3 con novedades"). Reusa `sincronizarTodas` ya existente (acotado a los del usuario).

### P17 — Campanita in-app de novedades · ⭐⭐ medio / alto
Ya está como follow-up en [[rama-judicial-actuaciones]] (necesita modelo Notificacion + topbar). La
señal "no leídas" por proceso ya existe (#3 de ese change); esto la sube al nivel global.

---

## Matriz de prioridad (impacto × esfuerzo)

| Prioridad | Propuestas | Por qué |
|---|---|---|
| **Quick wins** (alto/bajo) | P3 (separar líneas), P5 (frescura), P7 (disclaimer), P13 (contador/feedback), P14 (cuantía), P8 (origen) | Mucho valor de claridad por poco esfuerzo; casi todo copy/estilo + 1 campo de fecha |
| **Apuestas de impacto** (alto/alto) | **P1 (novedades en la lista)**, **P9 (importar documentos PDF)** | Cierran los dos gaps más fuertes (visibilidad y aprovechar la API) |
| **Mejoras medias** | P11 (Detalle), P10 (Sujetos→partes), P12 (preview radicado), P4 (actuación→etapa), P6 (estados), P16 (actualizar todos) | Buen valor, esfuerzo medio; varias dependen de exponer más de la API |
| **Cuando haya base** | P2 (cockpit), P17 (campanita), P15 (docs agrupados) | Dependen de in-app notifs / del importador de documentos |

## Roadmap por fases (propuesto)

- **Fase 1 — Claridad (quick wins):** P3 + P5 + P7 + P13 + P14 + P8. Casi todo front, bajo riesgo. Hace
  que lo ya construido se **entienda y se confíe**.
- **Fase 2 — Visibilidad:** P1 (novedades en la lista) + P16 (actualizar todos) + P6 (estados). El
  abogado deja de "entrar a adivinar".
- **Fase 3 — Aprovechar la API:** P9 (documentos PDF) + P11 (Detalle) + P10 (Sujetos) + P12 (preview).
  Sube el techo funcional; toca backend (más endpoints CPNU + storage).
- **Fase 4 — Push proactivo:** P2 (cockpit) + P17 (campanita) + P4 (actuación→etapa) + P15.

> Cada fase/propuesta, al aprobarse, sería su propio change (con su gate). Este documento solo
> identifica y prioriza; no implementa nada.
