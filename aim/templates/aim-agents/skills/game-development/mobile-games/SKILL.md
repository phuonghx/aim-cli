---
name: mobile-games
description: Guides building games for phones and tablets. Covers designing for touch instead of buttons, managing battery and heat, adapting to many screen sizes, handling interruptions, meeting iOS App Store and Google Play submission rules, and picking a monetization model. Use when planning, building, or porting a game to mobile and deciding how to fit the platform's limits.
---

# Building Games for Mobile

Phones reward games designed for their realities: a finger instead of a gamepad, a battery that drains, a chassis that overheats, and a player who gets interrupted.

## What the Platform Forces on You

Each hardware and usage limit has a design response.

| Reality | Design response |
|---|---|
| Input is a fingertip | Use generous hit areas and gestures |
| Power is finite | Keep CPU and GPU work modest |
| The device heats up | Scale back as temperature climbs |
| Screens vary widely | Lay out UI responsively |
| Calls and alerts intrude | Pause cleanly when backgrounded |

## Designing for Touch

A touchscreen is a different input device from a controller, not a worse one. Design for its strengths.

| Touch | Controller |
|---|---|
| Coarse pointing | Pixel-accurate |
| Fingers cover the screen | Nothing blocks the view |
| Handful of usable zones | Many discrete buttons |
| Natural gestures | Sticks and triggers |

Guidelines that hold up:

- Make tap targets at least **44x44 points**.
- Confirm every touch with a visible reaction.
- Do not demand frame-perfect timing.
- Handle both portrait and landscape.

## Staying Cool and Charged

Treat thermal headroom as a budget you spend down, and ease off in stages.

| Device state | Reaction |
|---|---|
| Running warm | Lower visual quality |
| Running hot | Cap the frame rate |
| Near the limit | Suspend expensive effects |

To go easy on the battery:

- A locked **30 FPS** is plenty for many games.
- Stop rendering entirely while paused.
- Use location and the network sparingly.
- Lean on dark themes — OLED panels draw less power on dark pixels.

## Clearing the Stores

Each storefront has gating requirements you must satisfy before review.

**Apple App Store**

- Declare data use in privacy nutrition labels.
- Offer in-app account deletion if you let users create accounts.
- Provide screenshots sized for every device class.

**Google Play**

- Target the current year's API level.
- Ship 64-bit binaries.
- Package with Android App Bundles (AAB).

## Choosing How to Earn

Match the revenue model to the kind of game and audience.

| Model | Fits |
|---|---|
| Paid up front | Polished games with a committed audience |
| Free with IAP | Casual titles built around progression |
| Ad-supported | Hyper-casual games at large scale |
| Subscription | Games with ongoing content or multiplayer |

## Common Mistakes

| Avoid this | Prefer this |
|---|---|
| Transplanting desktop controls | Designing the input for touch |
| Ignoring power draw | Watching thermals and adapting |
| Locking to landscape | Honoring the player's orientation |
| Assuming constant connectivity | Caching locally and syncing later |

---

Mobile is the tightest platform there is. Spend the player's battery and attention as carefully as your own.
