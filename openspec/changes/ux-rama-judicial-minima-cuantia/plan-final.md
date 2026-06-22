# Plan final — qué nos quedamos (decisión 2026-06-22)

Tras analizar las 17 propuestas (ver `propuestas-ux.md`) y validar con el usuario, **el alcance se
acota a un set pequeño de alto impacto**. El resto queda parqueado (no descartado).

## ✅ Nos quedamos con 3 esenciales + 1 paquete de pulido

### Fase A — Las 3 que "se sienten" (alto impacto)
1. **P12 — Preview del radicado al vincular** · *solo front, barata, muy visible* ·
   detalle en `diseno-p10-p11-p12-...md`. Sin cambios de backend (endpoint ya existe).
2. **P1 — Novedades del juzgado en la lista** · detalle en `diseno-p1-novedades-lista.md`.
   1 campo denormalizado (`actuacionesNuevas`) + filtro + píldora.
3. **P9 — Importar los PDF del expediente** · detalle en `diseno-p9-importar-documentos.md`.
   La de mayor impacto; 1 campo (`origenRamaIdReg`) + cliente + UI on-demand.

### Fase B — Pulido (opcional, casi gratis — un solo paquete)
"Tanda 1" de claridad/confianza, todo copy/estilo + 2 campos (detalle en `diseno-detallado.md`):
- **P3** separar "Avance en el despacho" vs "Lo que publica el juzgado 🏛️"
- **P5** frescura ("sincronizado hace X · última actuación …") — campo `actuacionesSyncAt`
- **P7** disclaimer de confianza · **P13** contador visible + feedback persistente
- **P8** origen del dato ("de la Rama") · **P14** mínima cuantía = cuantía implícita

## ⏸ Parqueado (no ahora)
P6 (badge reservado), P10 (importar partes/Sujetos), P11 (card Estado/ubicación), P16 (actualizar
todos), P4 (actuación→etapa), P15 (docs agrupados), P2 (cockpit), P17 (campanita in-app).
Todas tienen su diseño listo en este change para retomarlas cuando se quiera.

## Orden de implementación sugerido
1. **Fase B (pulido)** primero — barato, da claridad inmediata a lo ya construido.
2. **P12** — front, rápido, mejora el momento clave (vincular radicado).
3. **P1** — visibilidad de novedades en la lista.
4. **P9** — importar documentos (la más grande; **coordinar con la sesión paralela** del *uploader de
   documentos* para reusar su componente y no duplicar UI).

## Cambios de datos que implica el set elegido (todos aditivos → `pnpm push`)
| Propuesta | Campo |
|---|---|
| P5 (Fase B) | `Proceso.actuacionesSyncAt DateTime?` |
| P1 | `Proceso.actuacionesNuevas Int @default(0)` |
| P9 | `DocumentoProceso.origenRamaIdReg String?` (+ `@@unique([procesoId, origenRamaIdReg])`) |

## Notas de coordinación / riesgo
- **Sesión paralela activa** editando `procesos.service.ts`, la ficha y `procesos-api.ts` (uploader de
  documentos + `naturalezaJuridica`). **No implementar P1/P9 encima hasta que cierren y commiteen** —
  P9 además debe reusar su uploader. P12 (solo front, otro componente) y la Fase B (copy/estilo) son
  de menor riesgo de colisión.
- Cada fase, al implementarse, sería su propio change con su gate (tsc + tests + build).

> Este documento es la decisión de alcance; no implementa nada. `propuestas-ux.md` y los `diseno-*.md`
> conservan el análisis completo y el resto de propuestas para retomarlas.
