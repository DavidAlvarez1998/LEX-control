# Validación del proyecto y roadmap de mejoras

## Origen

Validación basada en una **auditoría multi-agente del código real** (21 agentes,
6 dimensiones × 3 subproyectos, 2026-06-26). Este change consolida los hallazgos en un
**roadmap accionable y priorizado** (ver `roadmap.md`). No cambia código: define qué
mejorar, en qué orden y con qué esfuerzo.

## Calificación (validación)

| Subproyecto | Arq. | Calidad | Seguridad | Tests | Rendim. | Robustez | Nota |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **lex-control-api** | 87 | 88 | 86 | 78 | 74 | 87 | **85 · B** |
| **lex-control-admin** | 76 | 78 | 82 | 32 | 74 | 83 | **76 · C** |
| **lex-control-client** | 81 | 79 | 82 | 22 | 74 | 83 | **74 · C** |

**Global ≈ 78 (B-/C+).** Núcleo backend fuerte (arquitectura en capas respetada de
verdad, tenancy forzado en el repositorio, motor de reglas puro); frontends correctos
pero con deuda visible y **sin red de tests**.

## Hallazgos transversales (los 3 proyectos)

1. **Tests = el agujero mayor.** API con 511 casos; ambos frontends en **cero** (CI solo
   lint+build). El **motor de reglas está triplicado** (api/admin/client) sin paquete
   compartido ni tests → riesgo de *drift* silencioso entre validación cliente/servidor.
2. **Sin paginación** en los listados principales → no escala multi-tenant.
3. **Seguridad: hardening barato pendiente** — sin CSP/headers en los `next.config.ts`,
   JWT en localStorage, uploads sin `fileFilter`, gating por rol cosmético en el cliente.
4. **God-components** (1300+ LOC, 30+ `useState`) en ambos frontends: intesteables.
5. **Integridad financiera**: `registrarPago` sin `FOR UPDATE` ni test de doble-pago.

## Ya resuelto desde la auditoría

- **API R1 (CI en rojo)**: el test commiteado que fallaba (`detectarHitos` tildes) ya
  está arreglado → suite **511/511** verde. [hecho esta sesión]

## Propuesta

Ejecutar el `roadmap.md` por **olas** (P0 → P2), empezando por el **Sprint 0** (alto
impacto / bajo costo): seguridad barata + red de tests mínima + el riesgo financiero.
Cada ítem es un cambio acotado y commiteable por separado; los grandes (descomponer
god-components, e2e contra DB real) se abren como sus propios changes cuando se encaren.
