# Diseño — cómo ejecutar el roadmap

Decisiones técnicas por tema (solo lo no-obvio). El "qué/orden" vive en `roadmap.md`;
el desglose ejecutable en `tasks.md`. Cada ítem es commiteable por separado.

## A. Concurrencia de pagos — `FOR UPDATE` (P0)

Prisma no expone `SELECT … FOR UPDATE` en su API tipada. Patrón a usar en
`registrarPago` (`facturacion.service.ts`):
1. Envolver el registro en `prisma.$transaction(async (tx) => { … })` **interactivo**.
2. Tomar el lock de fila con raw dentro de la tx:
   `await tx.$queryRaw\`SELECT id FROM facturas WHERE id = ${facturaId} FOR UPDATE\``.
3. Recién ahí leer pagos/saldo, validar y crear el `Ingreso`/pago — todo con `tx`.
- **Idempotencia adicional**: si `numeroComprobante` viene, ya hay unique; si no, el lock
  evita el doble-abono concurrente. **Test**: lanzar 2 `registrarPago` en `Promise.all`
  y assertar que solo uno pasa (o que el saldo final es correcto). Mockear con
  `$transaction` real no aplica (unit) → test a nivel servicio con la lógica de saldo,
  documentando que el lock se valida en integración (tema F).

## B. Seguridad — hardening (P1, todo S)

- **multer `fileFilter`**: lista blanca por extensión + MIME (`pdf`, `doc/x`, imágenes).
  Rechazar `html/svg/exe`. Aplicar a las 2 instancias (`procesos.router`, `contratos.router`).
- **JWT**: `jwt.sign/verify(..., { algorithms: ['HS256'] })` para impedir confusión de
  algoritmo. `/metrics`: detrás de `requireAuth` (rol ADMIN) o bind a red interna.
- **CSP / headers (Next)**: `async headers()` en `next.config.ts` (admin y client) con
  `Content-Security-Policy` (default-src 'self'; permitir el origen del API y, si aplica,
  el microservicio documental), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, y `Strict-Transport-Security`. Empezar **report-only** para no romper,
  medir, y endurecer. Nota: el JWT en localStorage no se mueve a cookie httpOnly en esta
  ola (cambio mayor de auth); la CSP es la mitigación inmediata.
- **Gating por rol server-side (frontends)**: envolver rutas sensibles en su Guard
  (`/equipo` → `AdminEmpresaGuard`); el sidebar filtrado NO es control de acceso (la
  autoridad real sigue siendo el 403 del API, pero cerramos el paseo directo por URL).

## C. Tests — red mínima primero (P1)

- **Frontends**: instalar `vitest` + `@vitest/coverage-v8`; script `test`/`test:run`;
  sumar `pnpm test` al workflow de CI (hoy solo lint+build).
- **Qué testear primero (máx ROI, lógica PURA, sin DOM)**:
  - client: `lib/procesos.ts` (`evaluarCondicion`, `campoEfectivamenteRequerido`,
    `documentosRequeridosDeEtapas`, `validarDatos`), `lib/vencimiento.ts`.
  - admin: `lib/format` (`formatMoney`, `parseMoneyInput`), comisiones de `lib/ventas`.
- **API**: `@vitest/coverage` para metrizar; e2e contra DB real = tema F (P2·L).

## D. Validación en runtime (zod en bordes) — (P1·M, api)

- Crear accesores tipados que centralicen el `as unknown as` del motor:
  `etapasDe(tipo): EtapaDef[]`, `esquemaDe(tipo): CampoEsquema[]`, `mapeoDe(tipo)`.
- Validar con zod **en el borde** (al leer columnas JSON de la DB y respuestas de la
  Rama/notificaciones). Si falla, error claro en el borde, no un crash aguas abajo.
- Migrar los ~13 sitios a los accesores; el contrato externo (Rama) gana su `parse`.

## E. Paginación universal — (P1·M)

- API: cablear el `parsePage` ya existente en los routers que devuelven la tabla del
  tenant entera (procesos, facturacion, litigantes, contratos); estrechar el `include`
  de procesos para no arrastrar el JSON pesado del `tipoProceso` por fila.
- Front: consumir `page` en los listados; **conteos al servidor** (campanita/inicio/
  catálogo nivel-3 hoy bajan el array completo solo para `.total` → endpoint de conteo).

## F. Temas grandes (cada uno su propio change SDD)

- **F1 · Motor de reglas compartido (P2·M)**: extraer `procesos.ts`/`esquema`/etapas a un
  paquete (`@lex/motor`) consumido por api+admin+client. Requiere primero los tests de C
  (red de seguridad para el refactor). Quita el *drift* de raíz.
- **F2 · Descomponer god-components (P2·L)**: por pantalla
  (`catalogo-procesos`, `usuarios`, `empresas`, `procesos/[id]`, `procesos/nuevo`):
  extraer sub-componentes y custom hooks (`useX`) que aíslen estado/fetch del render.
  Un change por pantalla; apoyarse en los tests nuevos.
- **F3 · e2e/integración contra DB real (P2·L)**: levantar MySQL efímero (ya hay CI con
  uno) y correr un set que ejerza el aislamiento multi-tenant a nivel motor, no
  where-clause. Cubrir los caminos críticos (pagos, tenancy, auth).
- **F4 · `actuaciones.repository.ts` (P2·M)**: mover los ~23 `prisma.` directos del
  service a un repositorio, alineando con la regla de capas del resto.

## Secuencia y dependencias

`Sprint 0` (A,B,C-mínimo, parte de E) → `Ola 1` (D, resto de E, P2 chicos) →
`Ola 2` (F1, apoyado en C) → `Ola 3` (F2/F3/F4). C (tests) habilita F1/F2 con red.
