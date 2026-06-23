---
name: web-games
description: Guides building games that run in the browser. Covers picking a rendering framework (2D vs 3D), deciding between WebGPU and WebGL, working within sandbox limits like tab throttling and blocked audio, packaging assets for fast delivery, and shipping as an installable PWA. Use when designing or troubleshooting a browser-based game and choosing the right tools and delivery strategy.
---

# Building Games for the Browser

Practical guidance for shipping games that run inside a web page, where the runtime is a sandbox you do not fully control.

## Choosing a Rendering Stack

Start from the dimensionality of your game, then decide how much engine you actually need.

- **2D, batteries included** — reach for Phaser when you want scenes, physics, input, and asset management handled for you.
- **2D, you drive** — reach for PixiJS when you mainly need a fast renderer and full control over UI and the scene graph.
- **3D, full engine** — reach for Babylon.js when you want physics, a scene system, and built-in XR support.
- **3D, lean renderer** — reach for Three.js when the focus is drawing and visualization and you want a smaller footprint.
- **Something bespoke** — drop down to raw Canvas or WebGL when no engine fits the shape of what you are building.

| Library | Dimension | Sweet spot |
|---|---|---|
| Phaser 4 | 2D | Complete game toolkit |
| PixiJS 8 | 2D | Renderer-first, custom UI |
| Three.js | 3D | Lightweight scenes, dataviz |
| Babylon.js 7 | 3D | Full engine with XR |

## WebGPU vs WebGL

WebGPU is the modern graphics API; WebGL remains the safe baseline. Roughly **73%** of users now have WebGPU.

| Engine | Availability |
|---|---|
| Chrome | 113 and up |
| Edge | 113 and up |
| Firefox | 131 and up |
| Safari | 18.0 and up |

How to choose:

- **Greenfield project** — target WebGPU and degrade to WebGL when it is missing.
- **Must support old devices** — build on WebGL from the start.
- **At runtime** — branch on the presence of `navigator.gpu` rather than sniffing the user agent.

## Living Within the Sandbox

The browser imposes limits that a native runtime does not. Plan around each one.

| Limitation | What to do |
|---|---|
| Cannot read the local disk | Ship assets in bundles or serve them from a CDN |
| Inactive tabs get throttled | Detect visibility changes and pause the loop |
| Users may be on metered data | Shrink assets aggressively |
| Sound will not autoplay | Wait for a tap or click before starting audio |

When you optimize, work through this order:

1. **Compress assets** — KTX2 for textures, Draco for geometry, WebP for images.
2. **Defer loading** — pull in content only when it is needed.
3. **Reuse objects** — pool instances so the garbage collector stays quiet.
4. **Batch draw calls** — group geometry to cut state changes.
5. **Move heavy work off-thread** — push expensive computation into Web Workers.

## Packaging Assets

Encode each asset type in a format the browser decodes cheaply.

| Asset | Preferred encoding |
|---|---|
| Textures | KTX2 with Basis Universal |
| Audio | WebM/Opus, falling back to MP3 |
| Models | glTF with Draco or Meshopt |

Split delivery into phases so the player reaches gameplay quickly:

- **Boot** — load only the essentials, ideally under ~2 MB.
- **In play** — stream additional content as the player needs it.
- **Idle** — quietly prefetch what comes next, such as the following level.

## Shipping as a PWA

Turning the game into a Progressive Web App gives it native-like reach.

What you gain:

- Plays without a connection
- Installs onto the home screen
- Runs full screen
- Can send push notifications

What it takes:

- A service worker that caches the build
- A web app manifest
- Delivery over HTTPS

## Working with Audio

Browsers gate the `AudioContext` behind a user gesture, so build around that rule.

- Instantiate the context on the first tap or click.
- If it comes back suspended, resume it before playing.
- Drive everything through the Web Audio API.
- Keep a pool of reusable audio nodes.
- Preload the sounds you trigger often.
- Encode clips as WebM/Opus to keep them small.

## Common Mistakes

| Avoid this | Prefer this |
|---|---|
| Front-loading every asset | Loading progressively |
| Running flat out in hidden tabs | Pausing when not visible |
| Stalling startup on audio | Loading audio lazily |
| Shipping uncompressed files | Compressing everything |
| Assuming a fast pipe | Designing for slow links |

---

The browser reaches more players than any other platform, but only if you build for its constraints instead of fighting them.
