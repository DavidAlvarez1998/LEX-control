# LEX Control

Plataforma multi-tenant de gestión para bufetes de abogados. Cubre la operación de
punta a punta: cartera de **clientes y CRM comercial**, **procesos legales** por
jurisdicción (civil, laboral, constitucional/tutela, derecho de petición…) con
catálogo data-driven y motor de documentos, **agenda**, **facturación**, **contable**
y **contratos**, además de integraciones externas (Rama Judicial, notificaciones,
documental). Se compone de **3 proyectos** + un repo paraguas que los agrupa con git
submodules.

```
┌──────────────────────┐      ┌──────────────────────┐
│  lex-control-admin    │      │  lex-control-client   │
│  Next.js  :3000       │      │  Next.js  :3001       │
│  (rol ADMIN)          │      │  (rol CLIENTE)        │
└──────────┬───────────┘      └──────────┬───────────┘
           │           HTTP / JWT          │
           └──────────────┬───────────────┘
                          ▼
              ┌────────────────────────┐
              │  lex-control-api        │  Express + Prisma
              │  :4000                  │
              └───────────┬────────────┘
                          ▼
                     MySQL "LEX"
```

## Estructura de repos (4)

```
org/
├─ lex-control-api      ← backend Express + capa de datos Prisma (@lex/db)
├─ lex-control-admin    ← panel de administración (Next.js)
├─ lex-control-client   ← portal del cliente (Next.js)
└─ lex-control          ← este repo (paraguas): submodules + docs + compose
```

## Módulos

Lo que hace cada portal (la barra lateral es la guía).

**Admin (`:3000`, rol ADMIN de plataforma):**

| Módulo | Qué hace |
|--------|----------|
| Empresas | Despachos cliente (tenants): alta, datos, activación |
| Servicios | Catálogo global de servicios y precio base |
| Planes | Planes de suscripción y asignación a despachos |
| Catálogo de procesos | Tipos de proceso data-driven por jurisdicción (campos + flujo + plantillas) |
| Facturación | Facturas e ítems a despachos |
| API | Estado/documentación de la API |
| Usuarios | Usuarios de plataforma y roles |
| Comercial | CRM: funnel, prospectos, comisiones |
| Agenda | Calendario de actividades |

**Client (`:3001`, usuarios CLIENTE del despacho):**

| Módulo | Qué hace |
|--------|----------|
| Clientes | Cartera de clientes del despacho (CRM) |
| Procesos | Procesos legales: ficha por etapa, documentos, integración Rama Judicial |
| Agenda | Vencimientos y actividades |
| Servicios | Servicios contratados |
| Contable | Ingresos/egresos/nómina/caja/cartera |
| Facturación | Facturas del despacho |
| Contratos | Contratos (RR. HH.) |
| Equipo | Gestión del equipo del despacho |
| Mi Cuenta | Perfil del usuario |

## Requisitos

- Node.js 22+
- pnpm
- Acceso a la base MySQL

## Clonar todo

```bash
git clone --recurse-submodules <url-del-paraguas>
cd lex-control
```

Si ya clonaste sin `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

## Variables de entorno

**Nunca se commitean** (están en `.gitignore`). Cada quien las crea localmente.

`lex-control-api/.env`:
```bash
DATABASE_URL="mysql://USUARIO:CLAVE@HOST:3306/LEX?connection_limit=10&allowPublicKeyRetrieval=true"
PORT=4000
JWT_SECRET="<generá uno: openssl rand -hex 32>"
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"   # opcional (este es el default)
```

`lex-control-admin/.env.local` y `lex-control-client/.env.local`:
```bash
NEXT_PUBLIC_API_URL="http://localhost:4000"
```
> `JWT_SECRET` y `DATABASE_URL` van **solo** en el API. Nunca en los fronts.

## Primera vez

```bash
# Backend
cd lex-control-api
pnpm install
pnpm generate          # genera el cliente Prisma (repetir después de cada pnpm install)
pnpm push              # sincroniza el esquema con la BD (sin migraciones)

# Crear el primer ADMIN (las credenciales las elegís vos, no se guardan en el repo)
ADMIN_EMAIL=admin@lex.com ADMIN_PASSWORD="TuClave" ADMIN_NOMBRE="Administrador" pnpm seed:admin

# (opcional) sembrar el catálogo de servicios
pnpm seed

# Frontends
cd ../lex-control-admin  && pnpm install
cd ../lex-control-client && pnpm install
```

## Levantar todo (3 terminales)

```bash
cd lex-control-api     && pnpm dev    # API   → http://localhost:4000
cd lex-control-admin   && pnpm dev    # admin → http://localhost:3000
cd lex-control-client  && pnpm dev    # client→ http://localhost:3001
```

Abrí `http://localhost:3000`, te redirige a `/login`, entrás con el ADMIN sembrado.

## Con Docker

Dos stacks de Compose en la raíz del paraguas.

### Dev — todo con un comando

