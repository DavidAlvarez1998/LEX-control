# Tasks — proceso-autoavance-terminal

> Estado: **APLICADO + VERIFICADO** (2026-06-18). 424 tests API + smoke laboral 40/0 + build
> cliente verde. SIN commit.

## 1. Motor (API) — salto a terminal decidido
- [x] `procesos.router.ts`: `terminalDecidido(etapas, etapaActual, datos, docs)` — único terminal
      con `disponibleSi` satisfecho, por delante, requisitos propios cumplidos; ambiguo → null
- [x] `autoavanzarEtapas`: usa `siguienteEtapaAuto(...) ?? terminalDecidido(...)` como respaldo
- [x] `siguienteEtapaAuto` sin cambios (avance conservador intacto)

## 2. Cliente — guardar antes de avanzar
- [x] `datos-proceso.tsx`: `forwardRef` + `useImperativeHandle` → `flush()` (guardado tolerante
      de lo diligenciado; devuelve el proceso con la etapa auto-avanzada)
- [x] `procesos/[id]/page.tsx`: `datosRef` + en `irAEtapa` llama `flush()` antes de `moverEtapa`;
      si el auto-avance ya dejó el proceso en la etapa pedida o cerró el caso, no re-mueve

## 3. Verificación
- [x] Smoke `smoke-laboral-flujo.ts`: retiro=SÍ desde presentación → `archivado`/`CERRADO`;
      sin decisión terminal no cierra (40/0)
- [x] Suite API completa 424/424
- [x] Build cliente verde
- [x] Smoke manual en vivo (escribir sin guardar → clic avanzar → guarda y avanza/guía) + commit
