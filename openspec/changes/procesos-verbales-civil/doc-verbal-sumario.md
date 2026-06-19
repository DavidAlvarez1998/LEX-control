# Proceso Verbal Sumario — flujo "como debería ser" (fiel al documento)

Fuente: `openspec/roadmap-docs/JURISDICCIÓN ORDINARIO CIVIL- PROCESO VERBAL SUMARIO.docx`.
Misma convención que `doc-verbal.md`. **Única instancia** (Unifica declarativos especiales y
monitorios). Es muy parecido al verbal, con estas diferencias clave marcadas con ⭐.

## CALIDAD (igual que el verbal)
`calidad` `[select]` *(obligatorio)*: Demandante · Demandado · Curador ad litem · Tercero
interviniente · Litisconsorte · Apoderado sustituto · Apoderado de ambas partes en procesos diferentes.

## Fases
| # | Fase | Etapas |
|---|---|---|
| 1 | **Demanda** | Presentación (verbal/escrita) · (Medida cautelar) · Radicado y autoridad |
| 2 | **Calificación** | Estado: admisión / inadmisión→subsanación 5d / rechazo→recurso · ⭐ reposición vs auto admisorio |
| 3 | **Traslado y respuesta** | Traslado ⭐10d · Reconvención · Contestación |
| 4 | **Resolución** | ⭐ Sentencia anticipada (sin audiencia) **o** Audiencia única (art. 392) |
| 5 | **Sentencia** | Sentencia + costas |
| 6 | **Ejecutoria** | Estado final (⭐ sin 2ª instancia — única instancia) |

## Grafo
```
0) ELIGE TIPO → "Proceso verbal sumario" · CALIDAD (7 opciones)

FASE 1 · DEMANDA
 ① PRESENTACIÓN
    ⭐ DEMANDA [VERBAL / ESCRITA] → ESCRITA: 📎 demanda.pdf · pruebas.pdf · anexos.pdf
    DEMANDANTE: nombre · cédula · dirección · correo · celular
    DEMANDADO:  nombre · cédula · dirección · correo · celular
    Unidad de medida [SMMLV/Pesos] · Cuantía [Mínima/Menor/Mayor/N-A]
    Pretensión [DETERMINADAS→montos / INDETERMINADAS] · Síntesis
    ⭐ ¿ES MÍNIMA CUANTÍA? [Sí/No]
    Fecha de presentación · Medio de radicación [ventanilla/correo/plataforma/otro] · 📎 soporte-radicacion
 ② ¿SOLICITA MEDIDA CAUTELAR? [Sí/No] → Sí: MÓDULO MEDIDAS CAUTELARES (idéntico al verbal)
 ③ RADICADO Y AUTORIDAD: radicado · juzgado/corporación · ⭐ correo del juzgado

FASE 2 · CALIFICACIÓN
 ④ ESTADO DE LA DEMANDA [Admitida / Inadmitida / Rechazada]
     ├ ADMITIDA → fecha auto · fecha notif. por estado · 📎 auto
     ├ INADMITIDA → fecha auto · notif · 📎 auto · ⏱ subsanar 5 días desde notif
     │     ¿Subsanación? [Sí/No] → fecha · 📎 escrito-subsanacion · 📎 copia-envio
     │     Decisión del juzgado [ADMISIÓN/RECHAZO] → admisión (📎+fechas) / rechazo (📎+recurso Fav/Desfav+📎)
     └ RECHAZADA → fecha auto · notif · 📎 auto · Recurso [Sí/No] → [Apelación/Reposición] · fecha · 📎 · decisión [Fav/Desfav] · obs
 ⭐ ¿REPOSICIÓN CONTRA EL AUTO ADMISORIO? [Sí/No] → Sí: fecha · 📎 recurso-reposicion · observaciones

FASE 3 · TRASLADO Y RESPUESTA
 ⑤ TRASLADO: ¿notificado? · fecha · 📎 soporte · inicio/fin ⏱ 10 días · estado
 ⑥ ¿RECONVENCIÓN? [Sí/No] → Sí: pretensiones · fecha · 📎 demanda-reconvencion · ¿contestación? Sí→📎+fecha · Decisión juez [Admitir/Rechazar] → fecha + 📎
 ⑦ CONTESTACIÓN: ¿contestó? [Sí/No] · fecha · 📎 contestacion · 📎 pruebas · 📎 anexos · ¿dentro del término?

FASE 4 · RESOLUCIÓN
 ⑧ ⭐ ¿PROCEDE SENTENCIA ANTICIPADA (sin audiencia)? [Sí/No]
     ├ Sí → SENTENCIA ESCRITA: fecha · tipo=Escrita · resultado [Fav/Desfav/Parcial/Inhibitorio] · ¿costas?→valor · 📎 sentencia · notif · ejecutoria · estado final
     └ No → habilita AUDIENCIA ÚNICA ▼
 ⑨ AUDIENCIA ÚNICA (art. 392)
    fecha auto fija · fecha/hora · estado [programada/realizada/aplazada/suspendida] (registrar reprogramaciones) · 📎 acta · grabación URL
    Conciliación [Total/Parcial/Fallida] · 📎 acta-conciliacion · obs
    Interrogatorio: ¿se practicó? → 📎 interrogatorio · obs
    Pruebas decretadas [documentales/testimoniales/interrogatorio/inspección/pericial] · n.º testigos demandante/demandado · ¿se practicaron todas? · obs
    Alegatos: demandante [texto/PDF] · demandado [texto/PDF] · ¿presentados?

FASE 5 · SENTENCIA
 ⑩ SENTENCIA: fecha · tipo [Oral/Escrita] · resultado [Fav/Desfav/Parcial/Inhibitorio] · ¿costas?→valor · obligaciones · 📎 sentencia · fecha notificación

FASE 6 · EJECUTORIA → Estado final [Ejecutoriado / Cumplido / Archivado]
   ⭐ NO hay apelación ni segunda instancia (única instancia).
```

## Diferencias clave vs. el verbal (⭐)
1. **Demanda VERBAL o ESCRITA** (si verbal, no se exige el PDF de demanda).
2. Campo **¿Es mínima cuantía?** explícito.
3. **Correo del juzgado** en radicado/autoridad.
4. Traslado **10 días** (no 20).
5. **Reposición contra el auto admisorio** (paso propio).
6. **Sentencia anticipada sin audiencia** (rama): si Sí → sentencia escrita directa; si No → audiencia única.
7. **Audiencia ÚNICA** (art. 392) en vez de dos audiencias.
8. **Sin segunda instancia** (única instancia) — cierra en ejecutoria.
9. Audiencia única captura n.º de testigos por parte (numérico), no tablas de testigos/peritos.

## Campos que HABILITAN otros (condicionales)
- **Demanda = ESCRITA** → abre 📎 demanda/pruebas/anexos.
- **Pretensión = DETERMINADAS** → abre montos.
- **¿Medida cautelar? = Sí** → módulo completo.
- **Estado = Inadmitida** → subsanación 5d → decisión.
- **Estado = Rechazada** → recurso.
- **¿Sentencia anticipada? = Sí** → sentencia escrita (cierra sin audiencia). **= No** → audiencia única.
- **¿Reconvención? = Sí** → pretensiones + PDF + decisión del juez.

## MÓDULO MEDIDAS CAUTELARES
Idéntico al `doc-verbal.md` (solicitud → tipo → decisión del despacho → ejecución → levantamiento).

## Plazos
- Subsanación **5 días** · Traslado **10 días** · (no hay plazos de 2ª instancia).
