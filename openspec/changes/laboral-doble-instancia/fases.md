# Fases del Proceso Laboral — contexto "perfecto" (fiel al doc)

Fuente: `openspec/roadmap-docs/PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx`.

Este documento es el **contexto de referencia**: define cómo debe quedar el flujo, organizado
en **fases** de alto nivel. Las fases son el esqueleto común a los 4 casos y la base del
**panel visual** (stepper agrupado): cada fase es un grupo del stepper; dentro, las etapas y
sus campos (detalle en `flujos-4-casos.md` y `design.md`). Las etapas conservan el orden y las
ramas del doc; las fases solo **agrupan** para lectura y navegación, no cambian la lógica.

## Las 6 fases

| # | Fase | Qué abarca (etapas) | Sentido procesal |
|---|---|---|---|
| **1** | **Demanda y admisión** | Presentación/radicación · (demandante) Calificación → Subsanación → Recurso de rechazo · (demandado·doble) Registro de admisión · ¿Retiro art. 67? | Se presenta/recibe la demanda y el juez la califica. |
| **2** | **Traslado y contestación** | Traslado y notificación (⏱10 días háb.) · Contestación (¿contestaron? · reforma · reconvención + su sub-flujo) | Se notifica y corre el término para contestar. |
| **3** | **Audiencias** | Preparación de la audiencia · Citación · Audiencia única **o** Audiencia art. 77 + Audiencia art. 80 | Conciliación, saneamiento, pruebas y juzgamiento. |
| **4** | **Sentencia y recurso** | Sentencia (fecha + PDF + decisión) · Recurso: **reposición** (única) / **apelación** (doble) | Fallo de 1ª instancia y su impugnación. |
| **5** | **Segunda instancia** *(solo doble, si la apelación se concede)* | Remisión al Tribunal · Sustentación · Audiencia de 2ª instancia · Sentencia de 2ª instancia (CONFIRMA/REVOCA/MODIFICA) | Conoce el Tribunal Superior (Sala Laboral). |
| **6** | **Terminación / archivo** | Terminación (ejecutoriada) · Archivo (retiro art. 67 · rechazo · conciliación) | Cierre del proceso. |

> Orden interno dentro de cada fase: **única** → Citación antes que Preparación; **doble** →
> Preparación antes que Citación (corrección del doc).

## Qué fases tiene cada caso

| Fase | Demandante·Única | Demandante·Doble | Demandado·Única | Demandado·Doble |
|---|---|---|---|---|
| 1 Demanda y admisión | ✅ calificación completa | ✅ calificación completa | ⚠️ sin calificación (solo retiro) | ✅ solo registro de admisión |
| 2 Traslado y contestación | ⚠️ solo traslado (sin contestación explícita) | ✅ completa | ⚠️ traslado + reforma | ✅ completa |
| 3 Audiencias | 1 audiencia | art. 77 + art. 80 | 1 audiencia | art. 77 + art. 80 |
| 4 Sentencia y recurso | reposición | apelación | reposición | apelación |
| 5 Segunda instancia | — | ✅ | — | ✅ |
| 6 Terminación / archivo | ✅ | ✅ | ✅ | ✅ |

Leyenda: ✅ presente · ⚠️ presente parcial (fiel al doc) · — no aplica.

## Mapeo fase → etapas (keys del seed)

- **Fase 1:** `presentacion` · `admision` · `subsanacion` · `recurso_rechazo` · `archivado_rechazo` · `retiro` · `archivado`
- **Fase 2:** `traslado` · `contestacion`
- **Fase 3:** `preparacionAudiencia(_doble)` · `citacionAudiencia(_doble)` · `audienciaUnica` · `audienciaArt77` · `audienciaArt80`
- **Fase 4:** `recurso`
- **Fase 5:** `remision2inst` · `sustentacion2inst` · `audiencia2inst` · `sentencia2inst`
- **Fase 6:** `terminada` (y los terminales de archivo de la Fase 1)

## Implicación para el panel visual (mejora propuesta, opcional)

Cada `EtapaDef` llevaría una etiqueta `fase` (1–6). El stepper agruparía las etapas por fase
(cabecera de fase + etapas dentro), mostrando solo las fases aplicables al caso (según la tabla
de arriba) y resaltando la fase actual. **No** es requisito para corregir el flujo; es la capa
de presentación que el documento habilita. Si se aprueba, se añade `fase` al esquema de etapas
en `tramite-catalog` y el render en `datos-proceso.tsx` / la ficha laboral.
