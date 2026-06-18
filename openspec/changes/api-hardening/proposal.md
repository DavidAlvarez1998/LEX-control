# Proposal — API hardening (seguridad + scoping + concurrencia)

## Why
Auditoría multi-agente del API (83 hallazgos) detectó deuda real. Este change ataca los
**quick wins de alto valor / bajo riesgo** que NO requieren coordinar con el frontend:

- **Sin baseline de seguridad**: falta `helmet` (security headers), no hay **rate-limit** en
  `/auth/login` (brute-force de contraseñas) ni en `/publico` (spam de cuentas), y
  `express.json()` no tiene límite de tamaño.
- **Fragilidad de tenant scoping**: algunos métodos de repo leen/actualizan por `{ id }` sin
  `empresaId` (hoy seguros porque el id ya viene validado por un fetch scoped previo, pero
  rompen el invariante "el repo siempre scopea").
- **Race en `generarCodigoInterno`**: usa `count()+1`, que bajo concurrencia genera el mismo
  código → choque `@@unique` (P2002 → 500).
- **Duplicación**: el helper `n()` (Decimal→Number) está definido 5 veces con firmas distintas.
- **Llave de cifrado**: `env.encKey` cae a `"lex-dev-secret"` (inalcanzable porque `JWT_SECRET`
  es required, pero es código muerto confuso).

## What
1. `helmet()` + `express-rate-limit` (login y público; **se omite en `NODE_ENV=test`** para no
   romper la suite) + `express.json({ limit })`.
2. Defense-in-depth: scopear por `empresaId` los métodos de repo que hoy leen por `{ id }`
   (cambio de cero-comportamiento: el id ya estaba validado).
3. `generarCodigoInterno`: derivar el consecutivo del ÚLTIMO código (`orderBy desc` + parse) en
   vez de `count`.
4. `shared/money.ts` (`toNumber`) y reemplazar los 5 `n()` duplicados.
5. Quitar el fallback muerto `"lex-dev-secret"` de `env.ts`.

## Non-goals (van como proyectos aparte, requieren coordinación)
- Migración masiva `Record<string,unknown>`+`as never` → `Prisma.*Input` (18 repos).
- Paginación end-to-end + unificar forma de respuesta (toca ambos frontends).
- Estandarizar 404 vs 400 de ownership (rompe expectativas del front).
- Orquestadores multi-módulo, unit tests de services, índices nuevos (siguiente tanda).

## Rollback
Cada punto es independiente; revertir el commit. El rate-limit/helmet son aditivos; el scoping
no cambia comportamiento; `shared/money` es un util nuevo.
