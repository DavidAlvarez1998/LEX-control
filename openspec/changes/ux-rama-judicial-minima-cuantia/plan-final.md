# Plan final — qué nos quedamos (decisión 2026-06-22)

Tras analizar las 17 propuestas (ver `propuestas-ux.md`) y validar con el usuario, **el alcance se
acota a un set pequeño de alto impacto**. El resto queda parqueado (no descartado).

## ✅ Nos quedamos con 3 esenciales + 1 paquete de pulido

### Fase A — Las 3 que "se sienten" (alto impacto)
1. [x] **P12 — Preview del radicado al vincular** (IMPLEMENTADO 2026-06-22) · solo front;
   debounce a 23 díg → tarjeta "Encontrado: JUZGADO… · radicó {fecha} + partes" + "Vincular y traer
   datos". `ValidarRadicadoResp +fechaProceso +sujetosProcesales`. tsc+build verdes.
2. [x] **P1 — Novedades del juzgado en la lista** (IMPLEMENTADO 2026-06-22) · `Proceso.actuacionesNuevas`
   (push) recalculado en el sync + reset en marcar-vistas; `listProcesos +conNovedades`; píldora "N
   nuevas del juzgado" por fila + toggle "Con novedades". tsc + 485 tests + build verdes.
3. [x] **P9 — Importar los PDF del expediente** (IMPLEMENTADO 2026-06-22) · cliente obtenerDocumentos/
   descargarDocumento (+getBuffer); servicio on-demand listar/importar (idempotente por
   `DocumentoProceso.origenRamaIdReg`, anti-bloqueo); endpoints; panel "Documentos del expediente" en
   la ficha (listar/seleccionar/importar). tsc + 487 tests + build + smoke real (PDF 384KB). ✅ **Fase A completa.**

### Fase B — Pulido (IMPLEMENTADA 2026-06-22)
"Tanda 1" de claridad/confianza:
- [x] **P3** separar "Avance en el despacho" vs "🏛️ Lo que publica el juzgado" (copy + microcopy)
- [x] **P5** frescura ("sincronizado hace X · última actuación …") — campo `Proceso.actuacionesSyncAt`
      (push), seteado en `sincronizarProceso`, expuesto en el detalle, helper `haceCuanto`
- [x] **P7** disclaimer de confianza al pie del panel del juzgado
- [x] **P13** contador del radicado más visible (text-sm + negrita)
- [~] **P14** cuantía implícita → **ya estaba resuelto**: el bloque genérico de cuantía ya se oculta
      para el ejecutivo (`!esEjecutivo(tipo)`); su cuantía va por su propio campo. Sin cambios.
- [x] **P8** origen del dato ("de la Rama") → IMPLEMENTADO con marcador `Proceso.camposRamaCsv` (chip
      "de la Rama" en Despacho/juzgado de la ficha).

Gate: tsc API+client · vitest 487 · build client. Commiteado.

## ✅ Parqueadas — TODAS IMPLEMENTADAS (P6/P11/P8/P4/P15/P16/P10/P2 el 2026-06-22; P17 el 2026-06-23)
- [x] **P6** badge reservado/no-publicado (Proceso.ramaEstado) · [x] **P11** card "Estado en el juzgado"
      (Endpoint Detalle, ubicación) · [x] **P8** chip "de la Rama".
- [x] **P4** sugerencia de avance inline en el timeline · [x] **P15** chip "del juzgado" en documentos.
- [x] **P16** "↻ Actualizar con la Rama" en la lista (sincronizarMisProcesos, cap 40, no-sync-6h).
- [x] **P10** importar partes desde Sujetos (cotejo + crear Litigante/ParteProceso, mapeo de rol).
- [x] **P2** cockpit "Novedades del juzgado" en /inicio.

## ✅ P17 campanita in-app (versión LIVIANA) — IMPLEMENTADA 2026-06-23
Decisión del usuario: hacer la **liviana** (no la completa con modelo Notificacion). Implementado:
- **Campanita 🔔 en el topbar del cliente** (`src/components/novedades-campana.tsx`, montada en
  `src/components/topbar.tsx`) con un **badge** = `total` de `listProcesos({ conNovedades: true })`
  (= procesos con `actuacionesNuevas>0`). **SIN modelo nuevo, sin migración** — reusa el endpoint existente.
- Solo visible para **JURIDICO** (o admin de empresa); calca el guard de `inicio` (`esAdminEmpresa || roles.includes("JURIDICO")`).
- Clic → `/procesos?conNovedades=1`. El page de procesos ahora inicializa `conNovedades` desde la URL,
  así el deep-link llega con el filtro puesto.
- Refresco: al cargar, al volver el foco a la pestaña y cada 60s (calca `prospectos-pendientes.tsx`).
- Gate: build del cliente verde. (El único lint que toca el componente es el `setState`-en-effect que
  también tiene el componente de referencia — patrón establecido para leer `localStorage` solo en cliente.)
- La versión COMPLETA (modelo Notificacion + dropdown + marcar-leídas + historial) queda como follow-up
  mayor para cuando se quieran notificaciones in-app de verdad (aplicaría a más que procesos).

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
