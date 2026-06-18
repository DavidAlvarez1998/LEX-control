# Tasks — API hardening

## 1. Seguridad
- [ ] 1.1 `pnpm add helmet express-rate-limit`.
- [ ] 1.2 `app.ts`: `helmet()` + `express.json({ limit: "1mb" })`.
- [ ] 1.3 Rate-limit en `/auth/login` (estricto) y `/publico` (moderado); omitido si `NODE_ENV=test`.
- [ ] 1.4 `env.ts`: quitar el fallback muerto `"lex-dev-secret"` de `encKey`.

## 2. Scoping defense-in-depth (cero cambio de comportamiento)
- [ ] 2.1 `facturacion.repository.findByIdConItems` → scoped por `empresaId`.
- [ ] 2.2 `clientes.service.convertirClienteUseCase` → lectura final scoped.

## 3. Concurrencia
- [ ] 3.1 `generarCodigoInterno` → derivar del último código (`orderBy desc` + parse) en vez de `count`.

## 4. Duplicación
- [ ] 4.1 `shared/money.ts` (`toNumber`) y reemplazar los 5 `n()` (cartera/facturacion/planes/publico/ventas).

## 5. Verificación
- [ ] 5.1 `tsc` + `pnpm test` (434) + `pnpm build` verdes.
- [ ] 5.2 Commit + (archivar tras smoke si aplica).
