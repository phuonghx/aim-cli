---
name: 3d-games
description: Reference for 3D game development, covering the rendering pipeline, draw-call and geometry optimization, shaders, 3D physics colliders, camera rigs, lighting, and level-of-detail strategy. Use it when building or reviewing 3D titles and when deciding how to cull geometry, when a custom shader is justified, which collider to attach, or how to keep shadows and meshes affordable on the target hardware. Also useful for catching performance anti-patterns before they ship.
---

# Building Games in 3D

A reference for the rendering, simulation, and presentation systems behind real-time 3D.

---

## The Rendering Pipeline

Geometry travels through a fixed sequence on its way to the screen:

```
vertices  →  transform & project    (vertex stage)
          →  fill triangles to a grid   (rasterization)
          →  shade each covered pixel   (fragment stage)
          →  composite to the framebuffer  (output)
```

**Cut work before it reaches the GPU:**

| Technique | What it skips |
|-----------|---------------|
| Frustum culling | Objects outside the camera's view volume |
| Occlusion culling | Objects fully blocked by closer geometry |
| Level of detail | Triangle counts on anything far away |
| Batching | Per-object overhead by merging draw calls |

---

## Shaders

| Stage | Responsibility |
|-------|----------------|
| Vertex | Positions, normals, per-vertex transforms |
| Fragment / pixel | Final color and per-pixel lighting |
| Compute | General-purpose GPU math, no fixed output |

**Reach for a custom shader when you need:**

- A bespoke effect the standard material cannot produce — flowing water, flickering fire, a swirling portal.
- A deliberate art direction such as cel-shading or a hand-drawn sketch look.
- A faster path than the default lighting for a specific case.
- A signature look that sets the title apart visually.

---

## Physics in 3D

| Collider | Typical assignment |
|----------|--------------------|
| Box | Crates, walls, buildings |
| Sphere | Projectiles, broad-phase checks |
| Capsule | Player and creature bodies |
| Mesh | Detailed terrain — accurate but costly |

Guiding rules:

- Pair a **lightweight collider** with the detailed visual mesh; never collide against the render geometry directly.
- Route interactions through **collision layers** so unrelated objects ignore each other.
- Use **raycasts** for sightlines, hit-scan weapons, and ground checks.

---

## Cameras

| Rig | Where it fits |
|-----|---------------|
| Third-person | Action and adventure |
| First-person | Shooters and immersive play |
| Isometric | Strategy and RPGs |
| Orbital | Asset inspection and editor views |

**What makes a camera feel good:**

- **Lerp** toward the target instead of teleporting to it.
- Push in when geometry would otherwise clip through the lens (collision avoidance).
- Lead the view slightly toward motion (look-ahead).
- Widen the field of view at speed to amplify the sense of velocity.

---

## Lighting

| Light | Real-world analog |
|-------|-------------------|
| Directional | The sun or moon, parallel rays |
| Point | A torch or lamp radiating outward |
| Spot | A flashlight or stage cone |
| Ambient | Flat base fill so shadows aren't pure black |

Cost-aware shadowing:

- Dynamic shadows are **expensive** — budget them carefully.
- **Bake** lighting and shadows into textures wherever the scene is static.
- Split shadow detail by distance with **cascades** across large outdoor maps.

---

## Level of Detail

Swap models by how far they are from the camera:

| Range | Model served |
|-------|--------------|
| Close | Full triangle count |
| Mid | Roughly half the triangles |
| Distant | About a quarter, or a flat billboard |

---

## Mistakes to Avoid

| Pitfall | Better approach |
|---------|-----------------|
| Mesh colliders on everything | Primitive shapes wherever they suffice |
| Dynamic shadows on mobile | Baked lightmaps or blob shadows |
| A single mesh at every distance | Distance-driven LOD swaps |
| Shipping shaders untested | Profile first, then trim the cost |

---

> **Bottom line:** 3D is a magic trick — sell the impression of detail rather than rendering all of it.
