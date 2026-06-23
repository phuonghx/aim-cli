---
name: vr-ar
description: Guides building immersive VR and AR experiences. Covers choosing a headset or AR platform, preventing motion sickness through locomotion and frame-rate choices, hitting per-device frame and resolution targets, designing controller and hand-tracking interactions, and getting spatial scale and depth cues right. Use when creating or reviewing an immersive experience and making comfort and performance decisions.
---

# Building Immersive VR and AR

Designing for headsets means a player sits inside the scene, so comfort and a rock-steady frame rate are not features — they are prerequisites.

## Choosing a Target

Pick the platform from where the experience will live.

**Virtual reality**

| Platform | Fits |
|---|---|
| Quest | Untethered, standalone play |
| PCVR | Maximum visual fidelity |
| PSVR | The console audience |
| WebXR | Delivery through the browser |

**Augmented reality**

| Platform | Fits |
|---|---|
| ARKit | Apple devices |
| ARCore | Android devices |
| WebXR | AR inside the browser |
| HoloLens | Enterprise deployments |

## Keeping Players Comfortable

Motion sickness comes from specific triggers. Neutralize each one.

| Trigger | Mitigation |
|---|---|
| Moving the player | Offer teleport or snap turning |
| Sagging frame rate | Hold a steady 90 FPS |
| Shaking the camera | Avoid it, or keep it minimal |
| Sudden acceleration | Ramp movement gradually |

Expose comfort options so players can tune to their own tolerance:

- A vignette that closes in during motion
- A choice between snap and smooth turning
- Seated and standing play modes
- Height calibration

## Hitting Performance Targets

Each headset has its own frame and per-eye resolution bar to clear.

| Headset | Frame rate | Per-eye resolution |
|---|---|---|
| Quest 2 | 72-90 | 1832x1920 |
| Quest 3 | 90-120 | 2064x2208 |
| PCVR | 90 | 2160x2160+ |
| PSVR2 | 90-120 | 2000x2040 |

On the frame budget:

- Consistency matters more than peak numbers.
- A single missed frame reads as a visible stutter.
- At 90 FPS you have **11.11 ms** per frame.

## Designing Interactions

Match the interaction style to the task.

| Style | Use for |
|---|---|
| Point and click | UI and far-off objects |
| Grab | Picking up and moving things |
| Gesture | Spells and special actions |
| Physical motion | Throwing, swinging, swordplay |

On hand tracking:

- It feels more present but is less accurate than controllers.
- It shines in social and casual settings.
- It struggles with action and anything demanding precision.

## Getting Space Right

**World scale** is the foundation — treat **1 unit as 1 meter** and never drift from it. Objects have to read at their true size, so verify against real-world measurements.

Layer depth cues by how much they contribute:

| Cue | Role |
|---|---|
| Stereo disparity | The primary sense of depth |
| Motion parallax | A strong secondary cue |
| Shadows | Anchor objects to surfaces |
| Occlusion | Establish front-to-back order |

## Common Mistakes

| Avoid this | Prefer this |
|---|---|
| Moving the camera independently | Leaving the camera under player control |
| Dipping under 90 FPS | Holding the frame rate steady |
| Cramped, tiny text | Large, legible text |
| Ignoring how far arms reach | Scaling to the player's reach |

---

Comfort is non-negotiable. The moment a player feels queasy, they take off the headset and they are done.
