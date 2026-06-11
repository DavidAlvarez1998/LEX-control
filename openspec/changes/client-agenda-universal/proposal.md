# Proposal: Agenda universal en el portal cliente

## Intent
Hoy la **agenda** del portal cliente (calendario mensual sobre `SeguimientoComercial`) está
restringida al rol `COMERCIAL` (nav + page guard + `requirePermiso("comercial.seguimiento.*")`).
El usuario quiere que **todos los usuarios del despacho** puedan crear y usar la agenda, que al crear
una actividad **NO se pre-listen todos los clientes** (cliente opcional), y que en la **vista del
admin de empresa** cada ítem muestre **quién lo creó y su rol**.

## Scope
- **Schema** (ya aplicado): `SeguimientoComercial.clienteId` pasa de obligatorio a opcional
  (`String?`, relación `Cliente?` con `onDelete: SetNull`). La actividad de agenda ya no exige cliente.
- **API** (módulo `comercial`):
  - Los endpoints de agenda/seguimiento (`GET/POST/PATCH /seguimientos`, `GET /agenda`,
    `completar`/`cancelar`/`reabrir`) pasan de `requirePermiso("comercial.seguimiento.*")` a solo
    `requireAuth` → **baseline para cualquier usuario autenticado del despacho** (incluido el USUARIO
    sin rol). Se mantiene el scoping por `empresaId` (hard `WHERE`) y la lógica de dueño (`comercialId`).
  - `POST /seguimientos`: `assertCliente` solo si viene `clienteId`.
  - `GET /agenda`: cada ítem incluye `registradoPor { nombre, roles[], esAdminEmpresa }`, resuelto en
    batch desde `registradoPorId` (escalar sin FK), scoped por `empresaId`.
- **Frontend cliente**:
  - nav: el ítem Agenda deja de tener `roles: ["COMERCIAL"]` → visible para todos.
  - page guard: se quita `RolEmpresaGuard roles={["COMERCIAL"]}` de `/agenda`.
  - form de crear actividad: cliente **opcional** y buscador que **solo muestra resultados al
    escribir** (no pre-lista); se puede agendar sin cliente.
  - vista admin: cada ítem muestra "Creado por {nombre} · {rol}"; el filtro pasa de "Todos los
    comerciales" a "Todos los miembros" (cualquier miembro activo del despacho).

## Decisión clave
La agenda se vuelve **baseline** (no exige el módulo comercial contratado ni un rol concreto), porque
el requisito es "todos los usuarios". El `requirePermiso` (que combina puerta de módulo + puerta RBAC)
bloqueaba al USUARIO sin rol; por eso se sustituye por `requireAuth` en estos endpoints. El gate de
módulo sigue vigente en el resto del módulo comercial (clientes/fases/cotización/alertas…).

## Bug corregido (de paso)
El trabajo en progreso había puesto `empresaIdRequerido` (que es un **getter** `(req) => string`, NO
un middleware) en la posición de middleware de varios endpoints → la request colgaba (timeout, nunca
llamaba `next()`). Se eliminó de la cadena de middleware; el handler ya lo usa como getter.

## Out of scope
- Una entidad de "tarea/agenda" propia (se sigue reusando `SeguimientoComercial`).
- Cambiar la agenda del ADMIN de plataforma (esto es solo el portal cliente).

## Rollback
Aditivo salvo el gating y el cliente-opcional. Revertir = restaurar `requirePermiso` + `clienteId`
obligatorio. Las actividades sin cliente quedarían huérfanas de cliente (no rompen: `clienteId` null).
