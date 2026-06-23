---
name: game-audio
description: Reference for game audio design and integration, covering sound categories and channel priority, SFX creation and layering, state-driven and adaptive music, 3D/spatial positioning, platform formats and memory budgets, mix levels and ducking, plus common mistakes. Use it when designing sound effects, wiring music to game state, building reactive or spatial audio, choosing audio formats per platform, or setting a mix. Helps make audio reinforce gameplay rather than just decorate it.
---

# Game Audio

How sound gets designed, scored, and mixed so it strengthens the experience instead of cluttering it.

## Categories and Who Wins

Different sound types behave differently and deserve different handling.

| Type | Typical behavior | Examples |
|---|---|---|
| Music | Loops, crossfades, gets ducked | Background score, combat theme |
| SFX | One-shot, often positioned in 3D | Footsteps, impacts |
| Ambient | A looping background bed | Wind, distant crowd, forest |
| UI | Fires immediately, no spatialization | Clicks, notifications |
| Voice | Top priority, triggers ducking | Dialogue, announcer |

When too many sounds fight for the mix at once, resolve it in this order:

1. **Voice** — must always cut through
2. **Player SFX** — the player's own feedback can't be lost
3. **Enemy SFX** — gameplay-relevant, keep it audible
4. **Music** — sets mood, safe to duck
5. **Ambient** — lowest stakes, first to give way

## Designing Sounds

### Four ways to make a sound

| Method | Reach for it when | Catch |
|---|---|---|
| Field recording | You need realism | Top quality, but slow to capture |
| Synthesis | Sci-fi, retro, or UI tones | Distinctive, but takes skill |
| Library samples | You need speed | Fast, but generic and license-bound |
| Layering | You want the strongest result | Best payoff, most labor |

### Build big sounds in layers

A convincing gunshot, for instance, stacks four parts:

| Layer | Role | In a gunshot |
|---|---|---|
| Transient / attack | The sharp leading edge | Click, snap |
| Body | The main mass of the sound | Boom, blast |
| Tail | Decay and room response | Reverb, echo |
| Sweetener | A detail that sells realism | Shell casing, mechanical clink |

## Music That Follows the Game

### Drive music off game state

| State | Music response |
|---|---|
| Menu | Calm, loopable theme |
| Exploration | Ambient, atmospheric bed |
| Combat detected | Transition into rising tension |
| Combat engaged | Full battle track |
| Victory | Stinger, then settle into calm |
| Defeat | Somber stinger |
| Boss | Bespoke, multi-phase piece |

### Ways to move between cues

| Technique | Use for | Character |
|---|---|---|
| Crossfade | A smooth mood change | Gradual |
| Stinger | An instant reaction to an event | Dramatic |
| Stem mixing | Shifting intensity on the fly | Seamless |
| Beat-synced switch | Rhythm-driven gameplay | Musical |
| Queued transition point | Waiting for the next natural bar | Clean |

## Adaptive Audio

### Hook parameters to game variables

| Parameter | What it drives | Example |
|---|---|---|
| Threat level | Music intensity | Number of enemies nearby |
| Health | Filtering / reverb | Low HP muffles the mix |
| Speed | Tempo and energy | Racing pace |
| Environment | Reverb and EQ | Cave vs. open field |
| Time of day | Mood and loudness | Quieter at night |

### Two structures (and the combo)

| Approach | What shifts | Best for |
|---|---|---|
| Vertical (layers) | Add or drop instrument stems | Scaling intensity up and down |
| Horizontal (segments) | Swap between different sections | Discrete state changes |
| Combined | Both at once | Big-budget adaptive scores |

## Spatial Audio

### What gets positioned in 3D

| Element | Positioned? | Reasoning |
|---|---|---|
| Player footsteps | No (or barely) | Should stay constant and audible |
| Enemy footsteps | Yes | Players need directional warning |
| Gunfire | Yes | Locating threats matters |
| Music | No | Non-diegetic; it sets mood |
| Ambient zones | Yes (per area) | Tied to a place |
| UI | No | It belongs to the interface, not the world |

### How a sound changes with distance

| Range | What happens |
|---|---|
| Near | Full volume, full frequency range |
| Medium | Volume drops, highs start rolling off |
| Far | Quiet, with a low-pass filter |
| Beyond max | Silent, or a faint ambient hint |

## Platforms and Budgets

### Format per platform

| Platform | Format | Reason |
|---|---|---|
| PC | OGG Vorbis, WAV | Quality with no licensing burden |
| Console | Platform-specific | Certification requirements |
| Mobile | MP3, AAC | Smaller files, broad support |
| Web | WebM/Opus, MP3 fallback | Maximize browser coverage |

### Rough memory budgets

| Project | Budget | Strategy |
|---|---|---|
| Casual mobile | 10–50 MB | Compress hard, fewer variants |
| PC indie | 100–500 MB | Favor quality |
| Big-budget | 1 GB+ | Full fidelity, lots of variation |

## The Mix

### Reference levels

| Type | Level | Note |
|---|---|---|
| Voice | 0 dB (reference) | Always intelligible |
| Player SFX | −3 to −6 dB | Forward, but not harsh |
| Music | −6 to −12 dB | The bed; ducks under voice |
| Enemy SFX | −6 to −9 dB | Present without dominating |
| Ambient | −12 to −18 dB | A quiet underlayer |

### When to duck

| Trigger | Duck | By |
|---|---|---|
| Voice starts | Music + ambient | −6 to −9 dB |
| Explosion | Everything but the explosion | A brief dip |
| Menu opens | Gameplay audio | −3 to −6 dB |

## Mistakes to Avoid

| Pitfall | Do this instead |
|---|---|
| Replaying one identical sample | Cycle through 3–5 variations |
| Cranking everything to max | Respect a real mix hierarchy |
| Filling every gap with sound | Use silence for contrast and impact |
| Looping a single track forever | Add variety and transitions |
| Leaving audio out of the prototype | Even placeholder audio shapes feel |

---

> Audio carries roughly half the experience. Mute a game and you strip out most of its soul.
