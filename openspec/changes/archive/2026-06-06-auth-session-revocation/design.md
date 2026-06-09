# Design: Revoke Sessions on Credential Change + Enforce Account States

## Technical Approach
Today `requireAuth` is purely stateless: it only verifies the JWT signature and `exp`. So a reset password leaves the old password usable until the admin disables the account, and any token already minted stays valid for its full 8h TTL — even after a reset or a deactivation. We close both gaps with two additions: (1) a per-user `tokenVersion` integer embedded in the JWT (`tv`) that, when bumped, kills every previously issued token for that user; (2) a stateful `requireAuth` that loads the user by PK and rejects non-active, pending, or stale-version tokens. The login endpoint also gains a pending-gate so the old password dies the instant a reset is issued.

## Architecture Decisions

### Decision: Token versioning for revocation
**Choice**: Add `Usuario.tokenVersion Int @default(0)`. JWT payload becomes `{ sub, rol, tv }`. Bumping `tokenVersion` invalidates all tokens minted before the bump.
**Alternatives**: (a) A token denylist (store revoked jti, reject on match). (b) Rely only on the 8h TTL.
**Rationale**: A denylist needs storage plus background cleanup of expired entries; `tokenVersion` is a single indexed integer compared per request — no extra table, no cleanup. Relying on the TTL alone is exactly the status-quo bug: up to 8h of exposure and the old password stays valid the whole time. Versioning gives instant, deterministic revocation at the cost of one int per user.

### Decision: Stateful `requireAuth`
**Choice**: After verifying the JWT, fetch the user by id (indexed PK) and 401 unless **all** hold: user exists AND `activo === true` AND `activationToken === null` (not pending) AND `payload.tv === user.tokenVersion`.
**Alternatives**: Keep auth stateless and enforce state only at login.
**Rationale**: State enforced only at login leaves live sessions untouched — the whole point here is to revoke already-issued tokens mid-session. The cost is one PK lookup per authenticated request (cheap, indexed). If that ever shows up under load, a short-TTL (e.g. 30s) in-memory cache keyed by user id is a clean future optimization; noted as future work, not built now.

### Decision: Login pending-gate
**Choice**: `POST /auth/login` rejects with the same generic 401 when `activationToken != null`, in addition to the existing `!activo` check.
**Alternatives**: Leave login as-is and rely on the unusable password placeholder.
**Rationale**: On a reset, the account still has its real bcrypt password until the user completes activation. Without this gate the OLD password keeps working through the pending window. Gating on `activationToken != null` makes the old password unusable the moment a reset is issued. Same generic message ("Credenciales inválidas") so we don't leak account state.

### Decision: When to bump `tokenVersion`
**Choice**: Bump `tokenVersion` (increment by 1) in three places — `reset-password` (admin), `set-password` (activation completes), and any PATCH that flips `activo` from true to false.
**Alternatives**: Bump only on reset.
**Rationale**: Each is a credential/access change that must kill live sessions. Reset → invalidate the user's current tokens immediately. set-password → activation already clears `activationToken` and sets `activo=true`; the bump there kills any token minted during the pending window (e.g. a token issued before the gate, or a racing reset). Deactivation → instantly logs the user out rather than waiting for the stateful check alone (defense in depth; the `activo` check would also catch it, but the bump makes the intent explicit and survives if the active-check is ever relaxed).

### Decision: Do not scrub the password hash on reset
**Choice**: On `reset-password` leave the existing bcrypt hash in place; do not overwrite/clear it.
**Alternatives**: Replace the hash with an unusable placeholder ("belt and suspenders").
**Rationale**: The login pending-gate already blocks the old password (account is pending until activation), and `tokenVersion++` kills live sessions. Scrubbing the hash adds a write and a special case (the account would have no valid password until activation anyway, which the pending-gate already enforces) with no additional security benefit. We choose the simpler option and rely on the two mechanisms above.

