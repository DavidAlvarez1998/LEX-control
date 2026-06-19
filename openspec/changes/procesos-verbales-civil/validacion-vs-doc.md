# Validación — lo IMPLEMENTADO vs. los DOCUMENTOS (verbal / verbal sumario)

Compara el seed actual (mi versión genérica del CGP) contra `doc-verbal.md` / `doc-verbal-sumario.md`
(fieles a los .docx). **Veredicto: lo implementado NO refleja los documentos — falta mucho.**
Esto es el insumo para actualizar el seed.

## Brechas (doc pide → implementado tiene)

| Área | Documento | Implementado hoy | Estado |
|---|---|---|---|
| **CALIDAD** (rol del cliente) | 7 opciones: demandante, demandado, **curador ad litem, tercero interviniente, litisconsorte, apoderado sustituto, apoderado de ambas partes** | `rol` = solo Demandante/Demandado | ❌ faltan 5 |
| **Datos de las partes** | demandante y demandado: nombre · cédula · dirección · correo · teléfono | no se piden (se usa cliente + partes) | ❌ falta |
| **Unidad de medida** | SMMLV / Pesos | — | ❌ falta |
| **Cuantía** | Mínima/Menor/Mayor/N-A | cuantía genérica del form (Mínima/Menor/Mayor) | ⚠️ parcial |
| **Pretensión** | Determinadas (→ monto pretensiones + total) / Indeterminadas | `pretensiones` (texto) | ❌ falta el condicional de montos |
| **Síntesis / medio de radicación / soporte** | sí | — | ❌ falta |
| **Medidas cautelares** | MÓDULO completo (solicitud→tipo→decisión despacho→caución→ejecución→levantamiento) | solo un booleano `solicitaMedidasCautelares` | ❌ falta el módulo |
| **Estado de la demanda** | admitida / inadmitida (subsanar 5d, copia de envío, decisión→admisión/rechazo→recurso) / rechazada (recurso apelación/reposición) | `decisionAuto` simplificado | ⚠️ incompleto |
| **Traslado** | notificado, fechas inicio/fin, estado [en término/vencido/contestado], 20d (verbal)/10d (sumario) | `fechaNotificacion` + plazo | ⚠️ incompleto |
| **Reconvención** | pretensiones, PDF, ¿contestación?, decisión juez admitir/rechazar | `hayReconvencion` + decisión | ⚠️ parcial |
| **Excepciones de mérito** | traslado 5d, pronunciamiento del demandante, pruebas adicionales | `excepcionesMerito` (texto) | ❌ falta el sub-flujo |
| **Audiencia inicial (372)** | asistencias, excepciones previas, conciliación, interrogatorio, fijación litigio, control legalidad, saneamiento, decreto pruebas [casillas], sentencia inmediata, acta, grabación | `conciliaResultado` + textos | ❌ muy incompleto |
| **Audiencia instrucción (373)** | pruebas practicadas [casillas], testigos/peritos (tablas), alegatos, sentencia oral, sentido, sentencia escrita 10d | `fechaSentencia`+`decisionSentencia` | ❌ muy incompleto |
| **Sentencia** | tipo (oral/escrita), resultado (fav/desfav/parcial/inhibitorio), costas, obligaciones | `decisionSentencia` (Fav/Desfav) | ⚠️ incompleto |
| **Recursos** | tipo: apelación / **aclaración / corrección / adición / reposición** | solo apelación (`hayRecurso`) | ❌ faltan tipos |
| **2ª instancia** | efecto (suspensivo/devolutivo/diferido), ponente, reparto, resultado (confirma/revoca/modifica/nulidad) | remisión→sustentación→audiencia→sentencia (genérico) | ⚠️ parcial |
| **Sumario: demanda verbal/escrita** | desplegable; escrita → PDF | demanda.pdf siempre | ❌ falta |
| **Sumario: ¿es mínima cuantía?** | sí | — | ❌ falta |
| **Sumario: reposición vs auto admisorio** | sí | — | ❌ falta |
| **Sumario: sentencia anticipada (sin audiencia)** | rama Sí→sentencia escrita / No→audiencia única | — | ❌ falta |
| **Sumario: audiencia única (392)** | conciliación, interrogatorio, pruebas, alegatos | `audienciaUnica` mínima | ⚠️ incompleto |

## Lo que SÍ coincide (mantener)
- Doble instancia (verbal) / única (sumario). ✅
- Plazos: subsanación 5d, traslado 20/10d. ✅
- Estructura general: demanda → calificación → traslado → audiencia(s) → sentencia → recurso. ✅
- `actualizado=true`, grupo JUDICIAL, jurisdicción ORDINARIA_CIVIL, sección Procesos. ✅

## Veredicto
La estructura macro está alineada, pero **el detalle de campos está MUY por debajo del documento**:
faltan la **CALIDAD (7 roles)**, los **datos de las partes**, **unidad/pretensión determinada**,
el **módulo de medidas cautelares**, el detalle de **audiencias**, los **tipos de recurso**, y en el
sumario la **demanda verbal/escrita** y la **sentencia anticipada**.

→ **Recomendación:** reescribir ambos `esquemaFormulario`/`etapas` del seed para que reflejen
los `doc-*.md`. Es un cambio grande (decenas de campos + sub-módulos condicionales), pero el
motor lo soporta (mostrarSi/disponibleSi/requeridosSi + documentos anclados). Confirmar antes de
implementar; posiblemente por fases (empezar por CALIDAD + datos de partes + cuantía/pretensión +
medidas cautelares, luego audiencias y recursos).
