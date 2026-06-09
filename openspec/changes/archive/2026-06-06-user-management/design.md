# Design: User Management + Activation Link

## Technical Approach
Add a `usuarios` feature module (same convention as servicios/empresas) and extend auth with a public `set-password`. Activation uses a high-entropy random token; only its SHA-256 hash is stored. The raw token is returned to the admin (no email yet) to build `${CLIENT_URL}/activar?token=…`.

## Architecture Decisions

### Decision: SHA-256 for activation token, bcrypt for passwords
**Choice**: Store `sha256(token)` in `activationToken`; passwords stay bcrypt.
**Alternatives**: bcrypt the token.
**Rationale**: Tokens are 32 random bytes (high entropy) → a fast hash is safe and lets us look up by `where activationToken = sha256(raw)`. bcrypt is for low-entropy human passwords.

### Decision: No separate "pending" flag
**Choice**: Pending = `activationToken != null`. A pending user has an unusable password placeholder, so login (bcrypt compare) fails until activation.
**Rationale**: Avoids extra state; `activo` stays for enable/disable.

### Decision: Activation page in the client app
**Choice**: `lex-control-client/src/app/activar/page.tsx` (public).
**Rationale**: Clients live in the client app. Adds a minimal `lib/api` call there; full client login is a later change.

## Data Flow
```
ADMIN ─POST /usuarios─▶ create user, token=rand32,
                        store sha256(token), password=<unusable>
        ◀── { user, activationUrl: CLIENT_URL/activar?token=raw }
ADMIN shares link ─▶ USUARIO opens /activar?token=raw
USUARIO ─POST /auth/set-password {token,password}─▶
        find by sha256(token), check expiry, set bcrypt password,
        clear activationToken/Expires  ─▶ can now log in
```

## Schema delta (`Usuario`)
```prisma
activationToken   String?   @unique   // sha256 del token; null = activado
activationExpires DateTime?
```
`password` becomes effectively optional in practice (placeholder for pending users) but stays `String` (set to a random non-bcrypt string on create so login fails).

## Key contracts
```ts
// POST /usuarios (ADMIN)
{ email, nombre, empresaId, rol?, esAdminEmpresa? }
→ { user, activationUrl }

// POST /usuarios/:id/reset-password (ADMIN)
→ { activationUrl }

// POST /auth/set-password (public)
{ token, password } → { ok: true }   // 400 invalid/expired, 422 weak password

// GET /usuarios?empresaId= (ADMIN) → Usuario[] with estado derived, no password
```

## File Changes
| File | Action |
|------|--------|
| `prisma/schema.prisma` | Modify (2 columns) + `pnpm push` |
| `src/modules/usuarios/usuarios.router.ts` / `.schemas.ts` | Create |
| `src/modules/auth/auth.router.ts` + `auth.service.ts` | Modify (set-password, token helpers) |
| `src/config/env.ts` | Modify (`CLIENT_URL` for building the link) |
| `src/app.ts` | Modify (mount `/usuarios`) |
| `admin .../usuarios/page.tsx` | Modify (list/create/reset UI) |
| `client .../activar/page.tsx` + `client lib/api.ts` | Create |
| tests | Create (usuarios + set-password) |

## Testing Strategy
Integration (vitest+supertest, prisma mocked): create→link, set-password happy/expired/invalid, list/role guards, reset.

## Migration / Rollout
Additive nullable columns → `pnpm push`, no data loss. Existing users keep working (activationToken null = already active).

## Open Questions
- [ ] `CLIENT_URL` default = `http://localhost:3001` (configurable via env) — OK?
- [ ] Min password policy for set-password (length ≥ 8)?