## Data Flow
```
ADMIN reset:
  ADMIN ─POST /usuarios/:id/reset-password─▶ set activationToken=hash,
                                             activationExpires, tokenVersion++  (tv: N → N+1)
        ◀── { activationUrl }
  USUARIO next request with OLD token (tv=N):
        requireAuth → load user → user.tokenVersion=N+1 ≠ N  ─▶ 401
  USUARIO tries login with OLD password:
        activationToken != null  ─▶ 401 (generic)

Deactivation:
  ADMIN ─PATCH /usuarios/:id { activo:false }─▶ tokenVersion++ (true→false)
  USUARIO next request:
        requireAuth → user.activo=false  ─▶ 401  (and tv mismatch ─▶ 401)

Activation completes:
  USUARIO ─POST /auth/set-password─▶ password set, activationToken=null,
                                     activo=true, tokenVersion++
        ─▶ any token minted during pending window now stale ─▶ 401 on next request
```

## Schema delta (`Usuario`)
```prisma
tokenVersion  Int  @default(0)   // bump invalida todos los JWT emitidos antes
```

## Key contracts
```ts
// auth.service.ts
export type JwtPayload = { sub: string; rol: Rol; tv: number };

signToken({ sub: usuario.id, rol: usuario.rol, tv: usuario.tokenVersion });

// middleware/auth.ts — requireAuth (pseudocode)
const payload = verifyToken(token);            // 401 if bad signature / expired
const user = await prisma.usuario.findUnique({
  where: { id: payload.sub },
  select: { activo: true, activationToken: true, tokenVersion: true },
});
const tv = payload.tv ?? 0;                    // missing tv → treat as version 0
if (
  !user ||
  !user.activo ||
  user.activationToken !== null ||             // pending (post-reset / not activated)
  tv !== user.tokenVersion
) throw new HttpError(401, "Token inválido o expirado");
req.user = payload;
```

## File Changes
| File | Action |
|------|--------|
| `prisma/schema.prisma` | Modify (add `tokenVersion Int @default(0)`) + `pnpm push` / migrate |
| `src/modules/auth/auth.service.ts` | Modify (`JwtPayload` adds `tv`) |
| `src/modules/auth/auth.router.ts` | Modify (login pending-gate; `signToken` carries `tv`; `set-password` bumps `tokenVersion`) |
| `src/middleware/auth.ts` | Modify (`requireAuth` becomes stateful: PK lookup + active/pending/tv checks; now async) |
| `src/modules/usuarios/usuarios.router.ts` | Modify (`reset-password` bumps `tokenVersion`; PATCH bumps when `activo` true→false) |
| tests | Modify/Create (revocation + pending-gate + deactivation cases) |

## Testing Strategy
Integration with **vitest + supertest**, prisma mocked (as in existing tests). Because `requireAuth` now performs a DB lookup, the mock must cover `prisma.usuario.findUnique` for the middleware path — return a stub user with `{ activo, activationToken, tokenVersion }` per case. Cases:
- **reset → old token 401**: mint token at tv=N, mock reset bumps user to tv=N+1, old token request → 401.
- **reset → old password 401**: after reset (`activationToken != null`), login with old password → 401 generic.
- **login pending 401**: user with `activationToken != null` cannot log in.
- **deactivate → token 401**: PATCH `activo:false` bumps tv (and sets activo=false); old token request → 401.
- **happy path still 200**: active user, `activationToken=null`, `tv` matches → authenticated route returns 200.

## Migration / Rollout
Additive column with `@default(0)`: `pnpm push` (or `pnpm migrate`) backfills all existing rows to `tokenVersion = 0`, no data loss. Tokens already issued before this change carry no `tv` claim. **Decision: treat a missing `tv` as version 0** (`payload.tv ?? 0`) and compare against `user.tokenVersion`. Since every existing user is backfilled to 0, already-issued valid tokens keep working until they expire naturally (≤8h) — no forced re-login, smooth rollout. The alternative (force re-login by rejecting tokens with no `tv`) is more disruptive and unnecessary given the additive default. After the first credential event for a user, their version moves to ≥1 and old tokens stop matching as intended.

## Open Questions
- [ ] Should `requireAuth` get the short-TTL in-memory cache now, or defer until profiling shows the per-request PK lookup matters?
- [ ] Increment style for `tokenVersion`: `{ increment: 1 }` in the same `update` is atomic and preferred — confirm all three call sites use it rather than read-modify-write.
