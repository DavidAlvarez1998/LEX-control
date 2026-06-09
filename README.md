# LEX Control

Plataforma multi-tenant para bufetes de abogados: gestiona empresas cliente, el
catálogo de servicios y la facturación. Se compone de **3 proyectos** + un repo
paraguas que los agrupa con git submodules.

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
