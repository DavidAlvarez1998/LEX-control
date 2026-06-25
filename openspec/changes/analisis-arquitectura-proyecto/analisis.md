# Análisis de arquitectura — LEX Control (API + admin + client)

> Mapa de arquitectura del sistema completo, levantado el **2026-06-25** sobre la rama
> `feat/cuenta-clientes`. Complementa (no reemplaza) las specs canónicas
> `specs/api-architecture` y `specs/http-api-foundation`. Es una foto del estado real
> del código, útil para onboarding y para ubicar dónde tocar cada cosa.

## 1. Visión general

LEX Control es una **plataforma SaaS multi-tenant** para despachos jurídicos: gestiona
empresas (despachos), sus procesos legales, su CRM/comercial, su contabilidad y la
facturación. Son **tres proyectos independientes** (sin monorepo; cada uno con su
`package.json` y su ciclo propio):

| Proyecto | Paquete | Qué es | Puerto | Depende de @lex/db |
|---|---|---|---|---|
| `lex-control-api` | `@lex/db` | Capa de datos Prisma **+ servidor HTTP Express** | 4000 | — (es el dueño) |
| `lex-control-admin` | — | Consola Next.js para **ADMIN de plataforma** | 3000 | ❌ No (solo HTTP) |
| `lex-control-client` | — | Portal Next.js para **CLIENTE / despacho** | 3001 | ❌ No (solo HTTP) |

> ⚠️ Corrección a una creencia previa: **ningún frontend importa `@lex/db`**. Ambos
> hablan solo por HTTP con la API. Verificado en sus `package.json`.

**Dos niveles de tenencia/rol** que se reflejan en los dos frontends:
- **Plataforma** (`Usuario.rol`): `ADMIN` (staff, `empresaId=null`), `COMERCIAL` (vende
  planes), `USUARIO` (pertenece a un despacho). → consola admin.
- **Despacho** (`RolEmpresa`, varios por usuario): `ADMINISTRADOR`, `JURIDICO`,
  `CONTABLE`, `COMERCIAL`. + flag `esAdminEmpresa`. → portal client.

## 2. Topología: cómo se conectan

```
Navegador ──> Next admin :3000 ──(rewrite /api/* )──┐
                                                     ├──> Express API :4000 ──> MySQL (Prisma)
Navegador ──> Next client :3001 ─(rewrite /api/* )──┘                     └──> Integraciones externas
```

- **Proxy same-origin**: cada front reescribe `/api/:path*` → `API_PROXY_TARGET`
  (default `http://localhost:4000`) en `next.config.ts`. El navegador nunca ve el :4000
  → **sin CORS directo** y compatible con el túnel SSH (solo se forwardean 3000/3001).
- **Auth por JWT** (8 h): el front guarda token+user en `localStorage`
  (`lex_admin_*` / `lex_client_*`) y manda `Authorization: Bearer`. No hay refresh:
  vence por `exp` y el `AuthGuard` programa logout proactivo.
- **Sin Server Components de datos**: los fronts son casi todo Client Components con
  `fetch` desde el navegador (useState/useEffect). Next actúa solo como proxy + shell.

## 3. `lex-control-api` (@lex/db) — capa de datos + API

**Stack**: Express 4.21, Prisma 6.2 (MySQL), Zod 3.24, jsonwebtoken, bcryptjs, helmet,
cors, express-rate-limit, multer, prom-client, Vitest 2.1 + supertest, tsx (dev). OpenAPI
3 generado desde Zod (`@asteasolutions/zod-to-openapi` + swagger-ui).

**Arranque**: `src/server.ts` → `createApp()` (`src/app.ts`) → escucha en `env.port`
(4000). Apagado ordenado (SIGTERM/SIGINT → cierra server → `prisma.$disconnect`).

### 3.1 Arquitectura por capas (confirmada)

