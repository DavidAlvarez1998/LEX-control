# Design — Inicio por rol

## Predicado de acceso (espejo del sidebar)
Una sección con `roles` es visible si `esAdminEmpresa` o `user.roles` incluye uno; una
`adminOnly` solo para `esAdminEmpresa`; sin marca, para todos. Se reusa la misma idea que
`NAV_ITEMS`/`puedeVer` para que el dashboard NUNCA muestre un widget de una sección que el
usuario no ve en el menú.

```ts
const u = getUser();
const tieneRol = (r: string) => !!u?.esAdminEmpresa || (u?.roles ?? []).includes(r);
const puedeProcesos  = tieneRol("JURIDICO");
const puedeClientes  = tieneRol("JURIDICO") || tieneRol("COMERCIAL");
const puedeComercial = tieneRol("COMERCIAL");        // alertas/pipeline
const puedeContable  = tieneRol("CONTABLE");
```

## Carga de datos: solo lo accesible
Cada fetch se dispara **solo si** el rol puede ver esa sección (evita 403 y trabajo inútil):
- `puedeProcesos` → `GET /procesos` (total) + `GET /procesos/vencimientos`.
- `puedeClientes` → `GET /clientes`.
- `puedeComercial` → `GET /comercial/alertas`.
- `puedeContable` → `GET /contable/cartera` + `GET /contable/reportes?periodo=`.

`Promise.all` solo de las llamadas habilitadas. Cada una mantiene su `.catch` defensivo.

## Tarjetas que navegan
- `StatCard` gana un prop opcional `href`: si está, se envuelve en `<Link>` con afordancia
  hover (cursor + leve realce). Sin `href` se comporta igual que hoy (compatibilidad).
- KPIs clicables: Clientes → `/clientes`, Procesos → `/procesos`, Cartera → `/contable`,
  Utilidad → `/contable`.
- Tarjetas de detalle ya navegan por fila (Vencimientos → `/procesos/:id`, Pendientes →
  `/agenda`·`/clientes`, Últimos clientes → `/clientes/:id`).

## Layout
- Saludo (todos).
- Grid de StatCards: solo las habilitadas por rol (1–4 según acceso).
- Vencimientos (si `puedeProcesos` y hay vencidos/por vencer).
- Pendientes/alertas (si `puedeComercial`) + Últimos clientes (si `puedeClientes`).
- Si el usuario no tiene ningún módulo (raro), muestra solo el saludo + acceso a Agenda/Mi Cuenta.

## Decisiones
- **Cliente-side gating** (presentación): el backend ya hace cumplir el acceso real (RBAC); esto
  solo decide qué pintar/llamar. No es una frontera de seguridad nueva.
- **Sin colapsar a "admin ve todo" en una sola consulta**: el admin de empresa pasa todos los
  predicados, así que ve la unión sin código especial.
