---
name: multiplayer
description: Guidance for networked multiplayer game systems, covering topology choice, state and input synchronization, latency hiding, bandwidth budgets, server-side authority, anti-cheat, and matchmaking trade-offs. Use it when picking between dedicated, host-based, or peer networking, when remote players jitter or rubber-band, when deciding what to replicate and how often, or when hardening gameplay against cheating clients.
---

# Networked Multiplayer

Practical reference for wiring up a multiplayer game: where authority lives, how clients stay in sync, how to spend bandwidth wisely, and how to keep cheaters from rewriting the rules.

## Picking a topology

Match the network model to how the game is actually played:

- **Twitch / ranked PvP** (fighting games, shooters, racing) -> run an **authoritative dedicated server**. Players never talk directly; the server owns the truth.
- **Drop-in co-op or friendly lobbies** -> use a **listen server**, where one player's machine doubles as host. Cheap and quick to stand up.
- **Turn-by-turn play** (card games, async strategy) -> a **plain client-server** loop is plenty; no tight timing budget.
- **Persistent worlds at scale** (MMO) -> spread load across **sharded / distributed servers**, each owning a region or instance.

How the three common hosting styles stack up:

| Model | Round-trip latency | Operating cost | Cheat resistance |
|-------|-------------------|----------------|------------------|
| Dedicated server | Consistently low | Expensive to host | High |
| Peer-to-peer | Unpredictable | Nearly free | Poor |
| Listen / host-based | Middling | Cheap | Moderate |

The pattern: spend money to buy latency and trust. P2P flips that — it costs almost nothing but gives up both.

## Keeping clients in sync

Two opposite philosophies, plus the blend almost everyone ships:

| Strategy | What travels the wire | Where it shines |
|----------|----------------------|-----------------|
| State replication | Snapshots of the world (positions, HP, flags) | Small object counts, easy to reason about |
| Lockstep / input replication | Just the button presses, replayed in lockstep | Deterministic RTS and fighting games |
| Hybrid | Inputs locally, state for everyone else | The default for most titles |

### Hiding the latency

Even on a dedicated server, the round trip is real. Four techniques paper over it:

- **Client-side prediction** — the local player moves the instant a key is pressed, guessing what the server will confirm, so input feels immediate.
- **Entity interpolation** — remote characters are rendered a beat in the past, blending between received snapshots so they glide instead of teleporting.
- **Server reconciliation** — when a prediction turns out wrong, the client quietly snaps back and re-simulates from the authoritative state.
- **Lag compensation** — for hit registration the server rolls the world back to what the *shooter* saw at fire time, so well-aimed shots count despite ping.

A concrete flow: a player with 90 ms ping fires. Locally the shot leaves instantly (prediction). The server receives it, rewinds enemies ~90 ms (lag compensation), checks the hit against that older snapshot, then broadcasts the result; everyone else sees the victim react a frame late but smoothly (interpolation).

## Spending bandwidth wisely

You will run out of bytes before you run out of things to send. Trim aggressively:

| Technique | What it buys you |
|-----------|------------------|
| Delta encoding | Transmit only fields that changed since the last ack |
| Quantization | Drop float precision — a position rarely needs 32 bits per axis |
| Prioritization | Push the urgent stuff (an incoming grenade) ahead of cosmetic updates |
| Area of interest / relevancy | Replicate only entities the player could plausibly perceive |

Tune send frequency to how fast each value matters:

| Data | Suggested cadence |
|------|-------------------|
| Movement / transforms | ~20-60 Hz, tick-dependent |
| Health & damage | Event-driven, on change |
| Inventory / loadout | Event-driven, on change |
| Text chat | Only when a message is sent |

## Authority and anti-cheat

The bedrock rule: the client is an attacker's playground, so it gets no say over outcomes. Treat every inbound packet as a *claim* the server must prove.

When a client reports "my rocket killed them," the server independently asks:

1. Did a projectile with that trajectory actually intersect the target?
2. Was the firing player in a state allowed to shoot (alive, not stunned, weapon ready)?
3. Is the timestamp physically plausible, or is it impossibly fast?

Common exploits map cleanly onto server-side checks:

| Exploit | Server-side defense |
|---------|--------------------|
| Speed hacking | Validate movement deltas against allowed velocity |
| Aimbot | Re-verify line of sight and target visibility |
| Item duplication | Keep inventory entirely server-owned; clients only request |
| Wallhack | Never transmit data for entities the player cannot see |

That last row is the strongest lever: an exploit is impossible if the cheating client was never handed the information in the first place.

## Matchmaking trade-offs

Four goals that constantly pull against each other:

| Goal | Why it matters |
|------|---------------|
| Skill parity | Keeps matches competitive and not lopsided |
| Connection quality | Low enough ping to be playable for everyone |
| Queue time | Players abandon long waits |
| Party handling | Groups must stay together and slot into a lobby |

Tightening any one usually loosens another — perfect skill matching, for instance, means longer queues or worse pings.

## Pitfalls to avoid

| Mistake | Do this instead |
|---------|----------------|
| Letting the client decide outcomes | Make the server the sole authority |
| Replicating the entire world state | Send only what each player needs |
| Assuming a perfect connection | Budget for 100-200 ms and design around it |
| Snapping to exact remote coordinates | Interpolate and predict for smoothness |

---

**Bottom line:** a client's word is only ever a request, never a fact. The server is the one and only source of truth.
