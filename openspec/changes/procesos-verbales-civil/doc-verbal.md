# Proceso Verbal — flujo "como debería ser" (fiel al documento)

Fuente: `openspec/roadmap-docs/JURISDICCIÓN ORDINARIO CIVIL- PROCESO VERBAL.docx`.
Este MD describe el flujo COMPLETO que el documento especifica, para luego **validarlo contra
lo implementado** y actualizar el seed. Notación: `[tipo]` · *(obligatorio)*/*(opcional)* ·
📎 documento · ⏱ plazo · → "habilita" (un campo abre otros).

> Contexto del doc: bajo "Jurisdicción Ordinario – Civil → Proceso o acción judicial" se
> despliega una lista (verbal, verbal sumario, ejecutivo, monitorio, pertenencia, divisorio,
> restitución, rendición de cuentas, reivindicatoria, simulación, nulidad de contrato,
> responsabilidad civil). Este MD es el **Proceso Verbal** (unifica ordinarios, abreviados y
> verbales de mayor/menor cuantía). **Doble instancia.**

## CALIDAD (en qué calidad actúa el cliente)  ← lo que faltaba
Campo `calidad` `[select]` *(obligatorio, al crear)* — **NO es solo demandante/demandado**:
- Demandante · Demandado · Curador ad litem · Tercero interviniente · Litisconsorte ·
  Apoderado sustituto · Apoderado de ambas partes en procesos diferentes.

> Esto es la "calidad procesal" del cliente. Reemplaza/extiende el `rol` actual (que solo tenía
> Demandante/Demandado).

## Fases del proceso
| # | Fase | Etapas |
|---|---|---|
| 1 | **Etapa escrita — Demanda** | Presentación · (Medida cautelar) · Radicado y autoridad |
| 2 | **Calificación** | Estado de la demanda: admisión / inadmisión→subsanación 5d / rechazo→recurso |
| 3 | **Traslado y respuesta** | Traslado 20d · Reconvención · Contestación · Excepciones de mérito 5d |
| 4 | **Etapa oral** | Audiencia inicial (art. 372) · Audiencia de instrucción y juzgamiento (art. 373) |
| 5 | **Sentencia** | Sentencia (oral/escrita) + costas |
| 6 | **Recursos / 2ª instancia** | Recurso (apelación→2ª instancia / otros→mismo despacho) |
| 7 | **Ejecutoria** | Estado final: ejecutoriado / cumplido / archivado |

## Grafo
```
0) ELIGE TIPO → "Proceso verbal" · CALIDAD (demandante/demandado/curador/tercero/litisconsorte/apoderado…)

FASE 1 · DEMANDA (etapa escrita)
 ① PRESENTACIÓN DE LA DEMANDA
    📎 demanda.pdf · pruebas.pdf · anexos.pdf
    DEMANDANTE: nombre · cédula · dirección · correo · teléfono
    DEMANDADO:  nombre · cédula · dirección · correo · teléfono
    Unidad de medida [SMMLV / Pesos] · Cuantía [Mínima/Menor/Mayor/N-A]
    Pretensión [DETERMINADAS → monto pretensiones + monto total / INDETERMINADAS → (sin montos)]
    Síntesis · Fecha de presentación · Medio de radicación [ventanilla/correo/plataforma/otro] · 📎 soporte-radicacion
 ②  ¿SOLICITA MEDIDA CAUTELAR? [Sí/No]
        └ Sí → MÓDULO MEDIDAS CAUTELARES (ver abajo)
 ③ RADICADO Y AUTORIDAD: radicado · juzgado/corporación

FASE 2 · CALIFICACIÓN
 ④ ESTADO DE LA DEMANDA [Admitida / Inadmitida / Rechazada]
     ├ ADMITIDA → fecha auto · fecha notif. por estado · 📎 auto
     ├ INADMITIDA → fecha auto · notif · 📎 auto · ⏱ Fecha límite subsanar (5 días desde notif)
     │     ¿Subsanación presentada? [Sí/No] → Sí: fecha · 📎 escrito-subsanacion · 📎 copia-envio
     │     Decisión del juzgado [ADMISIÓN / RECHAZO]
     │        ├ ADMISIÓN → 📎 auto-admision · fecha admisión · fecha notif.
     │        └ RECHAZO → 📎 auto-rechazo · fecha · notif · Recurso [Sí/No/N-A] → decisión [Fav/Desfav] · 📎 decisión-recurso
     └ RECHAZADA → fecha auto · notif · 📎 auto · Recurso [Sí/No]
            └ Sí → [Apelación / Reposición] · fecha recurso · 📎 auto-recurso · decisión [Fav/Desfav] · observaciones

FASE 3 · TRASLADO Y RESPUESTA
 ⑤ TRASLADO: ¿demandado notificado? · fecha notif · 📎 soporte · fecha inicio/fin traslado ⏱ 20 días · estado [en término/vencido/contestado]
 ⑥ ¿RECONVENCIÓN? [Sí/No]
        └ Sí → pretensiones · fecha · 📎 demanda-reconvencion · ¿contestación? Sí→📎+fecha · Decisión juez [Admitir/Rechazar] → fecha + 📎 auto
 ⑦ CONTESTACIÓN: ¿contestó? [Sí/No] · fecha · 📎 contestacion · 📎 pruebas · 📎 anexos · ¿contestó dentro del término? (auto vs fin traslado)
 ⑧ EXCEPCIONES DE MÉRITO: ¿hay traslado? [Sí/No]
        └ Sí → 📎 escrito-excepciones · fecha inicio/fin ⏱ 5 días · ¿demandante se pronunció? → 📎 + fecha · ¿pruebas adicionales? · 📎 soporte

FASE 4 · ETAPA ORAL
 ⑨ AUDIENCIA INICIAL (art. 372)
    fecha auto que fija · 📎 auto · fecha/hora · estado [programada/realizada/aplazada/suspendida]
    asiste demandante/demandado · apoderados [casillas]
    excepciones previas resueltas [Sí/No/N-A] → resultado
    Conciliación [Total/Parcial/Fallida/N-A] → Total/Parcial: ¿cuál fue?
    interrogatorio de partes · fijó litigio · hechos aceptados · hechos objeto de prueba
    control de legalidad · saneamiento → descripción
    decretó pruebas → [documentales/testimoniales/interrogatorio/pericial/inspección/oficios/otras] · pruebas negadas
    ¿sentencia inmediata? [Sí/No] → Sí: 📎 sentencia · sentido [Fav/Desfav/Parcial]
    📎 acta-audiencia-inicial · grabación URL · observaciones
 ⑩ AUDIENCIA DE INSTRUCCIÓN Y JUZGAMIENTO (art. 373)
    fecha/hora · 📎 auto · estado · pruebas practicadas [casillas]
    testigos (tabla: nombre/parte/asistió) · peritos (tabla) · documentos exhibidos · pruebas pendientes → descripción
    alegatos [Sí/No] → alegato demandante [texto/PDF] · alegato demandado [texto/PDF]
    ¿sentencia oral? [Sí/No] · ¿anunció sentido? → [Concede/Niega/Parcial/Inhibitorio]
    sentencia escrita pendiente → ⏱ 10 días · fecha sentencia escrita · 📎 acta · grabación URL

FASE 5 · SENTENCIA
 ⑪ SENTENCIA: fecha · tipo [Oral/Escrita] · 📎 sentencia · resultado [Fav/Desfav/Parcial/Inhibitorio]
    ¿condena en costas? → valor · obligaciones impuestas · fecha notificación

FASE 6 · RECURSOS / 2ª INSTANCIA
 ⑫ ¿RECURSO INTERPUESTO? [Sí/No]
     ├ No → FASE 7 (ejecutoria)
     └ Sí → tipo [Apelación / Aclaración / Corrección / Adición / Reposición] · fecha · 📎 escrito · obs
          ├ NO es apelación → lo resuelve el mismo despacho: fecha auto · decisión [concede/niega/aclara/corrige/adiciona/repone/no repone] · 📎 providencia · notif · ¿ejecutoriado?
          └ APELACIÓN → ¿conoce el superior? · ¿concedido? · efecto [suspensivo/devolutivo/diferido] · fecha remisión
               └ SEGUNDA INSTANCIA: despacho · reparto · ponente · admisión · traslado alegatos · 📎 alegatos
                  · fecha sentencia 2ª · 📎 sentencia-2inst · resultado [Confirma/Revoca/Modifica/Nulidad] · notif · ejecutoria

FASE 7 · EJECUTORIA → Estado final [Ejecutoriado / Cumplido / Archivado]
```

## Campos que HABILITAN otros (condicionales clave)
- **Pretensión = DETERMINADAS** → abre `monto pretensiones` + `monto total`. INDETERMINADAS → no abre.
- **¿Solicita medida cautelar? = Sí** → abre el **módulo Medidas Cautelares** completo.
- **Estado = Inadmitida** → abre subsanación (⏱5 días) → Decisión del juzgado → admisión/rechazo→recurso.
- **Estado = Rechazada** → abre recurso (apelación/reposición) → decisión.
- **¿Reconvención? = Sí** → pretensiones + demanda PDF + decisión del juez.
- **¿Excepciones de mérito? = Sí** → traslado 5 días + pronunciamiento del demandante.
- **¿Sentencia inmediata? = Sí** (en audiencia inicial) → 📎 sentencia + sentido (cierra sin audiencia de instrucción).
- **¿Sentencia oral? = No** → sentencia escrita pendiente (⏱10 días).
- **Recurso = Apelación** → módulo **Segunda Instancia** (solo visible si apelación + conoce el superior).

## MÓDULO MEDIDAS CAUTELARES (sub-flujo, si se solicita)
1. **Solicitud:** solicitante [Demandante/Demandado(excep.)/Reconvención] · 📎 escrito-solicitud · fecha.
2. **Tipo de medida** [múltiple: inscripción de demanda / embargo / secuestro / suspensión de obra / suspensión de actos / innominada / otra] · bien o derecho afectado · valor estimado (COP) · observaciones.
3. **Decisión del despacho:** ¿decretada? [Sí/No/Parcial] · fecha auto · 📎 auto-medida · ¿requiere caución? → valor · ¿constituida? → fecha.
4. **Ejecución:** ¿practicada? · fecha · entidad oficiada (ORIP/banco/tránsito) · resultado [exitosa/parcial/fallida/pendiente] · 📎 soporte.
5. **Levantamiento:** ¿levantada? · fecha · motivo [sentencia/desistimiento/caución/orden judicial/otro] · 📎 auto-levantamiento.

## Plazos (del doc)
- Subsanación: **5 días** desde notificación.
- Traslado de la demanda: **20 días**.
- Traslado de excepciones de mérito: **5 días**.
- Sentencia escrita (tras anuncio del sentido): **10 días**.
