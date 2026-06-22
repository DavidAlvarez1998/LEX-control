# Validación — documentos vs. ley (CGP) vs. práctica real

> Encargo del usuario: validar lo ya implementado (ejecutivo de mínima cuantía) y el flujo de la
> integración de actuaciones contra (1) los documentos/seed, (2) la **ley** (CGP, Ley 1564/2012) y
> (3) la **práctica real**. Donde la ley/realidad discrepe de los documentos, **se reporta** — pero
> la decisión del usuario es **seguir los documentos**. Aquí: ✅ confirmado · ⚠️ matiz/ajuste ·
> ❌ error. Investigación con fuentes (ver §fuentes).

## Resumen ejecutivo

- El flujo del ejecutivo es **jurídicamente sólido en lo esencial** (instancia, competencia, título,
  ruta de excepciones, cautelares, liquidación, remate, terminación). ✅
- Hay **2 errores fácticos de plazo/cita que conviene corregir** aunque "sigamos los documentos",
  porque el propio documento citó mal la ley: **(a)** el mandamiento ordena pagar en **5 días**
  (art. 431), no 10 — los 10 días son para **excepciones** (art. 442); **(b)** la cuantía de
  mínima (40 SMLMV) está en el **art. 25**, no en el 18.
- La **práctica real CPNU confirma el diseño de la integración** (títulos de actuación = texto
  libre → matching difuso; no es fuente legal única → automatización asistida). Pero añade **riesgos
  operativos reales** a manejar (latencia de días, cobertura incompleta, procesos reservados).

---

## Parte A — Ejecutivo de mínima cuantía (lo ya implementado) vs. ley

