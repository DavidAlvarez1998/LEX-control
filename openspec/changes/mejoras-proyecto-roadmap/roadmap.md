# Roadmap de mejoras (priorizado)

Prioridad: **P0** crítico · **P1** alto · **P2** medio. Esfuerzo: **S** (<½ día) ·
**M** (1–2 días) · **L** (varios días → su propio change). `[api|admin|client]`.

---

## ⭐ Sprint 0 — alto impacto / bajo costo (empezar por acá)

- [ ] **P0·S [api]** `FOR UPDATE` en `registrarPago` + test de doble-pago concurrente.
      Cierra el riesgo financiero (dos abonos podrían pasar el chequeo de saldo).
      `facturacion.service.ts:151-179`.
- [ ] **P1·S [api]** `fileFilter` de MIME/extensión en los 2 multer (`procesos.router.ts:22`,
      `contratos.router.ts:15`) → cierra el vector de upload malicioso (XSS almacenado).
- [ ] **P1·S [api]** Fijar `algorithms:['HS256']` en `jwt.verify/sign` (`auth.service.ts:34,39`)
      y poner `/metrics` tras auth o restringido por red (`app.ts:52-55`).
- [ ] **P1·S [admin+client]** `headers()` en `next.config.ts` con CSP, X-Frame-Options,
      X-Content-Type-Options, HSTS → defensa en profundidad (JWT vive en localStorage).
- [ ] **P1·M [client]** Instalar **vitest** + tests de la lógica pura crítica
      (`procesos.ts`: evaluarCondicion/campoEfectivamenteRequerido/validarDatos;
      `vencimiento.ts`) y sumar `pnpm test` al CI. Es el motor triplicado sin red.
- [ ] **P1·S [admin]** Instalar **vitest** + tests de helpers puros (`format.ts`
      formatMoney/parseMoneyInput, comisiones de `lib/ventas`).
- [ ] **P1·S [api]** Cachear/memoizar `resolveEntitlements` por-request (o TTL): baja
      `/buscar` de ~15 queries de auth a una fracción.

## P1 — siguientes

- [ ] **P1·S [api]** `$transaction` en `importarPartesRama` (litigante + parteProceso):
      elimina el multi-write no atómico (`actuaciones.service.ts:540-545`).
- [ ] **P1·M [api]** Validación en runtime (zod) en los bordes JSON: ~14 `as unknown as`
      sobre columnas JSON y respuestas de la Rama/notificaciones → fallar en el borde,
      no aguas abajo. Empezar por un accesor tipado `etapasDe(tipo)`/`esquemaDe(tipo)`.
- [ ] **P1·M [admin+client]** **Paginación** universal: cablear `parsePage` en los routers
      que devuelven la tabla completa del tenant (procesos, facturacion, litigantes,
      contratos) y consumir `page` en los listados; mover conteos al servidor
      (campanita/inicio/catálogo nivel-3 descargan el array entero solo para `r.total`).

## P2 — deuda y robustez

- [ ] **P2·S [client]** No tragar errores: reemplazar `.catch(()=>{})` en dashboards
      (`inicio/page.tsx`, `contable.ts`) por estado de error; el usuario ve ceros como
      datos reales ante un fallo. + guard de cancelación en efectos de fetch con filtros.
- [ ] **P2·S [admin]** Reusar el `Modal` compartido en lugar de overlays
      `fixed inset-0 z-50` hechos a mano (empresas/usuarios/servicios/planes/catálogo).
- [ ] **P2·S [admin]** Consolidar tipos/constantes duplicados (`Jurisdiccion ×3`,
      `Empresa ×2`, `inputCls`) y `key={i}` → keys estables.
- [ ] **P2·S [api]** N+1 de cartera (`conSaldo` con aggregate por fila) → `groupBy`
      único (`cartera.service.ts:31-37`, `contable.service.ts:266-270`).
- [ ] **P2·S [admin+client]** Memoizar cómputos por-keystroke/IIFE costosos
      (`formulario-dinamico.tsx`, `datos-proceso.tsx`; `gruposUsuarios`, lookups O(n)).
- [ ] **P2·S [api]** `@vitest/coverage` + script `--coverage` (métrica real de cobertura).
- [ ] **P2·M [client]** **Unificar el motor de reglas** triplicado en un paquete
      compartido (api/admin/client) — quita el drift de raíz (depende de tener tests).
- [ ] **P2·L [admin+client]** Descomponer god-components (1300+ LOC, 30+ useState):
      `catalogo-procesos`, `usuarios`, `empresas`, `procesos/[id]`, `procesos/nuevo`.
      Abrir como change propio por pantalla.
- [ ] **P2·L [api]** Tests de integración/e2e contra **DB real** (hoy 22/36 mockean
      Prisma): valida el aislamiento multi-tenant a nivel motor, no solo where-clause.
- [ ] **P2·M [api]** Mover el acceso a datos de `actuaciones.service.ts` (~23 `prisma.`
      directos) a un `actuaciones.repository.ts` (respetar la regla de capas del resto).

---

## Notas de ejecución
- Sprint 0 son ~7 ítems S/M: en una pasada deja seguridad base + red de tests mínima +
  el riesgo financiero cerrado. Sube las dos notas C de los frontends de forma directa.
- Los **L** (god-components, e2e, motor compartido) merecen su propio change SDD cada uno.
- Tras cada ola, re-correr la auditoría (o una acotada) para medir el delta.
