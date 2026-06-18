# Proposal — Inicio del portal cliente consciente del rol (con tarjetas que navegan)

## Why
El `/inicio` del portal cliente (`lex-control-client`) es **igual para todos los roles**:
trae clientes, procesos, cartera, utilidad, alertas comerciales y vencimientos sin importar
quién mira. Problemas:
- Un **JURIDICO** ve "Cartera pendiente" y "Utilidad del mes" (contable) y alertas comerciales
  que no le tocan; un **CONTABLE** ve procesos/clientes que no gestiona.
- Las llamadas a módulos sin acceso devuelven **403** (se atrapan y muestran "—"): ruido y
  fetches inútiles.
- Las **StatCards de KPIs no son clicables** (Clientes/Procesos/Cartera/Utilidad): el usuario
  ve un número pero no puede ir a la sección.

## What
Hacer el dashboard de inicio **consciente del rol**: cada usuario ve SOLO los KPIs, alertas y
accesos rápidos de las secciones a las que tiene acceso, y **todas las tarjetas navegan** a su
sección. El criterio de acceso reusa el MISMO predicado del sidebar (`adminOnly` →
esAdminEmpresa; `roles` → esAdminEmpresa o tiene el rol; sin marca → todos). El admin de
empresa ve todo.

Mapa rol → widgets (mismas rutas/datos que ya existen):
- **JURIDICO** → KPI Procesos (→ /procesos) + tarjeta Vencimientos (→ /procesos/:id) + Clientes.
- **COMERCIAL** → KPI Clientes/Prospectos (→ /clientes) + Pendientes/alertas (→ /agenda · /clientes).
- **CONTABLE** → KPI Cartera pendiente y Utilidad del mes (→ /contable) + Facturación.
- **Todos** → Agenda (acceso) + saludo.
- **Admin de empresa** → la unión de todo.

## Scope
- Solo `lex-control-client`: `src/app/(dashboard)/inicio/page.tsx` + un `href` opcional en el
  `StatCard` compartido (`components/ui.tsx`) para hacerlo clicable.
- Reusa endpoints existentes (`/procesos`, `/procesos/vencimientos`, `/clientes`,
  `/comercial/alertas`, `/contable/cartera`, `/contable/reportes`). Solo se llama lo que el rol
  puede ver (no más 403 inútiles).

## Non-goals
- Sin cambios de API, schema ni endpoints nuevos. Sin tocar el backend ni el portal admin.
- Sin nuevos KPIs que requieran datos no disponibles hoy.

## Rollback
Revertir el commit del frontend; el inicio vuelve a su versión única. `StatCard.href` es
aditivo (opcional) → no afecta otros usos.
