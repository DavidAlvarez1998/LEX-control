# Tasks — ui-tooltip

> Estado: **APLICADO** (2026-06-19). Componente creado en ambos portales + primera adopción
> (Clientes Míos/Todos). tsc verde en client y admin. Sin commitear aún (frontends con trabajo
> paralelo del usuario).

## 1. Componente
- [x] `Tooltip` en `lex-control-client/src/components/ui.tsx`: PORTAL a `document.body` + `position: fixed` + `zIndex: 1000` (no lo tapa el sidebar/topbar), retardo ~450ms al hover, hover+focus, `role="tooltip"`, `pointer-events-none`, theme-aware, `side` top/bottom/left/right
- [x] `Tooltip` idéntico en `lex-control-admin/src/components/ui.tsx`

## 2. Primera adopción
- [x] Botones "Míos" / "Todos" de `clientes/page.tsx` (client) migrados de `title` → `<Tooltip>` con la explicación de cada vista

## 3. Verificación
- [x] `tsc --noEmit` verde en client y admin (sin tocar `.next`; dev servers vivos hot-reload)
- [ ] Smoke visual en el navegador (hover muestra la burbuja; el click sigue funcionando)

## 4. Cierre
- [ ] Migrar otros `title` de UI a `<Tooltip>` de forma incremental (no urgente)
- [ ] Fusionar el spec delta a `openspec/specs/ui-tooltip/` y archivar el change
- [ ] Commit (frontends: client + admin) cuando el usuario lo indique
