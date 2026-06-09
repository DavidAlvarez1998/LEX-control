# Design: Client Portal

## Technical Approach
Two small, additive backend changes plus client wiring. Login gains an optional `audience`
discriminator; a new USUARIO-scoped `/mi-empresa` endpoint exposes the caller's company.
The client portal (already scaffolded with login + AuthGuard) is wired to real data.

## Architecture Decisions

### Decision: `audience` is a portal guard, not authorization
**Choice**: `POST /auth/login` accepts optional `audience` (`z.nativeEnum(Rol)`). If present
and `usuario.rol !== audience`, throw the SAME generic 401 used for bad credentials.
**Alternatives**: separate login endpoints per portal; a distinct 403 status.
**Rationale**: One endpoint stays simple. The generic 401 avoids leaking that the
credentials were valid-but-wrong-portal. Real data protection remains per-endpoint via
`requireRole` — `audience` only stops a user from loading the wrong SPA shell.

### Decision: Scoped `/mi-empresa` instead of relaxing `/empresas/:id`
**Choice**: New `GET /mi-empresa` resolves the company from `req.user.sub` (look up the
user, read its `empresa`). `requireRole(USUARIO)`.
**Alternatives**: allow USUARIO on `/empresas/:id` when `id === own empresaId`.
**Rationale**: The client never supplies an id, so there is no ownership check to get
wrong. ADMIN-only `/empresas` routes stay single-audience and unchanged.

### Decision: empresaId stays out of the JWT
**Choice**: JWT remains `{ sub, rol }`; `/mi-empresa` does one extra lookup to reach the
company.
**Rationale**: Keeps the token minimal and avoids staleness if a user is reassigned; the
extra query is cheap and only on the portal read path.

## Data Flow
```
USUARIO ─POST /auth/login {email,password,audience:"USUARIO"}─▶ rol must == USUARIO
        ◀── { token, user }
USUARIO ─GET /mi-empresa (Bearer)─▶ find usuario by sub → its empresa + active servicios
        ◀── { id, nombre, rfc, email, telefono, activo, servicios:[{..., servicio}] }
```

## Key Contracts
```ts
// POST /auth/login  — audience optional
{ email, password, audience?: "ADMIN" | "USUARIO" }
→ 200 { token, user: { id, nombre, email, rol, esAdminEmpresa } }
  | 401 (bad creds OR portal mismatch) | 400 (invalid body)
// The portal derives an "Acceso" label from the session: rol ADMIN → "Administrador de
// plataforma"; else esAdminEmpresa ? "Administrador" : "Usuario" (the raw rol USUARIO is
// not shown to end users — it reads as confusing in the tenant portal).

// GET /mi-empresa (USUARIO)
→ 200 Empresa & { servicios: EmpresaServicio[] with nested servicio }
→ 401 (no token) | 403 (not USUARIO) | 404 (no empresa associated)
```

## Testing Strategy
Integration (vitest + supertest, prisma mocked): audience match/mismatch on login;
`/mi-empresa` 401/403/404/200 including the assertion that the lookup uses the token `sub`.

## Open Questions
- [ ] Billing model for the `facturacion` page (base + per-unit usage) — deferred to a later change.
