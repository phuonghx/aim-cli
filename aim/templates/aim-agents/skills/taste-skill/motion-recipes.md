# motion-recipes.md — Scroll and physics motion patterns

Reach for these only when the `MOTION` dial and the brief justify them. Three rules sit above all of them:

- **Reduced motion is mandatory above `MOTION 3`.** Wrap with `useReducedMotion()` in Motion, or gate CSS behind `@media (prefers-reduced-motion: no-preference)`. Loops, parallax, scroll-hijacks, and physics all collapse to static under a reduce preference.
- **Animate only `transform` and `opacity`.** Never tween `top`, `left`, `width`, or `height`. Use `will-change: transform` only on elements that genuinely animate.
- **Never read scroll or pointer through React state.** No `window.addEventListener("scroll", …)`, no `window.scrollY` in state, no `requestAnimationFrame` loops that call `setState`. Each re-renders the whole tree per frame and stutters on phones. Use Motion's `useScroll` / `useMotionValue` / `useTransform`, GSAP `ScrollTrigger`, `IntersectionObserver`, or CSS scroll-driven animation (`animation-timeline: view()`).

Keep heavy scroll work isolated: GSAP and Three.js must live in dedicated `'use client'` leaves with `useEffect` cleanup, and must not share a component tree with Motion — they compete for the same frames.

---

## Recipe 1 — Scroll-reveal stagger (the light default)

For "items fade up as they enter," prefer Motion's `whileInView` over GSAP — no plugin, no ScrollTrigger, far cheaper. Use it for feature lists, testimonial grids, logo walls.

```tsx
"use client";
import { motion, useReducedMotion } from "motion/react";

export function RevealOnScroll({ entries }: { entries: string[] }) {
  const prefersReduced = useReducedMotion();

  return (
    <ul className="grid gap-6">
      {entries.map((entry, index) => (
        <motion.li
          key={entry}
          initial={prefersReduced ? false : { opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.35 }}
          transition={{
            duration: 0.55,
            delay: index * 0.07,
            ease: [0.16, 1, 0.3, 1], // expo-out
          }}
        >
          {entry}
        </motion.li>
      ))}
    </ul>
  );
}
```

Save GSAP for actual pinning and scrubbing (the next two recipes); use this for anything that only needs "enter on scroll."

---

## Recipe 2 — Sticky card stack

A real stack pins each card at the top of the viewport while the next one scrolls up over it, shrinking and dimming the one behind. It is *not* a sequential reveal list.

```tsx
"use client";
import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "motion/react";

gsap.registerPlugin(ScrollTrigger);

export function CardStack({ panels }: { panels: React.ReactNode[] }) {
  const scope = useRef<HTMLDivElement>(null);
  const prefersReduced = useReducedMotion();

  useEffect(() => {
    if (prefersReduced || !scope.current) return;

    const ctx = gsap.context(() => {
      const panelEls = gsap.utils.toArray<HTMLElement>(".stack-panel");
      const last = panelEls[panelEls.length - 1];

      panelEls.forEach((panel, i) => {
        if (panel === last) return;

        // Pin this panel at the viewport top until the final panel arrives.
        ScrollTrigger.create({
          trigger: panel,
          start: "top top",
          endTrigger: last,
          end: "top top",
          pin: true,
          pinSpacing: false,
        });

        // Shrink + fade this panel as the NEXT one slides up.
        gsap.to(panel, {
          scale: 0.93,
          opacity: 0.5,
          ease: "none",
          scrollTrigger: {
            trigger: panelEls[i + 1],
            start: "top bottom",
            end: "top top",
            scrub: true,
          },
        });
      });
    }, scope);

    return () => ctx.revert();
  }, [prefersReduced]);

  return (
    <div ref={scope} className="relative">
      {panels.map((panel, i) => (
        <div
          key={i}
          className="stack-panel sticky top-0 flex min-h-[100dvh] items-center justify-center"
        >
          {panel}
        </div>
      ))}
    </div>
  );
}
```

Key points: `start: "top top"` (pin at the very top, not "top center"), `pin: true`, every panel except the last is pinned, and the shrink transform is driven by the *next* panel's trigger so the one behind recedes as the new one arrives. The usual bug is pinning too late — `"top 80%"` or `"top center"` fires mid-scroll and looks broken.

---

## Recipe 3 — Horizontal pan on vertical scroll

Pin a section and translate an over-wide inner track sideways as the user scrolls down.

```tsx
"use client";
import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "motion/react";

gsap.registerPlugin(ScrollTrigger);

export function HorizontalPan({ children }: { children: React.ReactNode }) {
  const section = useRef<HTMLElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const prefersReduced = useReducedMotion();

  useEffect(() => {
    if (prefersReduced || !section.current || !track.current) return;

    const ctx = gsap.context(() => {
      const overflow = track.current!.scrollWidth - window.innerWidth;

      gsap.to(track.current, {
        x: -overflow,
        ease: "none",
        scrollTrigger: {
          trigger: section.current,
          start: "top top",           // pin once the section top reaches the top
          end: () => `+=${overflow}`, // scroll length == horizontal travel
          pin: true,
          scrub: 1,
          invalidateOnRefresh: true,  // recompute overflow on resize
        },
      });
    }, section);

    return () => ctx.revert();
  }, [prefersReduced]);

  return (
    <section ref={section} className="relative overflow-hidden">
      <div ref={track} className="flex h-[100dvh] items-center">
        {children}
      </div>
    </section>
  );
}
```

Key points: pin the wrapper (`start: "top top"`, `pin: true`), set `end` to the exact horizontal travel (`+=${overflow}`), and `scrub: 1` ties motion to the scrollbar. `invalidateOnRefresh` keeps it correct after resize. The common failure is the track moving before the section is pinned, so the reader sees half a slide — same fix as the stack: pin at the top.

---

## Layout and orchestration notes

- **Shared-element and reorder transitions:** use Motion's `layout` / `layoutId` for visible state changes (reordering a list, expanding a modal, moving an element across routes). Don't wrap static content in `layout` "just in case" — it pays for measurement work it doesn't need.
- **Sequenced reveals:** use Motion's `staggerChildren` (parent `variants` and children must share one client tree) or a CSS cascade (`animation-delay: calc(var(--i) * 90ms)`) when order carries meaning.
- **Springs over linear easing** for physical motion (`type: "spring", stiffness: 100, damping: 20`).
- **Motion must earn its place.** Before adding any animation, name what it communicates — hierarchy, narrative sequence, feedback, or a state change. "It looked cool" is not a reason. If you can't justify a ScrollTrigger, a marquee, or a pinned section in one sentence, cut it. At most one horizontal text marquee per page.
- **Claimed motion must be shown.** If the page advertises a high `MOTION` value, it actually animates (hero entry, scroll-reveal, hover feedback at minimum). If you can't ship motion cleanly within scope, lower the dial and ship a clean static page rather than half-built, janky effects with missing cleanup.
