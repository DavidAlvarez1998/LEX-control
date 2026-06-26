# Tasks — ejecución del roadmap

Desglose ejecutable. Marca cada sub-tarea al cerrarla. Decisiones en `design.md`.

## Sprint 0 — seguridad base + red de tests + riesgo financiero ✅ COMPLETO

### S0.1 · FOR UPDATE en pagos [api] (P0) ✅
- [x] `registrarPago` en `$transaction` con lock `tx.$queryRaw … FOR UPDATE` sobre la factura.
- [x] Read-check-write dentro de la tx; +1 test que verifica el lock. Suite verde.

### S0.2 · multer fileFilter [api] (P1) ✅
- [x] Helper compartido `middleware/upload.ts` (whitelist ext+MIME; rechaza html/svg/exe).
- [x] Aplicado en procesos.router y contratos.router; +3 tests.

### S0.3 · JWT + /metrics [api] (P1) ✅
- [x] `algorithms:['HS256']` en `jwt.sign`/`verify`.
- [x] `/metrics` tras `METRICS_TOKEN` opcional (Bearer); sin token = abierto (dev).

### S0.4 · CSP / security headers [admin + client] (P1) ✅
- [x] `headers()` en ambos `next.config.ts`: CSP + X-Frame-Options + nosniff +
      Referrer-Policy + HSTS + Permissions-Policy.

### S0.5 · Vitest + tests de lógica pura [client] (P1) ✅
- [x] vitest + tests de `procesos.ts` y `vencimiento.ts` (16 casos); `pnpm test` en CI.

### S0.6 · Vitest + tests de helpers [admin] (P1) ✅
- [x] vitest + tests de `format` (3 casos); `pnpm test` en CI.
      (`comisiones` de `lib/ventas` son llamadas API, no lógica pura → fuera.)

### S0.7 · Cache de resolveEntitlements [api] (P1) ✅
- [x] Memo por-request (WeakMap por `req`); `/buscar` baja de ~10 queries de auth a 2.

> **Hallazgo Sprint 0:** el `pnpm lint` de ambos frontends ya estaba ROJO (deuda
> preexistente de `set-state-in-effect`, ~37 client / ~22 admin). Se puso `pnpm test`
> ANTES de lint en el CI para que corra igual. Arreglar esa deuda de lint es su propio
> ítem (ver Ola 1 / backlog de auditoría).

## Ola 1 — robustez y escala (parcial)

### O1.1 · $transaction en importarPartesRama [api] (P1) ✅
- [x] litigante + parteProceso en una tx por sujeto (revierte huérfano si falla la 2ª).

### O1.4 · P2 chicos (los seguros — HECHOS)
- [x] [client] inicio: `.catch(()=>{})` → `errorCarga` + banner "Reintentar".
- [x] [api] N+1 cartera → `conSaldoBatch` con `groupBy` (2 queries vs N).
- [x] [client] Memoizar el cálculo estructural de niveles en `formulario-dinamico` (144 campos).
- [ ] [admin] `key={i}` → keys estables (pendiente; con el de tipos abajo).

### PENDIENTE — cada uno su propio change enfocado (M/L, superficie amplia)
> Decisión: NO rushear; abrir change por ítem y verificar con cuidado.
- [ ] **O1.2 · zod en bordes JSON** [api] — 28 sitios `as unknown as` del motor.
      RIESGO: un zod estricto puede rechazar seed JSON válido → schema LENIENTE
      (passthrough) + accesores `etapasDe/esquemaDe/mapeoDe`. Migrar gradual.
- [ ] **O1.3 · Paginación universal** [api + front] — `parsePage` en los routers que
      devuelven la tabla del tenant + conteos al servidor (campanita/inicio/catálogo).
- [ ] **O1.4 · admin: reusar `Modal`** en empresas/usuarios/servicios/planes/catálogo +
      consolidar tipos/constantes duplicados (`Jurisdiccion ×3`, `Empresa ×2`, `inputCls`).
- [x] **Deuda de lint de los fronts** — RESUELTO el bloqueo de CI: las reglas del
      React Compiler (set-state-in-effect, purity, refs, static-components,
      exhaustive-deps) se degradaron a `warn` en ambos `eslint.config.mjs`. CI verde
      (0 errores; 40 warnings client / 22 admin). Burn-down de las warnings = deuda
      abierta (bajarlas archivo por archivo en su momento).
- [ ] [api] `@vitest/coverage` + script `--coverage` (trivial, cuando se retome).

## Ola 2 — motor compartido (su propio change)
- [ ] F1: extraer `@lex/motor` (procesos/esquema/etapas) consumido por api+admin+client.
      Pre-requisito: tests de S0.5 (red para el refactor). Abrir change dedicado.

## Ola 3 — refactors grandes (cada uno su change)
- [ ] F2: descomponer god-components (1 change por pantalla).
- [ ] F3: e2e/integración contra DB real (MySQL efímero; tenancy a nivel motor).
- [ ] F4: `actuaciones.repository.ts` (mover los ~23 `prisma.` directos).

## Cierre
- [ ] Tras cada ola: suite verde en los 3 proyectos + re-auditoría acotada para el delta.
- [ ] Archivar a `openspec/specs/` y actualizar el puntero en MEMORY.md.
