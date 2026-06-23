# Testing API Security

> How to probe an API for weaknesses, organized around the OWASP API risks plus authentication and authorization checks.

---

## The OWASP API risk list

| Risk | Where to poke |
|------|---------------|
| **API1 — Object-level authz (BOLA)** | Reaching another user's records by ID |
| **API2 — Broken authentication** | Tokens, sessions, credential handling |
| **API3 — Object property authz** | Mass assignment, over-exposed fields |
| **API4 — Resource consumption** | Missing throttling, denial of service |
| **API5 — Function-level authz** | Admin-only routes, role bypass |
| **API6 — Business-flow abuse** | Gaming the workflow, scripted misuse |
| **API7 — SSRF** | Coaxing the server to hit internal hosts |
| **API8 — Misconfiguration** | Open debug routes, lax CORS |
| **API9 — Inventory gaps** | Forgotten endpoints, stale versions |
| **API10 — Unsafe upstream use** | Blindly trusting third-party responses |

---

## Probing authentication

### Tokens (JWT)

| Area | What to try |
|------|-------------|
| Algorithm | `none`, swapping the signing algorithm |
| Secret | Weak keys, offline cracking |
| Claims | Expiry, issuer, audience checks |
| Signature | Tampering, injecting your own key |

### Sessions

| Area | What to try |
|------|-------------|
| Issuance | Can identifiers be predicted? |
| Storage | How safely is it held client-side? |
| Lifetime | Is the timeout actually enforced? |
| Teardown | Does logout truly kill the session? |

---

## Probing authorization

| Angle | Method |
|-------|--------|
| **Sideways** | Reach a peer's data at the same privilege |
| **Upward** | Reach functions above your role |
| **Out of scope** | Reach things outside your granted scope |

### Walking a BOLA / IDOR check

1. Spot the resource identifiers in the traffic.
2. Record a request authenticated as user A.
3. Replay it carrying user B's credentials.
4. Confirm whether B got into A's data.

---

## Probing input handling

| Injection | Where it bites |
|-----------|----------------|
| SQL | Bending the query |
| NoSQL | Manipulating document filters |
| Command | Slipping in shell commands |
| LDAP | Tampering with directory lookups |

**Method:** hit every parameter, coerce types, push past boundaries, and read what the error messages reveal.

---

## Probing the rate limiter

| Question | Check |
|----------|-------|
| Present? | Is any cap enforced at all? |
| Evadable? | Can spoofed headers or rotating IPs slip past? |
| Scoped how? | Per user, per IP, or one global bucket? |

**Evasion tricks worth trying:** `X-Forwarded-For` spoofing, alternate HTTP verbs, casing tweaks on the path, hitting a different API version.

---

## GraphQL specifics

| Test | Aim |
|------|-----|
| Introspection | Leaking the schema |
| Batching | Overloading via many ops at once |
| Nesting | Depth-driven denial of service |
| Authorization | Access enforced per field |

---

## Review checklist

**Authentication**
- [ ] Attempt to bypass it
- [ ] Gauge credential strength
- [ ] Confirm tokens are sound

**Authorization**
- [ ] Run BOLA / IDOR checks
- [ ] Try to escalate privilege
- [ ] Verify function-level gates

**Input**
- [ ] Exercise every parameter
- [ ] Hunt for injection

**Configuration**
- [ ] Inspect CORS
- [ ] Check security headers
- [ ] See how errors are handled

---

> **Bottom line:** APIs hold up modern software. Probe them the way an attacker would, before one does.
