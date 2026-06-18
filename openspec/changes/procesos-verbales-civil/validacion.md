# Validación — procesos-verbales-civil

Auditoría de conformidad de lo IMPLEMENTADO (seed `prisma/seed-tipos.json`) contra lo
SOLICITADO (`proposal.md` + `design.md`, fuente CGP). Fecha: 2026-06-18.

**Método:** verificación programática sobre el seed real (28 aserciones) + suite de tests con
el motor real + Zod del catálogo. Resultado: **28/28 conforme**.

## Matriz de conformidad

### Ubicación (lo que pidió el usuario: "agregarlos a Procesos, jurisdicción y sección")
| Requisito | Verbal | Sumario |
|---|---|---|
| Sección "Procesos" (`grupo = JUDICIAL`) | ✅ | ✅ |
| `esJudicial = true` (muestra radicado/juzgado) | ✅ | ✅ |
| Jurisdicción `ORDINARIA_CIVIL` (grupo "Ordinaria civil" en Nuevo proceso) | ✅ | ✅ |

### Proceso (declarativo) verbal — CGP 368-373
| Requisito (diseño/CGP) | Estado |
|---|---|
| Campo `rol` (Demandante/Demandado) | ✅ |
| Calificación gated a `rol=Demandante` (solo el demandante califica) | ✅ |
| Subsanación 5 días **hábiles** | ✅ |
| Traslado 20 días **hábiles** | ✅ |
| Dos audiencias (inicial art. 372 + instrucción art. 373) | ✅ |
| Recurso de apelación contra la sentencia | ✅ |
| Segunda instancia completa (remisión→sustentación→audiencia→sentencia 2ª) | ✅ |
| 2ª instancia gated por `hayRecurso=SI ∧ concedeApelacion=SI` | ✅ |
| Terminal por conciliación | ✅ |
| Terminales de archivo (rechazo + retiro) | ✅ |
| Reconvención modelada | ✅ |

### Proceso verbal sumario — CGP 390-392
| Requisito (diseño/CGP) | Estado |
|---|---|
| Campo `asuntoNaturaleza` (asuntos del art. 390) | ✅ |
| Traslado 10 días **hábiles** | ✅ |
| Audiencia única (art. 392) | ✅ |
| **SIN** etapa de recurso (sentencia EN FIRME — única instancia, art. 318) | ✅ |
| Sin apelación / sin 2ª instancia | ✅ |
| Terminal "sentencia en firme" | ✅ |
| Sentencia exigida **solo si NO se concilia** | ✅ |

### Comportamiento del motor (heredado, verificado por `tests/verbales-flujos.test.ts`)
| Requisito | Estado |
|---|---|
| Auto-avance al completar campos/documentos | ✅ (8 tests caminan con motor real) |
| Gating (no avanza si falta dato/documento) | ✅ (el test detectó que traslado exige `fechaNotificacion`) |
| Salto a terminal decidido (retiro / rechazo / conciliación cierran solos) | ✅ |
| Sin estancamientos (verbal sin apelar termina; sumario sin 2ª inst.) | ✅ |
| Plazos en días hábiles (CGP art. 118) | ✅ |

## Evidencia
- **Verificación programática:** 28/28 aserciones "TODO CONFORME".
- **`tests/verbales-flujos.test.ts`:** 8/8 (flujos verbal + sumario con `siguienteEtapaAuto`/`terminalDecidido` reales).
- **`tests/seed-tipos.test.ts`:** verde (Zod del catálogo; refs de campo válidas, claves únicas).
- **Suite API completa:** 442/442. **Re-seed:** 40 tipos. **Build cliente:** verde.

## Alcance respetado ("tal como dicta el CGP, sin enriquecimientos")
Confirmado que NO se agregaron: desistimiento, casación, sentencia anticipada como rama,
conciliación-como-requisito que gatee, ni terminales diferenciados por resultado. Solo el
trámite que dicta el código.

## Pendiente (no afecta conformidad)
- Smoke e2e en vivo (opcional; el test de flujos ya cubre los caminos con el motor real).
- Stepper agrupado por fase: hoy es laboral-only → el verbal/sumario usan el stepper plano
  (funciona). Extenderlo a civil es un ajuste de cliente aparte.
- Commit (staging selectivo por submódulo).

## Veredicto
**CUMPLE lo solicitado.** Los dos procesos quedaron en la sección y jurisdicción correctas, con
los flujos completos fieles al CGP (verbal doble / sumario única), heredando el auto-avance y el
gating del motor. 28/28 conforme + 442 tests verdes.
