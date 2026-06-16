# Tasks — client-landing-page

## Backend (lex-control-api) — public-marketing-api
- [ ] `modules/publico/publico.router.ts`: `GET /publico/planes` (sin auth) — planes `activo`
      ordenados por `orden`, proyección mínima `{clave,nombre,descripcion,precioMensual,modulos[],cuotas[]}`
- [ ] `POST /publico/solicitar-demo` (sin auth): zod body + honeypot → crea Prospecto(canalEntrada=WEB, estado=NUEVO)
- [ ] Montar `app.use("/publico", publicoRoutes)` antes del 404
- [ ] Tests (tests/publico.test.ts): planes ok + oculta inactivos + sin campos internos; demo crea prospecto, honeypot no-op, 400 inválido, ignora estado/empresa

## Frontend (lex-control-client) — public-landing
- [ ] Routing: mover `(dashboard)/page.tsx` → `(dashboard)/inicio/page.tsx`
- [ ] Repuntar a `/inicio`: redirect de login, ítem "Inicio" en `nav.tsx`, guard del dashboard, cualquier `href="/"`/`replace("/")`
- [ ] `app/page.tsx`: landing pública (usa root layout, sin sidebar); si hay sesión → CTA "Ir a mi portal"
- [ ] Componentes de landing: header público, hero+CTAs, grid de módulos, cómo funciona, planes (fetch público), form demo, footer
- [ ] `lib/publico-api.ts`: getPlanesPublicos() + solicitarDemo()
- [ ] Responsive + tema claro/oscuro; degradación si planes falla

## Verificar
- [ ] `pnpm build` API + cliente verdes
- [ ] Smoke API: GET /publico/planes (200 sin token, proyección) + POST solicitar-demo (crea prospecto, honeypot no-op)
- [ ] Manual: `/` muestra landing sin sesión; login → `/inicio`; demo capta lead en /prospectos

## Decisión
- [ ] commit / merge — pendiente decisión del usuario