| # | Lo que dice nuestro doc | Veredicto | Ley | Resolución |
|---|---|---|---|---|
| A1 | Mínima cuantía (≤40 SMLMV) → juez civil municipal, **única instancia** (arts. 17 y 18) | ✅ con cita a corregir | Única instancia = **art. 17**; los 40 SMLMV = **art. 25** (no 18) | Corregir cita "17 y **25**". Sustancia OK. |
| A2 | Ejecutivo: obligación clara, expresa y exigible; arts. 422, 430 ss. | ✅ | Arts. 422 + 430 | Sin cambios. |
| A3 | Con excepciones, en mínima cuantía se resuelve en la **audiencia única del art. 392** (esquema verbal sumario) | ✅ legalmente correcto | Remisión expresa del **art. 443.2** → audiencia del **art. 392** en mínima cuantía | Mejorar redacción: NO es que el ejecutivo "se convierta" en verbal sumario; el proceso sigue siendo ejecutivo y solo la fase de excepciones va a la audiencia del 392. |
| A4 | Excepciones: **10 días hábiles** desde notificación del mandamiento | ✅ | **Art. 442** (10 días) + **art. 118** (días = hábiles) | Sin cambios. |
| A5 | Inadmisión → **5 días hábiles** para subsanar | ✅ con cita a afinar | **Art. 90** (no el 85) | Confirmar que el seed/plazo apunta al art. 90. |
| A6 | "Mandamiento de pago: plazo **10 días hábiles**" | ❌/⚠️ **mezcla dos plazos** | Mandamiento ordena **pagar en 5 días** (**art. 431**); los **10 días** son para **excepciones** (**art. 442**) | **Corregir/separar:** plazo de pago = 5 días; plazo de excepciones = 10 días. Si la UI muestra "10 días" como plazo del mandamiento para pagar, está mal. |
| A7 | Cautelares del ejecutivo: **art. 599 y ss.** | ✅ | Núcleo **art. 599**; régimen general (formas de embargo, inscripción de la demanda) en **588/591/593** | "y ss." salva la cita; la inscripción de la demanda vive en el 593. |
| A8 | El modelo de cautelares cita **CPC art. 531** (conservado "literal/fiel al doc", decisión #6) | ⚠️ obsoleto **a propósito** | CPC **derogado** por el CGP (art. 626/627); hoy sería **art. 599 CGP** | **Decisión consciente del usuario** (fidelidad al modelo). Se reporta: jurídicamente la cita correcta hoy es art. 599 CGP. Seguimos el documento salvo que decidas modernizar la cita. |
| A9 | Liquidación del crédito = **art. 446** | ✅ | Art. 446 | Sin cambios. |
| A10 | Avalúo y remate = **arts. 444–457** | ⚠️ rango corto | Avalúo **444–447**; remate y pago **448–461** (incluye terminación por pago, **art. 461**) | Ampliar a "444–461" para que el remate quede completo. Menor. |
| A11 | Desistimiento tácito = **art. 317** (requerimiento + 30 días); v1 **sin enforcement** | ⚠️ incompleto pero **decidido** | Art. 317 tiene 2 causales: subjetiva (requerimiento + **30 días**) y objetiva (**1 año**, o **2 años** si ya hay sentencia/seguir-adelante) | Nuestro doc **decidió no enforzar plazos** en v1 → OK. Se reporta la causal objetiva (1/2 años) por si se enforza luego. |
| A12 | Terminación: "seguir adelante la ejecución" **NO cierra** (sigue a liquidación→avalúo→remate→pago) | ✅ | Auto/sentencia de seguir adelante (440/443) → ejecución forzada → **terminación por pago art. 461** | Cita fina: 461 = terminación por pago; entrega de dinero al ejecutante = art. 447. |
| A13 | **Omisión:** contra el mandamiento procede **recurso de reposición (3 días)**, no modelado | ⚠️ falta | Reposición 3 días, independiente de las excepciones (10 días) | No está en el flujo. Decisión: ¿se modela o se deja fuera de alcance? (Hoy fuera.) |

## Parte B — Integración de actuaciones vs. práctica real (CPNU)

| # | Supuesto del diseño | Veredicto | Realidad | Impacto en el diseño |
|---|---|---|---|---|
| B1 | Radicado = **23 dígitos** asignado por el juzgado al repartir | ✅ con matiz | Estructura oficial: **DANE(5)** + corporación(2) + especialidad(2) + despacho(3) + año(4) + consecutivo(5) + recurso(2). NO asumir split 2+3 dpto/ciudad | Tratar el radicado como **string de 23 dígitos** (ceros a la izquierda), validar longitud y que sea numérico. |
| B2 | El radicado existe **tras radicar/repartir** | ✅ con riesgo | **Latencia real de días** entre reparto y aparición/actuaciones en la consulta; NO es tiempo real | No marcar "sin novedad" por una sola consulta; **polling** periódico; el radicado puede no ser consultable apenas se radica. |
| B3 | Actuaciones = **fecha · actuación · anotación** | ✅ confirmado | Estructura real confirmada (documento real de estado). Títulos = **texto libre**, varían por despacho | **Valida nuestro §3a**: detección de hitos por **keywords normalizadas**, NUNCA igualdad exacta de títulos. |
| B4 | Los ejecutivos de mínima cuantía civil municipal **aparecen** en CPNU | ⚠️ no universal | **No todos los despachos publican** (municipales pequeños); hay **procesos reservados/privados** que ocultan actuaciones | Distinguir 3 estados: **encontrado** / **no publicado-no encontrado** / **reservado**. No garantizar cobertura 100%. |
| B5 | La info de actuaciones es confiable | ⚠️ | No es tiempo real; puede tener **omisiones/errores**; "no es fuente única de verdad legal" | **Valida nuestra decisión "asistida, no autónoma"**: no automatizar decisiones legales irreversibles solo con CPNU. |
| B6 | (transporte) endpoint estable | ⚠️ riesgo | No hay **API contractual oficial** documentada; sin SLA, puede cambiar/rate-limitar (puerto 448, User-Agent, 403/429) | Diseñar como integración **frágil**: reintentos con backoff, caché, tolerancia a cambios de esquema (ya en `specs/rama-judicial/spec.md`). |
| B7 | Sync idempotente por clave natural | ✅ con cuidado | Las actuaciones pueden ser **editadas/reordenadas retroactivamente** por el despacho | Clave estable `(procesoId, fechaActuacion, actuacion, anotacion)`/hash; contemplar correcciones retroactivas. |

## Conclusión y decisión

**Seguimos los documentos** (instrucción del usuario). El flujo es legalmente sólido. Se **reportan**
las discrepancias; de ellas, el equipo decide cuáles ajustar:

- **Recomendado corregir** (errores fácticos de la propia ley citada, baratos): **A6** (mandamiento
  paga en 5 días; 10 días = excepciones) y **A1** (cita art. 25, no 18). Opcional **A10** (remate
  hasta 461).
- **Decisiones conscientes que se mantienen** (fidelidad al documento): **A8** (cita CPC art. 531),
  **A11** (desistimiento sin enforcement). Se dejan como están salvo orden contraria.
- **La práctica real CONFIRMA el diseño de la integración** (B3, B5) y añade **requisitos operativos**
  a incorporar en la implementación: estados encontrado/no-publicado/reservado (B4), latencia y
  polling (B2), radicado como string (B1), transporte frágil con reintentos (B6), idempotencia con
  correcciones retroactivas (B7).

## Fuentes

CGP (texto oficial): [Secretaría del Senado — Ley 1564/2012](http://www.secretariasenado.gov.co/senado/basedoc/ley_1564_2012.html) ·
[U. Externado — Depto. Derecho Procesal (arts. 90, 118, 317, 442, 443, 444, 461)](https://procesal.uexternado.edu.co/) ·
arts. 422/430/431/440/446/448/455/461/599 en leyes.co.
Práctica CPNU: [Manual CPNU — composición del radicado](https://consultaprocesos.ramajudicial.gov.co/manual/numRadicacion.html) ·
[FAQ CPNU — Rama Judicial](https://www.ramajudicial.gov.co/pregunta-cpnu) ·
[Documento real de actuaciones/estado (PDF Rama)](https://publicacionesprocesales.ramajudicial.gov.co/documents/6098902/66599926/ESTADO181.pdf) ·
[Código Único del Proceso (23 dígitos) — Trib. Sup. Cúcuta](https://tribunalsuperiordecucuta.gov.co/2018/11/26/codigo-unico-del-proceso-judicial-23-digitos/).
