# Comercial — Contrato & Cobro · delta (cartera read-only en la ficha)

> Change `comercial-rol-portal`. Adds a read-only cartera/cobro summary on the cliente ficha under the
> COMERCIAL module, so a comercial sees the client's outstanding balance WITHOUT requiring the
> contable module. It reuses the saldo derivation extracted to `contable/cartera.service.ts`.

## ADDED Requirements

### Requirement: Cliente cartera summary is readable under the comercial module
The system MUST expose `GET /comercial/clientes/:id/cartera` returning the cliente's `Cartera` rows
with their DERIVED saldo (`valorPagado`/`conSaldo`, reusing the contable cartera derivation), gated by
`requireAuth` + `requirePermiso('comercial.cobro.ver')` (granted to `ADMINISTRADOR` + `COMERCIAL`) and
the COMERCIAL módulo gate — it MUST NOT require the contable module or any contable permiso. It is
READ-ONLY (no write path here) and hard-scoped by `WHERE { empresaId }` with `assertCliente` on the
path id.

#### Scenario: Comercial reads a client's cartera without contable
- GIVEN a despacho whose contable module is NOT contracted and a user holding `comercial.cobro.ver`
- WHEN they GET `/comercial/clientes/:id/cartera` for a same-empresa cliente
- THEN they receive the cartera rows with derived saldo (200), not a "módulo contable no contratado" error

#### Scenario: Cross-empresa cliente rejected
- GIVEN a user of despacho A
- WHEN they GET `/comercial/clientes/:id/cartera` for a cliente of despacho B
- THEN it is rejected (assertCliente cross-tenant) and no cartera is returned
