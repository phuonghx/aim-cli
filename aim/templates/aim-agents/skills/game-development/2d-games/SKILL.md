---
name: 2d-games
description: Reference for building 2D games, covering sprite and animation setup, tilemap construction, 2D collision and physics, camera behavior, and genre-specific movement patterns. Use it when designing or reviewing platformers, top-down shooters, or any 2D title, and when deciding how to organize art, tune jump feel, or keep a camera readable. Also useful for spotting common 2D mistakes like draw-call bloat or overly precise collision geometry.
---

# Building Games in 2D

A working reference for the systems that make a 2D game feel responsive and look coherent.

---

## Sprites and Animation

Art that is loaded and drawn efficiently keeps frame times low and motion legible.

**How to organize sprite data:**

- **Texture atlas** — pack many images into one sheet so the GPU issues fewer draw calls. A character's idle, walk, and jump frames all live on a single sheet rather than as 30 separate files.
- **Frame sequence** — an ordered list of regions on the atlas, cycled to produce motion.
- **Pivot point** — the anchor used for rotation and scaling. Put a sword's pivot at the handle, not the center, so it swings correctly.
- **Z-order** — the integer that decides who draws on top. The player's z sits above the floor tiles but below the HUD.

**Making motion feel alive:**

- Animate somewhere between **8 and 24 frames per second** depending on the style — chunky retro sprites read fine at the low end, fluid action wants the high end.
- Compress and elongate shapes (squash & stretch) on impacts and jumps to sell weight.
- Lead into a big action with a brief wind-up (anticipation) — a crouch before a leap.
- Let motion settle afterward (follow-through) instead of snapping to a stop.

---

## Tilemaps

Grid-based levels are fast to author and cheap to render.

| Decision | Guidance |
|----------|----------|
| Tile dimension | Stick to a power of two — 16, 32, or 64 px — and stay consistent |
| Terrain edges | Lean on auto-tiling so corners and borders pick themselves |
| Collision data | Approximate with coarse shapes, not the exact painted pixels |

**A typical layer stack, back to front:**

1. **Backdrop** — distant scenery you can never touch.
2. **Ground** — the solid tiles the player stands on.
3. **Objects** — chests, switches, pickups the player interacts with.
4. **Overlay** — foreground elements that scroll at a different rate for parallax depth.

---

## Collision and Physics

| Collider | Best for |
|----------|----------|
| Box | Crates, platforms, walls |
| Circle | Coins, bombs, anything round |
| Capsule | Player and enemy bodies |
| Polygon | Irregular hand-authored shapes |

Key choices when wiring up physics:

- Decide early between **pixel-perfect** movement and a **physics-driven** body — blending the two invites jitter and tunneling.
- Step the simulation on a **fixed timestep** so behavior stays identical regardless of frame rate.
- Use **collision layers** to control what tests against what — bullets check enemies, not other bullets.

---

## Cameras

| Style | Where it fits |
|-------|---------------|
| Follow | Keep the avatar centered |
| Look-ahead | Bias the view toward facing direction |
| Multi-target | Frame two players at once with co-op |
| Room-bounded | Snap between chambers in a metroidvania |

**Screen shake**, used with restraint:

- Keep bursts brief — roughly **50 to 200 ms**.
- Ramp the intensity down over the burst rather than cutting it dead.
- Reserve it for moments that matter; constant shake just fatigues the eye.

---

## Genre Movement

**Platformers** live or die on jump feel:

- **Coyote time** — accept a jump input for a few frames after the player walks off a ledge.
- **Jump buffering** — remember a jump pressed slightly before landing and fire it on touchdown.
- **Variable height** — cut the upward velocity when the button releases so taps hop and holds soar.

**Top-down games** turn on movement granularity:

- Pick **8-direction** snapping or **free analog** motion to match the feel you want.
- Choose between **manual aiming** and **auto-targeting** based on how twitchy the combat should be.
- Decide whether the sprite **rotates** to face its heading or stays upright.

---

## Mistakes to Avoid

| Pitfall | Better approach |
|---------|-----------------|
| One texture per sprite | Batch them into an atlas |
| Collision matching every pixel | Approximate with simple shapes |
| A camera that snaps and stutters | Interpolate toward the target |
| Mixing pixel-perfect with a physics body | Commit to a single model |

---

> **Bottom line:** in 2D there is nowhere to hide — make every pixel say something.
