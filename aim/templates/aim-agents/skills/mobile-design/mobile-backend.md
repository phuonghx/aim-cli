# Backend Patterns for Mobile Clients

> Backend concerns that are specific to mobile apps. General API and server practice lives elsewhere; this file is about what changes once the client is a phone.
> A mobile backend is not a web backend with a different skin — the constraints are different, so the patterns are too.

---

## What makes a mobile client different

```
A phone is not a browser tab:
  · the network is unreliable — cellular dead zones, lifts, trains
  · battery is finite — every radio wake-up costs
  · storage is limited — you cannot cache everything
  · sessions get interrupted — calls, notifications, backgrounding
  · devices vary enormously — from budget Androids to flagships
  · updates are slow — app-store review gates every binary fix
```

The backend has to absorb all of that on the client's behalf.

---

## Common missteps

| Reflex | Why it hurts mobile | Better |
|--------|---------------------|--------|
| One API shared with web | mobile wants lean payloads | mobile endpoints, or field selection |
| Returning full objects | wastes bandwidth and battery | partial responses, pagination |
| Ignoring offline | the app breaks with no signal | offline-first design, sync queues |
| WebSockets for everything | constant battery drain | push + polling fallback |
| No app versioning | cannot force fixes or block stale clients | version headers, minimum-version gate |
| Vague error strings | users cannot self-recover | error codes plus a recovery action |
| Server sessions | apps restart and lose them | tokens with refresh |
| No device metadata | impossible to debug field issues | device id and app version in headers |

---

## 1. Push notifications

### The delivery path

```
            Your backend
                 │
        ┌────────┴────────┐
        ▼                 ▼
   FCM (Google)      APNs (Apple)
        │                 │
        ▼                 ▼
   Android device    iOS device
```

### Push kinds

| Kind | Use | User sees |
|------|-----|-----------|
| Display | new message, order update | a banner |
| Silent | background sync | nothing |
| Data | app-defined handling | depends on app logic |

### Rules

- Push carries a pointer, not the payload: send "New message," then let the app fetch the content. Never put sensitive data in a push.
- Batch, dedupe, and respect quiet hours instead of flooding.
- Segment by preference, timezone, and locale rather than blasting everyone.
- Prune invalid tokens; a delivery error usually means an uninstall.
- For iOS, route through APNs — FCM alone does not guarantee iOS delivery.

### Token lifecycle

```
register on launch → obtain token → send to backend
tokens rotate      → re-register on each start
tokens expire      → drop from the database
uninstall          → token errors out → clean it up
multiple devices   → store several tokens per user
```

---

## 2. Offline sync and conflicts

### Pick a strategy by data type

```
read-only (news, catalog)     → cache with a TTL; ETag/Last-Modified to invalidate
single-owner (notes, todos)   → last-write-wins, or timestamp merge
collaborative (shared docs)    → CRDT or OT; consider a managed sync backend
critical (payments, stock)     → server is the source of truth; optimistic UI + confirmation
```

### Resolution approaches

| Approach | Mechanism | Fits |
|----------|-----------|------|
| last-write-wins | newest timestamp wins | simple, single-user data |
| server-wins | server is authoritative | critical transactions |
| client-wins | offline edits take priority | offline-heavy apps |
| field merge | combine per field | documents, rich content |
| CRDT | conflict-free by construction | real-time collaboration |

### The sync queue

```
Client
  · edit → write to the local DB
  · enqueue { action, data, timestamp, retries }
  · when online → drain the queue in order
  · success → dequeue
  · failure → back off and retry (cap the attempts)
  · conflict → apply the chosen resolution

Server
  · accept the change with its client timestamp
  · compare against the stored version
  · resolve
  · return the merged state
  · client overwrites local with the server's answer
```

---

## 3. Trimming API responses

| Technique | Typical saving | How |
|-----------|----------------|-----|
| field selection | 30-70% | `?fields=id,name,thumbnail` |
| compression | 60-80% | gzip / brotli |
| pagination | varies | cursor-based |
| image variants | 50-90% | `/image?w=200&q=80` |
| delta sync | 80-95% | only records changed since a timestamp |

### Cursor pagination, not offset

```
Offset (poor for mobile)
  page 1: OFFSET 0  LIMIT 20
  page 2: OFFSET 20 LIMIT 20
  → an insert shifts everything → duplicates
  → large offsets get slow

Cursor (good for mobile)
  first: ?limit=20
  next:  ?limit=20&after=eyJpZCI6...
  → the cursor encodes id + sort keys
  → stable under inserts, consistent speed
```

### Batch round-trips

```
Instead of three calls (three latencies):
  GET /users/1
  GET /users/2
  GET /users/3

Send one:
  POST /batch
  { "requests": [
      { "method": "GET", "path": "/users/1" },
      { "method": "GET", "path": "/users/2" },
      { "method": "GET", "path": "/users/3" }
  ]}
```

---

## 4. App versioning

A config endpoint lets you steer clients without shipping a build.