Patrón **router → service → repository → dto**, dependencias hacia adentro (ver
`specs/api-architecture`). Por módulo en `src/modules/<feature>/`:
- `*.router.ts` — HTTP puro (auth/RBAC, valida Zod, mapea DTO). **Sin `prisma.`**.
- `*.service.ts` — casos de uso, transacciones (`prisma.$transaction`). Recibe `TenantContext`, no toca Express.
- `*.repository.ts` — queries Prisma con **`empresaId` forzado en el constructor**.
- `*.dto.ts` / `*.schemas.ts` — forma de respuesta / validación + tipos (`z.infer`).

**22 módulos**: `auth`, `buscar`, `catalog`, `clientes`, `comercial`, `contable`,
`contratos`, `documentos`, `empresas`, `entitlements`, `facturacion`, `litigantes`,
`mi-empresa`, `notificaciones`, `planes`, `procesos`, `publico`, `rama-judicial`,
`roles`, `servicios`, `usuarios`, `ventas`.

### 3.2 Cross-cutting (`src/shared/` + `src/middleware/`)

- `shared/prisma.ts` — **singleton** PrismaClient; tipo `PrismaLike` para inyectar `tx`.
- `shared/tenant.ts` — `TenantContext { userId, rol, empresaId, esAdminEmpresa, rolesEmpresa }`; `empresaIdOrThrow`.
- `shared/errors.ts` — `mapPrismaError` (P2002→409, P2025→404, P2003→409).
- `shared/logger.ts` + `shared/request-context.ts` — log estructurado + `X-Request-Id` por `AsyncLocalStorage`.
- `shared/pagination.ts` — `{ items, total, page, pageSize }` **opt-in** (sin params → comportamiento previo).
- `shared/metrics.ts` — Prometheus en `GET /metrics`.
- `middleware/auth.ts` — `requireAuth` (JWT + **tokenVersion** para revocación instantánea), `requireRole`, `requireEmpresaAdmin`, `requirePermiso(clave)` (doble puerta: módulo contratado vía entitlements + RBAC por `RolEmpresa`).
- `middleware/{error,validate,async}.ts` — `HttpError`/handler central, validación Zod, `asyncHandler`.

### 3.3 Auth y multi-tenancy

- **Login** (`POST /auth/login`, con `audience` ADMIN|USUARIO) → JWT `{ sub, rol, tv }` 8 h.
- **Revocación**: cada request compara `tv` del token con `Usuario.tokenVersion`; reset /
  set-password / desactivación incrementan `tokenVersion` → matan todas las sesiones.
- **Scoping**: `empresaId` SIEMPRE sale del token, nunca del cliente; el repositorio lo
  inyecta en todo `where` → imposible fuga entre despachos. ADMIN plataforma = `empresaId null`.

### 3.4 Motor de procesos (dominio puro, testeable sin DB/HTTP)

En `src/modules/procesos/`:
- `maquina-etapas.ts` — `siguienteEtapaAuto` / `terminalDecidido` (auto-avance conservador).
- `esquema.ts` — tipos del **formulario dinámico** (CampoTipo: texto/textoLargo/numero/
  moneda/porcentaje/fecha/boolean/select/multiselect/listaCorreos) + `evaluarCondicion`
  (AND/OR/hoja, soporta multiselect).
- `diasHabiles.ts` — plazos hábiles/calendario (festivos CO).
- `plantilla.ts` + `plantillas-seed.ts` — catálogo semillero de tipos de proceso.
- `actuaciones.service.ts` + `hitos-actuaciones.ts` — sync con Rama Judicial → novedades → sugerir etapa/decisión.

### 3.5 Integraciones externas (cada una = su client aislado; secretos en env)

| Integración | Módulo | Dirección | Notas |
|---|---|---|---|
| **Rama Judicial (CPNU)** | `rama-judicial` | Lectura | `:448/api/v2`; User-Agent navegador, backoff, 404→null, batch+anti-rate-limit |
| **Notificaciones** | `notificaciones` | Escritura (**de cobro**) | host `10.10.10.211:5020`: correo (SES) ✅, llamadas (Go4 TTS) ✅, SMS (Háblame) ❌ no entrega |
| **Documental (Tecnovapp)** | `documentos` | Escritura | guarda solo `path` relativo; URL se reconstruye; carpeta `tenant/MÓDULO/AÑO/MES` (1 nivel) |

