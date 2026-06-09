# Session Expiry Specification

> New capability introduced by change `client-auth`. Applies to **both** frontends (`lex-control-admin` and `lex-control-client`). Pairs with the 8h absolute JWT lifetime defined in the `authentication` delta.

## ADDED Requirements

### Requirement: Absolute Session Lifetime
A session MUST become invalid 8 hours after login regardless of activity. The frontend MUST treat the JWT `exp` claim as the source of truth for the local deadline.

#### Scenario: Token past expiry on load
- GIVEN a stored token whose `exp` is in the past
- WHEN the app (re)loads or a guarded route mounts
- THEN the session is cleared and the user is redirected to `/login` without making an API call

### Requirement: Proactive Auto-Logout
While a guarded view is mounted, the frontend MUST schedule an automatic logout at the token's `exp`, so an idle session is ended exactly at expiry (not only on the next user/API action).

#### Scenario: Idle tab reaches expiry
- GIVEN a guarded view open with a valid token
- WHEN the wall-clock passes the token's `exp` with no user interaction
- THEN the session is cleared and the user is redirected to `/login` automatically

#### Scenario: Timer cleared on unmount
- GIVEN a scheduled auto-logout timer
- WHEN the guarded view unmounts or the user logs out
- THEN the timer is cleared (no stray redirects)

### Requirement: Tamper Safety
The client-side `exp` read is a UX optimization only. A token with a forged/edited `exp` MUST still be rejected by the API on the next request (server verifies the signature), so client-side decoding MUST NOT be relied on for authorization.

#### Scenario: Forged exp still fails server-side
- GIVEN a token whose payload was edited to extend `exp`
- WHEN it is sent to a protected API route
- THEN the API returns 401 (signature verification fails)
- AND the frontend clears the session and redirects to `/login`
