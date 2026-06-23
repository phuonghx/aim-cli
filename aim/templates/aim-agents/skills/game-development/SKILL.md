---
name: game-development
description: Entry point for game projects that points to the right specialized sub-skill and teaches engine-agnostic fundamentals. Covers the simulation loop, common architecture patterns, input handling, frame budgeting, AI approaches, and collision strategy. Useful when building a game with any engine such as Unity, Godot, Unreal, Phaser, Bevy, or a custom stack, and the work needs direction toward platform, dimension, or specialty guidance.
---

# Game Development

A hub skill: it carries the engine-neutral fundamentals every game shares and hands off to a focused sub-skill once the project's shape is clear.

---

## How to route

Pick the sub-skill that matches what the question is really about. Most projects touch several.

**By target hardware**

- Runs in a browser (HTML5 / WebGL / WebGPU) → `web-games`
- Phones and tablets (iOS, Android) → `mobile-games`
- Desktop and console (Steam, PlayStation, Xbox, Switch) → `pc-games`
- Headsets and passthrough (Quest, PCVR, ARKit/ARCore) → `vr-ar`

**By visual dimension**

- Flat: sprites, tiles, parallax → `2d-games`
- Volumetric: meshes, materials, lights → `3d-games`

**By discipline**

- Systems, economy, pacing, the design doc → `game-design`
- Networking, replication, authority → `multiplayer`
- Look, asset pipeline, rigging and animation → `game-art`
- Sound effects, score, reactive mixing → `game-audio`

---

## Fundamentals that apply everywhere

### 1. The simulation loop

A game is a loop that samples input, advances the world, and paints a frame:

```
read input  →  step simulation (fixed dt)  →  draw (interpolated)
```

Decouple the two clocks. Run gameplay and physics at a **fixed step** (commonly 30–60 Hz) so behavior is deterministic and stable; render **as often as the display allows** and interpolate between the last two simulation states so motion looks smooth even when the two rates disagree.

### 2. Choosing a structure

| Approach | Reach for it when | Concrete case |
|----------|-------------------|---------------|
| Finite state machine | An entity has a handful of clear modes | Door: closed → opening → open → closing |
| Object pool | Things spawn and die constantly | Shell casings, hit sparks, projectiles |
| Event bus / observer | Systems must react without knowing each other | Pickup grabbed → score, SFX, and HUD all respond |
| Entity-component-system | Tens of thousands of like entities | Bullet-hell waves, swarm units |
| Command objects | You need replay, netcode, or undo | Recording a speedrun ghost |
| Behavior tree | Branching, authorable AI | A guard that patrols, investigates, then chases |

Default to a state machine. Reach for ECS only after a profiler proves the entity count is the bottleneck — it costs real architectural overhead.

### 3. Talk in actions, not keys

Map raw devices onto named intents, then have gameplay listen for intents:

```
"interact"  ←  E key  /  gamepad West  /  tap on hotspot
"throttle"  ←  W      /  right trigger /  on-screen pedal
```

One indirection layer buys you remappable controls, multiple input devices, and painless porting.

### 4. The frame budget

At 60 FPS each frame must finish inside **16.7 ms**. A rough split for a mid-complexity title:

| Slice | Rough share |
|-------|-------------|
| Input + events | ~1 ms |
| Physics / collision | ~3 ms |
| AI / decision logic | ~2 ms |
| Gameplay & scripts | ~4 ms |
| Draw + present | ~5 ms |
| Safety margin | ~1.7 ms |

When you blow the budget, fix in this order — earlier items pay off more:

1. Pick a better algorithm (drop the O(n²) pass)
2. Batch draw calls and merge state changes
3. Pool allocations to stop GC stutter
4. Swap in lower detail by distance (LOD)
5. Cull what the camera can't see

### 5. Matching AI to the problem

| Technique | Effort | Sweet spot |
|-----------|--------|------------|
| State machine | Low | A few predictable modes |
| Behavior tree | Medium | Designer-tweakable, modular logic |
| Utility scoring | High | Pick the best of many weighted options |
| Goal-oriented planning (GOAP) | High | Emergent agents that chain actions toward a goal |

### 6. Picking a collision test

| Method | Good for |
|--------|----------|
| Axis-aligned box (AABB) | Cheap rectangular overlap |
| Circle / sphere | Round bodies, fastest possible check |
| Spatial hash grid | Many objects of similar size |
| Quadtree / octree | Sprawling worlds with mixed-size objects |

---

## Habits worth keeping

| Instead of | Prefer |
|------------|--------|
| Recomputing everything each tick | Dirty flags and event-driven updates |
| `new` inside the hot loop | Pre-allocated pools |
| Re-fetching the same component repeatedly | Caching the reference once |
| Guessing where time goes | Measuring with a profiler first |
| Gameplay code reading the keyboard directly | An input-abstraction layer |

---

## Routing in practice

**"A browser platformer in HTML5"** — open `web-games` to settle the framework, lean on `2d-games` for tile and sprite work, and borrow level-pacing ideas from `game-design`.

**"A match-3 puzzle shipping on iOS and Android"** — start in `mobile-games` for touch and store rules, then use `game-design` to tune the difficulty curve.

**"A co-op VR melee game"** — `vr-ar` first for comfort and hand interaction, `3d-games` for rendering, `multiplayer` for state sync.

---

> Good games are *found*, not *planned*. Get an ugly playable build running early, then iterate toward the fun.
