# Tasks — client-landing-page

## Backend (lex-control-api) — public-marketing-api
- [x] `modules/publico/publico.router.ts`: `GET /publico/planes` (sin auth) — planes `activo`
      ordenados por `orden`, proyección mínima `{clave,nombre,descripcion,precioMensual,modulos[],cuotas[]}`
- [x] `POST /publico/solicitar-demo` (sin auth): zod body + honeypot → crea Prospecto(canalEntrada=WEB, estado=NUEVO)
- [x] Montar `app.use("/publico", publicoRoutes)` antes del 404
- [x] Tests (tests/publico.test.ts): planes ok + oculta inactivos + sin campos internos; demo crea prospecto, honeypot no-op, 400 inválido, ignora estado/empresa

## Frontend (lex-control-client) — public-landing
- [x] Routing: mover `(dashboard)/page.tsx` → `(dashboard)/inicio/page.tsx`
- [x] Repuntar a `/inicio`: redirect de login, ítem "Inicio" en `nav.tsx`, guard del dashboard, cualquier `href="/"`/`replace("/")`
- [x] `app/page.tsx`: landing pública (usa root layout, sin sidebar); si hay sesión → CTA "Ir a mi portal"
- [x] Componentes de landing: header público, hero+CTAs, grid de módulos, cómo funciona, planes (fetch público), form demo, footer
- [x] `lib/publico-api.ts`: getPlanesPublicos() + solicitarDemo()
- [x] Responsive + tema claro/oscuro; degradación si planes falla

## Verificar
- [x] `pnpm build` API + cliente verdes
- [x] Smoke API: GET /publico/planes (200 sin token, proyección) + POST solicitar-demo (crea prospecto, honeypot no-op)
- [x] Manual: `/` muestra landing sin sesión; login → `/inicio`; demo capta lead en /prospectos

## Decisión
- [x] commit / merge — pendiente decisión del usuario
