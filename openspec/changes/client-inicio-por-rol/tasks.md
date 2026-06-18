# Tasks — Inicio por rol

## 1. StatCard clicable
- [ ] 1.1 `components/ui.tsx`: agregar prop opcional `href` a `StatCard`; si está, envolver en
      `<Link>` con afordancia hover (cursor + realce). Sin `href` = igual que hoy.

## 2. Dashboard por rol (`inicio/page.tsx`)
- [ ] 2.1 Leer `getUser()` → predicados `puedeProcesos/puedeClientes/puedeComercial/puedeContable`
      (espejo del sidebar; admin de empresa pasa todos).
- [ ] 2.2 Cargar SOLO los datos accesibles (`Promise.all` condicional; cada uno con `.catch`).
- [ ] 2.3 Render condicional: StatCards (clicables) + Vencimientos (procesos) + Pendientes
      (comercial) + Últimos clientes (clientes), cada bloque tras su predicado.
- [ ] 2.4 Fallback: sin módulos → saludo + acceso a Agenda / Mi Cuenta.

## 3. Verificación
- [ ] 3.1 `pnpm --dir lex-control-client build` verde + `tsc` limpio.
- [ ] 3.2 Smoke manual por rol: JURIDICO (procesos sí, contable no), CONTABLE (cartera sí,
      comercial no), COMERCIAL (clientes/alertas), admin (todo); clic en cada KPI navega.

## 4. Cierre
- [ ] 4.1 Commit (client + superrepo) + archivar (fusionar delta a specs/client-portal).
