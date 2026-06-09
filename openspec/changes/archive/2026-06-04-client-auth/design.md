# Design: client-auth

## Architecture Decisions

### AD-1 — Reuse the admin session stack in the client app
**Decision:** Copy the proven admin shape (`lib/auth.ts` + `lib/api.ts` + `components/auth-guard.tsx` + `app/login/page.tsx`) into the client app, changing only storage keys and the role gate.
**Rationale:** Both apps already share an identical structure (CLAUDE.md). Consistency lowers maintenance cost and review effort; no new patterns to learn.
**Trade-off:** Some duplication across the two apps. A shared package is overkill now (no workspace tooling); revisit if a third consumer appears.

### AD-2 — Absolute 8h JWT, no refresh tokens
**Decision:** `TOKEN_TTL = "8h"`, stateless JWT, no refresh flow.
**Rationale:** Smallest change over the current stateless JWT; predictable; no Redis/DB session store needed.
**Trade-off:** No silent renewal (user re-logs in after 8h) and no server-side revocation. Documented as future work.

### AD-3 — Proactive expiry by decoding `exp` client-side
**Decision:** Base64url-decode the JWT payload (no signature verification) to read `exp`; on guard mount, redirect if already past; otherwise `setTimeout(remaining)` to auto-logout.
**Rationale:** Gives instant, idle-safe logout without backend changes. The API stays authoritative — a tampered `exp` still fails signature verification server-side (401).
**Trade-off:** A long single `setTimeout` can drift if the device sleeps; acceptable because the guard also re-checks on mount/route change and the API enforces on every call. (Optional hardening: re-check on `visibilitychange`.)

### AD-4 — Role separation in two layers
**Decision:** (1) API: `loginSchema` gains optional `audience`; the handler returns 401 if `usuario.rol !== audience`. (2) Frontend: each app sends its own `audience` and refuses to store a session of the wrong rol.
**Rationale:** API-level rejection is the real control; the frontend gate is fast UX feedback. Existing `requireRole` guards already protect every privileged route, so this is defense-in-depth, not the sole barrier.
**Trade-off:** Slightly more login logic. Negligible.

## JWT `exp` reader (shared shape, per app)
```ts
// Decodes the JWT payload WITHOUT verifying the signature — UX only.
// Returns the expiry in ms epoch, or null if unreadable.
export function getTokenExpiry(token: string): number | null {
  try {
    const [, payload] = token.split(".");
    const json = JSON.parse(
      atob(payload.replace(/-/g, "+").replace(/_/g, "/")),
    );
    return typeof json.exp === "number" ? json.exp * 1000 : null;
  } catch {
    return null;
  }
}

export function isExpired(token: string): boolean {
  const exp = getTokenExpiry(token);
  return exp === null ? true : Date.now() >= exp;
}
```

## AuthGuard with proactive expiry (both apps)
```ts
useEffect(() => {
  const token = getToken();
  if (!token || isExpired(token)) {
    clearSession();
    router.replace("/login");
    return;
  }
  setChecked(true);
  const ms = (getTokenExpiry(token) ?? 0) - Date.now();
  const timer = setTimeout(() => {
    clearSession();
    router.replace("/login");
  }, Math.max(0, ms));
  return () => clearTimeout(timer);
}, [router]);
```

## Backend login change (sketch)
```ts
// auth.schemas.ts
export const loginSchema = z.object({
  email: z.string().trim().email("Correo inválido"),
  password: z.string().min(1, "La contraseña es obligatoria"),
  audience: z.nativeEnum(Rol).optional(),
});

// auth.router.ts — after verifyPassword OK:
if (req.body.audience && usuario.rol !== req.body.audience) throw invalidas; // same generic 401

// auth.service.ts
const TOKEN_TTL = "8h";
```

## Dependency
A `CLIENTE` can only log in **after** they have a password. That is produced by the `user-management` change (activation link → `/activar` → `POST /auth/set-password`). `client-auth` assumes `user-management` is applied; otherwise client login always returns "Credenciales inválidas".

## Future Work (out of scope)
- Sliding/idle timeout + refresh tokens for silent renewal.
- Stateful sessions / token blocklist for server-side revocation ("cerrar sesión en todos los dispositivos").
- Re-check expiry on `visibilitychange` to harden against device sleep.
