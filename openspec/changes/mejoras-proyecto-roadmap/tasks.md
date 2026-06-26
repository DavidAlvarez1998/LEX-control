# Tasks — ejecución del roadmap

Desglose ejecutable. Marca cada sub-tarea al cerrarla. Decisiones en `design.md`.

## Sprint 0 — seguridad base + red de tests + riesgo financiero

### S0.1 · FOR UPDATE en pagos [api] (P0)
- [ ] `registrarPago` en `$transaction` interactivo; lock con `tx.$queryRaw … FOR UPDATE`.
- [ ] Leer saldo y validar DENTRO de la tx (con `tx`, no `prisma`).
- [ ] Test de servicio: 2 `registrarPago` concurrentes → saldo final correcto / 1 falla.

### S0.2 · multer fileFilter [api] (P1)
- [ ] Helper `fileFilter` (whitelist ext+MIME; rechaza html/svg/exe).
- [ ] Aplicar en `procesos.router.ts:22` y `contratos.router.ts:15`.
- [ ] Test: un MIME no permitido → 400/rechazo.

### S0.3 · JWT + /metrics [api] (P1)
- [ ] `algorithms:['HS256']` en `jwt.sign` y `jwt.verify` (`auth.service.ts`).
- [ ] `/metrics` tras `requireAuth` (ADMIN) o bind a red interna (`app.ts:52-55`).

### S0.4 · CSP / security headers [admin + client] (P1)
- [ ] `async headers()` en ambos `next.config.ts`: CSP (report-only primero),
      X-Frame-Options, X-Content-Type-Options, Referrer-Policy, HSTS.
- [ ] Verificar que no rompe llamadas al API ni al microservicio documental; endurecer.

### S0.5 · Vitest + tests de lógica pura [client] (P1)
- [ ] Instalar `vitest` + `@vitest/coverage-v8`; scripts `test`/`test:run`.
- [ ] Tests: `lib/procesos.ts` (evaluarCondicion, campoEfectivamenteRequerido,
      documentosRequeridosDeEtapas, validarDatos) y `lib/vencimiento.ts`.
- [ ] Sumar `pnpm test` al CI del client.

### S0.6 · Vitest + tests de helpers [admin] (P1)
- [ ] Instalar `vitest`; tests de `format` (formatMoney/parseMoneyInput) y comisiones.
- [ ] Sumar `pnpm test` al CI del admin.

### S0.7 · Cache de resolveEntitlements [api] (P1)
- [ ] Memoizar por-request (o TTL corto) las queries de permisos; medir `/buscar`.

## Ola 1 — robustez y escala

### O1.1 · $transaction en importarPartesRama [api] (P1)
- [ ] Envolver litigante + parteProceso en una tx (`actuaciones.service.ts:540-545`).

### O1.2 · zod en bordes JSON [api] (P1)
- [ ] Accesores `etapasDe/esquemaDe/mapeoDe(tipo)` con `parse` zod en el borde.
- [ ] Migrar los ~13 `as unknown as`; validar el contrato de la Rama al parsear.

### O1.3 · Paginación universal [api + front] (P1)
- [ ] `parsePage` en routers procesos/facturacion/litigantes/contratos; `include` estrecho.
- [ ] Front: consumir `page`; endpoint(s) de conteo para campanita/inicio/catálogo.

### O1.4 · P2 chicos
- [ ] [client] Sacar `.catch(()=>{})` de dashboards → estado de error; guard de cancelación.
- [ ] [admin] Reusar `Modal` compartido en empresas/usuarios/servicios/planes/catálogo.
- [ ] [admin] Consolidar tipos/constantes duplicados; `key={i}` → keys estables.
- [ ] [api] N+1 cartera → `groupBy` (`cartera.service.ts`, `contable.service.ts`).
- [ ] [admin+client] Memoizar cómputos por-keystroke/IIFE (`formulario-dinamico`, `datos-proceso`).
- [ ] [api] `@vitest/coverage` + script `--coverage`.

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