### 3.6 Tests

~35 `*.test.ts` (Vitest + supertest): dominio puro (maquina-etapas, esquema,
diasHabiles), servicios E2E contra DB de test, integraciones con mocks, auth/revocación,
flujos (laboral/verbal/ejecutivo), seeds.

## 4. Modelo de datos (`prisma/schema.prisma`, ~1.850 líneas, ~50 modelos)

IDs `cuid()`, tablas snake_case vía `@@map`. Por dominio:

- **Tenencia/auth**: `Empresa`, `Usuario` (enum `Rol`).
- **Servicios/planes/entitlements**: `Servicio`, `EmpresaServicio` (precio negociado),
  `Modulo`, `Permiso`, `RolEmpresaPermiso`, `UsuarioRolEmpresa`, `Plan`, `PlanModulo`,
  `PlanCuota`, `Suscripcion`, `SuscripcionModulo`, `SuscripcionCuota`.
- **Catálogo de procesos**: `AreaPractica`, `CategoriaProceso`, `TipoProceso`,
  `TipoProcesoArea`, `PlantillaDocumento` (enums `Jurisdiccion`, `GrupoProceso`,
  `Instancia`, `CuantiaTipo`, `TipoAreaPractica`).
- **Procesos (motor)**: `Proceso`, `EtapaProceso`, `DocumentoProceso`, `ActuacionProceso`,
  `Litigante`, `ParteProceso` (enums `EstadoProceso`, `RolParte`, `TipoPersona`,
  `NaturalezaJuridica`, `TipoDocumento`, `CategoriaDocumentoProceso`).
- **CRM despacho (comercial interno)**: `Cliente`, `SeguimientoComercial`,
  `ComisionDespacho`, `FaseComercialHistorial`, `Cotizacion`, `ContratoComercial`,
  `ConfiguracionCobro`, `SolicitudAsignacionProceso`.
- **Comercial de plataforma (venta de planes)**: `Prospecto`, `SeguimientoProspecto`,
  `Comision`. → ¡OJO! es **otro mundo** distinto al CRM del despacho.
- **Contable**: `Ingreso`, `Egreso`, `Nomina`, `CajaMenor`(+`Movimiento`), `ServicioFijo`,
  `ServicioFijoRecurrente`, `CuentaBancaria`, `Cartera`.
- **Facturación**: `Factura`, `FacturaItem`.
- **Contratos RRHH**: `Contrato`, `DocumentoContrato`.

## 5. `lex-control-admin` (consola plataforma, :3000)

**Stack**: Next 16.2.7 (App Router) + React 19.2.4 + Tailwind v4 + TS. Build `standalone`,
View Transitions on, proxy `/api`.

- **Rutas** (`src/app/(dashboard)/`): `/` (dashboard ADMIN vs COMERCIAL), `empresas`,
  `servicios`, `planes`, `catalogo-procesos`, `usuarios`, `comercial` (hub:
  prospectos/equipo/comisiones/contratos), `agenda`; `facturacion` y `api` = placeholders.
- **Nav** (`src/lib/nav.tsx`): `NAV_ITEMS` filtrado por rol (COMERCIAL ve Dashboard/
  Comercial/Agenda/Planes; ADMIN todo).
- **API client** (`src/lib/api.ts`): wrapper fetch, JWT en localStorage (`lex_admin_*`),
  401→logout, `errorMessage()` para issues Zod, `uploadFile()` multipart. `lib/ventas.ts`
  encapsula prospectos/comisiones/agenda.
- **UI** (`src/components/ui.tsx`): PageHeader, Button, Card, Modal/Tooltip (portal),
  MoneyInput, StatCard, EmptyState; `feedback.tsx` (confirm/notify); theme dark.
