# Tasks — laboral-titulo-auto

## Implementación (cliente)
- [x] `tituloAuto` incluye `tipo.grupo === "LABORAL"` en `procesos/nuevo/page.tsx`
- [x] Helper `tituloLaboral(tipo, datos)`: "{tipo} — {demandante} vs. {demandado}", orden por `rol`, contraparte desde partes, fallback a solo cliente
- [x] `tituloFinal` usa `tituloLaboral` para LABORAL
- [x] Oculta el campo manual "Título del caso" para LABORAL (gate de render)

## Acotar roles a demandante/demandado (laboral)
- [x] `ROLES_LABORAL` + helper `rolesDisponibles(tipo)` en `procesos/nuevo/page.tsx`
- [x] Selector "Rol procesal del cliente" usa `rolesDisponibles(tipo)`
- [x] Selector "Rol procesal" de la contraparte usa `rolesDisponibles(tipo)`

## Verificación
- [x] `pnpm build` del cliente verde
- [ ] Smoke manual: crear laboral como Demandante (cliente vs contraparte), como Demandado (contraparte vs cliente), y sin contraparte (solo cliente)

## OpenSpec
- [x] Spec delta `tramite-catalog` (MODIFIED el requirement del título auto)
- [ ] Archivar tras verificación manual (fusionar a `openspec/specs/tramite-catalog`)
