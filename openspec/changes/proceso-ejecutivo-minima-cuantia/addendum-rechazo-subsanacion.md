# Addendum — Rechazo de la demanda tras la subsanación (hueco del flujo)

> Estado: **IMPLEMENTADO + VERIFICADO 2026-06-22** (sin commit). Etapa terminal
> `archivado_rechazo` (orden 11, hermana de `terminacion`) agregada al seed con
> `disponibleSi {todas:[decisionCalificacion=Inadmite, decisionTrasSubsanacion=Rechazar]}`.
> `pnpm seed:catalogo` aplicado (ejecutivo: 12 etapas). Decisión: cierre **CERRADO**
> (sin cambio transversal del motor) · reposición NO modelada. Motor verificado por
> simulación (Inadmite+Rechazar → archivado_rechazo terminal; Admitir → sigue) + tsc +
> 484 tests. **Sin cambios de motor** (terminalDecidido ya lo resuelve).

## El hueco
La etapa `subsanacion` tiene el campo `decisionTrasSubsanacion` con opciones
**`Admitir` / `Rechazar`**, pero **el "Rechazar" no lleva a ningún cierre**: no existe etapa
terminal de rechazo. Si el juez rechaza, el proceso queda colgado o avanzaría mal hacia
`mandamientoPago`. El verbal/sumario/laboral sí tienen `archivado_rechazo`; al ejecutivo le
falta.

## La realidad legal (art. 90 CGP)
Si tras la inadmisión el demandante **no subsana** (o lo hace mal / fuera de los 5 días
hábiles), el juez **rechaza la demanda** → el proceso **termina sin trámite** (no hay
mandamiento de pago). Devuelven los anexos; **no hay cosa juzgada** (se puede re-demandar
corrigiendo), pero **la prescripción no se interrumpió** (art. 94 CGP: depende de la
notificación del auto admisorio, que nunca ocurrió). En **mínima cuantía (única instancia)
no hay apelación** del rechazo: solo **reposición**.

## Validación técnica (motor de etapas)
- El motor marca **toda etapa `terminal: true` como `estado = "CERRADO"`**
  (`procesos.service.ts:267` y `:382`). **No** existe mapeo a `ARCHIVADO` por etapa ni flag
  `estadoTerminal`. El `archivado_rechazo` del verbal es terminal → también queda **CERRADO**
  (el "archivado" es solo el nombre del paso).
- `terminalDecidido` (`maquina-etapas.ts`) ya selecciona una etapa terminal cuyo
  `disponibleSi` se cumple → basta agregar la etapa con la condición correcta; **el motor no
  se toca**.

## Solución (la manera correcta, fiel al patrón del verbal)
Agregar al seed del ejecutivo una etapa **terminal** `archivado_rechazo`:

```jsonc
{
  "key": "archivado_rechazo",
  "nombre": "Archivo (rechazo de la demanda)",
  "orden": <tras subsanacion>,
  "terminal": true,
  "disponibleSi": { "todas": [
    { "campo": "decisionCalificacion", "igualA": "Inadmite" },
    { "campo": "decisionTrasSubsanacion", "igualA": "Rechazar" }
  ] }
}
```

- Resultado: al marcar `decisionTrasSubsanacion = "Rechazar"`, el motor lleva el proceso a esa
  etapa terminal → **estado `CERRADO`**, etiqueta "Archivo (rechazo de la demanda)". Consistente
  con verbal/laboral. **Sin cambios de motor.**
- `decisionTrasSubsanacion = "Admitir"` sigue al flujo normal (mandamiento de pago).
- **No** se modela rama de apelación: mínima cuantía = única instancia (solo reposición).

### Decisiones a confirmar con el usuario
1. **Estado del cierre por rechazo: `CERRADO` (como verbal) vs `ARCHIVADO` real.** `CERRADO`
   es cero-esfuerzo y consistente; `ARCHIVADO` exigiría una mejora chica del motor (mapear
   ciertas etapas terminales a `ARCHIVADO`), que afectaría también al verbal/laboral.
   *Recomendado: `CERRADO`* para no abrir un cambio transversal por un caso de borde.
2. **¿Modelar la reposición?** Opcional, a futuro: campo `recursoReposicion`
   (interpuesto/decidido) + rama que reabra si la reposición prospera. v1: no.

## Tareas
- [x] Agregar la etapa `archivado_rechazo` al ejecutivo en `seed-tipos.json` (orden 11, terminal).
- [x] `pnpm seed:catalogo` para aplicar (33 tipos actualizados; ejecutivo con 12 etapas).
- [x] Smoke del motor: `Inadmite + Rechazar` → `archivado_rechazo` terminal (CERRADO); `Admitir` → sigue.
- [ ] (Opcional, descartado v1) ARCHIVADO real (mejora transversal del motor) · modelar reposición.