- **Conectado de verdad**: Dashboard, Empresas, Servicios, Planes, Catálogo de procesos,
  Usuarios, Comercial (prospectos/equipo/comisiones), Agenda. **Placeholder**: Facturación, API.

## 6. `lex-control-client` (portal despacho, :3001)

**Stack**: idéntico al admin (Next 16.2.7 / React 19 / Tailwind v4). Es una **variante
scoped a una empresa**.

- **Rutas** (`src/app/(dashboard)/`): `inicio`, `procesos` (+`nuevo`/`[id]`), grupos que
  redirigen a `procesos?grupo=…` (`peticiones`, `acciones-constitucionales`,
  `procesos-laborales`), `mis-procesos`, `clientes`, `agenda`, `contable` (shell de 8
  tabs en una página), `facturacion`, `servicios`, `contratos`, `equipo`, `cuenta`,
  `soporte`. Públicas: `/` (landing), `login`, `activar`.
- **Nav role-aware** (`src/lib/nav.tsx`): por `RolEmpresa`/`esAdminEmpresa`. **Refresh de
  roles en vivo**: `AuthGuard` llama `GET /auth/me` en cada navegación y al `focus` →
  `USER_CHANGED_EVENT` → sidebar/guards re-renderizan sin re-login. Guards:
  `RolEmpresaGuard`, `AdminEmpresaGuard`.
- **API client** (`src/lib/api.ts`, tokens `lex_client_*`) + APIs por dominio:
  `procesos-api.ts`, `comercial-api.ts`, `contable.ts`, `publico-api.ts`.
- **Componentes destacados**: `formulario-dinamico.tsx` (motor de forms condicionales,
  espejo del server), `datos-proceso.tsx` (ficha), `caso-chain.tsx` (DdP→reiteración→
  tutela), `novedades-campana.tsx` (campanita P17, deep-link `?conNovedades=1`),
  `documentos-uploader.tsx`, `components/contable/*` (8 tabs).
- **Conectado de verdad**: Procesos (JURIDICO), Clientes, Agenda/Comercial, Contable
  (CONTABLE), Equipo (admin-empresa). **Placeholder/stub**: Facturación, Servicios, Soporte.

## 7. Patrones transversales compartidos por los dos fronts

- Misma estructura `src/app` (route group `(dashboard)/` con `layout`+`template`),
  `src/components/ui.tsx`, `src/lib/{api,auth,nav,theme,format,view-transition}`.
- Tailwind v4 con tokens semánticos theme-aware; dark mode class-based; `MoneyInput`
  formato es-CO (1.000.000); modales portaleados (fix Firefox).
- View Transitions (~200ms crossfade) heredadas por todas las páginas vía `template.tsx`.

## 8. Madurez y deuda (referencias)

- **Backend muy maduro**: capas + tenancy + dominio puro + observabilidad + OpenAPI;
  ver programa "API perfecta" (`changes/api-production-grade`, `api-hardening`) y
  auditoría SOLID (`changes/api-arquitectura-solid`: pendiente dedup del motor de reglas
  API↔client).
- **Fronts**: muy conectados salvo facturación (ambos) y algunos stubs del client.
- **Deuda conocida**: `changes/` (auditoría malas prácticas: key={i}, setState-en-effect,
  N+1) y duplicación del motor de condiciones entre API y client.

## 9. Para ubicarse rápido (dónde tocar qué)

- Endpoint o regla de negocio → `lex-control-api/src/modules/<feature>/`.
- Cambio de modelo → `lex-control-api/prisma/schema.prisma` + `pnpm push` (NO `pnpm migrate`, resetea la DB).
- Pantalla admin → `lex-control-admin/src/app/(dashboard)/<seccion>/page.tsx`.
- Pantalla despacho → `lex-control-client/src/app/(dashboard)/<seccion>/`.
- Form de proceso / catálogo → `procesos/esquema.ts` (server) ↔ `formulario-dinamico.tsx` (client).
