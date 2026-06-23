---
name: pc-games
description: Guides building games for PC and consoles. Covers choosing between Unity, Godot, and Unreal, integrating Steam and passing console certification, mapping input as abstract actions across gamepads, profiling and fixing performance bottlenecks, and applying engine-specific techniques. Use when selecting an engine or shipping a desktop or console title and weighing the tradeoffs.
---

# Building Games for PC and Console

Guidance for desktop and console development, where you pick an engine, satisfy platform holders, and tune for a wide range of hardware.

## Picking an Engine

Decide by what the project actually demands, not by what is trending.

For 2D work:

- **Godot** when an open-source toolchain matters to you.
- **Unity** when a large team and asset pipeline are in play.

For 3D work:

- **Unreal** when you are chasing AAA-grade visuals.
- **Unity** when broad cross-platform reach is the priority.
- **Godot 4** for indie projects that value being open source.

For specialized requirements:

- **Unity** when you need DOTS for raw throughput.
- **Unreal** when you want Nanite geometry and Lumen lighting.
- **Godot** when you want something small and lightweight.

| Dimension | Unity 6 | Godot 4 | Unreal 5 |
|---|---|---|---|
| 2D | Good | Excellent | Limited |
| 3D | Good | Good | Excellent |
| Ramp-up | Medium | Easy | Hard |
| Licensing | Revenue share | Free | 5% past $1M |
| Best team size | Any | Solo to mid | Mid to large |

## Platform Capabilities

**Steam** gives you a set of services worth wiring up:

| Feature | What it does |
|---|---|
| Achievements | Track player milestones |
| Cloud saves | Sync progress across machines |
| Leaderboards | Drive competition |
| Workshop | Host user-made mods |
| Rich presence | Surface what the player is doing |

**Consoles** require passing the platform holder's compliance program before launch:

| Platform | Program |
|---|---|
| PlayStation | TRC |
| Xbox | XR |
| Nintendo | Lotcheck |

## Handling Controllers

Bind logical **actions**, never raw buttons, so one mapping works everywhere.

- *Confirm* resolves to A on Xbox, Cross on PlayStation, B on Nintendo.
- *Cancel* resolves to B on Xbox, Circle on PlayStation, A on Nintendo.

Tune haptics to the weight of the event:

| Strength | When |
|---|---|
| Subtle | UI feedback |
| Moderate | Collisions and hits |
| Strong | Big moments |

## Tuning Performance

Measure before you change anything — each engine ships a profiler:

| Engine | Where to look |
|---|---|
| Unity | Profiler window |
| Godot | Debugger then Profiler |
| Unreal | Unreal Insights |

Recurring culprits and their fixes:

| Symptom | Fix |
|---|---|
| Too many draw calls | Batch and use atlases |
| Garbage-collection hitches | Pool objects |
| Physics overhead | Simplify colliders |
| Heavy shaders | Add shader LODs |

## Engine-Specific Notes

**Unity 6**

- Use DOTS for systems where performance is critical.
- Compile hot paths with Burst.
- Stream assets through Addressables.

**Godot 4**

- Prototype quickly in GDScript.
- Drop to C# for involved logic.
- Decouple systems with signals.

**Unreal 5**

- Let designers build with Blueprints.
- Reserve C++ for performance-sensitive code.
- Render dense environments with Nanite.
- Light scenes dynamically with Lumen.

## Common Mistakes

| Avoid this | Prefer this |
|---|---|
| Picking an engine by buzz | Picking by project requirements |
| Skipping platform rules | Reading the certification specs |
| Wiring code to physical buttons | Routing through abstract actions |
| Optimizing on guesswork | Profiling early and repeatedly |

---

The engine is only a means to an end. Internalize the underlying principles and you can apply them in any engine.