Levanta `api` + `admin` + `client` con hot-reload (bind-mount del código,
`tsx watch` / `next dev`). **No hay contenedor de MySQL:** el API se conecta a la
**base real** vía `DATABASE_URL` de `lex-control-api/.env` — igual que `pnpm dev`
sin Docker, así que ves todos tus usuarios y datos reales.

```bash
docker compose -f docker-compose.dev.yml up -d     # primer arranque instala deps (lento una vez)
docker compose -f docker-compose.dev.yml ps        # ver estado | logs -f api para seguir un servicio
docker compose -f docker-compose.dev.yml down      # bajar (down -v también borra los volúmenes de deps)
```

Puertos: admin `:3000`, client `:3001`, api `:4000`. Los cambios de código se
reflejan en caliente (no hace falta reconstruir ni reiniciar).

> ⚠️ Como dev apunta a la **base real**, **no corras `pnpm push`/`pnpm migrate`**
> desde el contenedor salvo que quieras modificar (o resetear, en el caso de
> `migrate`) esa base. Entrá con tus usuarios reales y su contraseña de siempre.

**Store de pnpm compartido:** los 3 contenedores comparten un único store (volumen
`pnpm-store`, vía `npm_config_store_dir=/pnpm-store`) → cada paquete se descarga una
sola vez y el store no se escribe dentro de los proyectos. Configurado solo en el
compose de la raíz; los submódulos no se tocan.

> Si querés una base **aislada de juguete** en lugar de la real (pruebas/CI), se
> puede agregar un servicio `mysql` al compose y apuntarle `DATABASE_URL` —
> ahí sí `pnpm push` + `pnpm seed:admin` para sembrarla.

### Prod — imágenes construidas

Imágenes multi-stage (API: `tsc` → `node dist/server.js`; fronts: Next.js
`output: "standalone"`), no-root, con `tini` y healthchecks. **Sin** contenedor de
MySQL: el API apunta a la BD externa vía `DATABASE_URL` (en `lex-control-api/.env`).

```bash
docker compose up -d --build          # usa docker-compose.yml (prod) por defecto
```

> **No auto-migra.** La BD se maneja con `pnpm push`, nunca `prisma migrate dev`
> (resetea la BD). Aplicá cambios de esquema a mano contra la BD destino.

> **Gotcha Next:** `rewrites()` se evalúa en build, así que `API_PROXY_TARGET` queda
> horneado en la imagen. En prod se pasa como build arg (`http://api:4000`).

### `.env.example` (no se pudieron commitear por el bloqueo de `.env*`)

El repo bloquea la escritura de cualquier `.env*`. Creá estos archivos a mano
(`.gitignore` permite `!.env.example`):

**`lex-control-api/.env.example`**
```bash
DATABASE_URL="mysql://user:password@host:3306/LEX"
JWT_SECRET="change-me-to-a-long-random-string"   # requerido (el server sale si falta)
PORT=4000
NODE_ENV=development
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
CLIENT_URL="http://localhost:3001"
ADMIN_URL="http://localhost:3000"
# Externos (opcionales, defaults en config/env.ts):
# DOCUMENTOS_API_URL, DOCUMENTOS_RAIZ_PREFIJO, NOTIFICAR_API_URL, RAMA_JUDICIAL_URL
```

**`lex-control-admin/.env.example`** y **`lex-control-client/.env.example`**
```bash
# Target del proxy /api/* (next.config.ts). En Docker = http://api:4000.
# OJO: con `next build` queda horneado (pasalo como build arg).
API_PROXY_TARGET=http://localhost:4000
```

## Scripts del API (`lex-control-api`)

| Script | Qué hace |
|--------|----------|
| `pnpm dev` | Servidor en watch (tsx), puerto `PORT` |
| `pnpm build` / `pnpm start` | Compila a `dist/` y lo ejecuta |
| `pnpm test` | Tests de integración (vitest + supertest) |
| `pnpm generate` | Regenera el cliente Prisma |
| `pnpm push` | Sincroniza esquema con la BD (sin migraciones) |
| `pnpm seed` | Siembra el catálogo de servicios |
| `pnpm seed:admin` | Crea/actualiza el ADMIN (requiere `ADMIN_EMAIL`/`ADMIN_PASSWORD`) |
| `pnpm studio` | Explorador visual de la BD (Prisma Studio) |

## Trabajar con submodules (día a día)

Cada proyecto es un repo normal **dentro de su carpeta**:

```bash
cd lex-control-api
# ...editás, commiteás y pusheás a SU repo como siempre...
git add -A && git commit -m "feat: ..." && git push
```

El paraguas guarda **a qué commit** apunta cada submódulo. Tras avanzar un proyecto:

```bash
# en la raíz (paraguas)
git add lex-control-api          # mueve el puntero al nuevo commit
git commit -m "chore: bump api" && git push
```

Traer lo último de todos los submódulos:

```bash
git submodule update --remote --merge
```

> Regla de oro: en el paraguas, los submódulos se gestionan con `git submodule`
> (no con `git add -A` indiscriminado).