```
GET /api/app-config
  X-App-Version: 2.1.0
  X-Platform: ios
  X-Device-ID: 7f3a...

{
  "minimum_version": "2.0.0",
  "latest_version": "2.3.0",
  "force_update": false,
  "update_url": "https://apps.apple.com/...",
  "feature_flags": { "new_player": true, "dark_mode": true },
  "maintenance": false,
  "maintenance_message": null
}
```

```
client >= minimum  → run normally
client <  minimum  → show a blocking force-update screen
client <  latest   → offer an optional update

feature flags → toggle features without a release, A/B test, roll out gradually (10% → 50% → 100%)
```

---

## 5. Authentication

```
Access token
  · short-lived (15 min - 1 hour)
  · held in memory, not persisted
  · sent on every request
  · refreshed when it expires

Refresh token
  · long-lived (30-90 days)
  · stored in SecureStore / Keychain
  · used only to mint a new access token
  · rotated on each use

Device token
  · identifies this device
  · powers "log out everywhere"
  · stored beside the refresh token
  · server tracks the active set
```

### Silent refresh

```
request with the access token
  401?
    have a refresh token?
      yes → POST /auth/refresh
              success → retry the original request
              failure → force logout
      no  → force logout
    (an expired-but-valid token refreshes invisibly)
  ok → continue
```

---

## 6. Error handling

Mobile errors should be machine-readable, human-readable, and actionable:

```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Your payment was declined",
    "user_message": "Check your card details or try another payment method",
    "action": { "type": "navigate", "destination": "payment_methods" },
    "retry": { "allowed": true, "after_seconds": 5 }
  }
}
```

| Status | Meaning | Client behavior |
|--------|---------|-----------------|
| 400-499 | client error | show the message, prompt an action |
| 401 | auth expired | silent refresh or re-login |
| 403 | forbidden | show an upgrade/permission screen |
| 404 | not found | drop it from the local cache |
| 409 | conflict | surface a sync-conflict UI |
| 429 | rate limited | honor Retry-After, back off |
| 500-599 | server error | retry with backoff, "try later" |
| network | offline | use cache, queue for sync |

---

## 7. Media and large files

### Images on demand

```
GET /images/{id}?w=400&h=300&q=80&format=webp

  · resize on the fly or via CDN
  · WebP for Android, HEIC for newer iOS, JPEG fallback
  · Cache-Control: max-age=31536000
```

### Resumable chunked upload

```
1. POST /uploads/init      { filename, size, mime_type } → { upload_id, chunk_size }
2. PUT  /uploads/{id}/chunks/{n}   upload 1-5 MB pieces, resumable
3. POST /uploads/{id}/complete     server assembles → final URL
```

### Adaptive streaming

```
needs: HLS for iOS, HLS or DASH for Android, multiple bitrates,
       range requests for seeking, downloadable chunks for offline

GET /media/{id}/manifest.m3u8
GET /media/{id}/segment_{n}.ts
GET /media/{id}/download
```

---

## 8. Security

### Attestation

```
prove it is a real device, not an emulator or bot:
  iOS     → DeviceCheck, verified server-side with Apple
  Android → Play Integrity, verified server-side with Google
fail closed: reject when attestation fails
```

### Request signing

```
Client
  signature = HMAC(timestamp + path + body, secret)
  X-Signature, X-Timestamp, X-Device-ID

Server
  timestamp within 5 minutes?
  recompute the signature from the same inputs
  compare; reject on mismatch (tampering)
```

### Rate limiting

```
scope per device, per user, per endpoint; prefer a sliding window

X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
Retry-After: 60   (on 429)
```

---

## 9. Observability

### Headers every mobile request should carry

```
X-App-Version: 2.1.0
X-Platform: ios | android
X-OS-Version: 17.0
X-Device-Model: iPhone15,2
X-Device-ID: <persistent uuid>
X-Request-ID: <per-request uuid for tracing>
Accept-Language: en-GB
X-Timezone: America/Sao_Paulo
```

### Log and alert

```
log per request: the headers above, endpoint/method/status,
                 response time, error detail, user id if known

alert on: error rate > 5% for a version
          p95 latency > 2s
          a crash spike on one version
          an auth-failure spike (possible attack)
          a push-delivery failure spike
```

---

## Checklist

**Before API design** — mobile-specific needs identified, offline behavior planned, sync strategy chosen, bandwidth limits considered.

**Each endpoint** — response as small as possible, cursor pagination, correct cache headers, error format with an action.

**Auth** — refresh implemented, silent re-auth flow, multi-device logout, secure-storage guidance for the client.

**Push** — FCM and APNs configured, token lifecycle managed, silent vs display defined, no sensitive data in the payload.

**Release** — version-check endpoint live, feature flags wired, force-update path, observability headers required.

---

> The backend must shrug off bad networks, spare the battery, and recover gracefully from interrupted sessions. The client cannot be trusted — but it also cannot be left stranded, so give it offline capability and a clear path out of every error.
