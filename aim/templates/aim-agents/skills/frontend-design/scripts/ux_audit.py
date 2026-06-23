#!/usr/bin/env python3
"""Static UX / frontend-design linter.

This tool scans source files (markup, components, stylesheets) and flags
places where the code drifts from a broad catalogue of design and
front-end best practices. Findings are split into two buckets: hard
``issues`` (treated as failures) and softer ``warnings`` (advisory only).

The rules are organised into the following themed groups:

* Cognitive / perceptual laws
    Hick (navigation breadth), Fitts (hit-target size), Miller (form
    chunking), Von Restorff (a stand-out primary action) and the serial
    position effect (key items first or last).

* Emotional design (after Don Norman)
    Visceral first impressions, behavioural feedback on interaction, and
    reflective brand/identity content.

* Trust cues
    Security reassurance on forms, social proof, and authority markers.

* Cognitive-load handling
    Progressive disclosure, visual-noise limits, and conventional/labelled
    controls.

* Ethical persuasion
    Sensible pre-selected defaults, price anchoring, quantified social
    proof, and progress feedback.

* Typography (nine facets)
    Family count, measure/line-length, leading, tracking, weight contrast,
    fluid sizing, heading order, modular scale, and chunked readability.

* Visual effects (ten facets)
    Glassmorphism, neumorphism, shadow elevation, gradient restraint,
    border restraint, glow restraint, image overlays, GPU-friendly
    animation, ``will-change`` discipline, and effect-vs-decoration balance.

* Colour (seven facets)
    A hard ban on purple hues, the 60-30-10 split, scheme detection,
    dark-mode purity, contrast risk, contextual colour psychology, and a
    nudge toward HSL palettes.

* Animation (six facets)
    Duration bounds, easing direction, interaction micro-feedback, loading
    states, route transitions, and scroll-handler performance.

* Motion graphics (seven facets)
    Lottie fallbacks, GSAP teardown, SVG animation cost, 3D-transform setup,
    particle fallbacks, scroll throttling, and functional-vs-decorative use.

* Accessibility
    Image alt text, reduced-motion support, and form labelling.

All told the scanner runs well over eighty individual checks.
"""

import json
import os
import re
import sys
from pathlib import Path

# Source extensions worth inspecting.
SCANNED_SUFFIXES = {'.tsx', '.jsx', '.html', '.vue', '.svelte', '.css'}

# Directories that never contain hand-authored UI worth auditing.
PRUNED_DIRS = {'node_modules', '.git', 'dist', 'build', '.next', 'ui'}

# Generic font keywords / system faces that should not count toward the
# per-file "distinct font family" tally.
GENERIC_FONTS = {
    'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'system-ui',
    'inherit', 'arial', 'georgia', 'times new roman', 'courier new',
    'verdana', 'helvetica', 'tahoma',
}

# Named CSS weights mapped onto their numeric equivalents.
NAMED_WEIGHTS = {
    'thin': '100', 'extralight': '200', 'light': '300', 'normal': '400',
    'medium': '500', 'semibold': '600', 'bold': '700', 'extrabold': '800',
    'black': '900',
}

# Layout-affecting properties that should not be animated or hinted via
# will-change (they force reflow rather than compositing).
LAYOUT_PROPS = {'width', 'height', 'top', 'left', 'right', 'bottom',
                'margin', 'padding'}

# Recognised modular-scale ratios.
SCALE_RATIOS = {1.067, 1.125, 1.2, 1.25, 1.333, 1.5, 1.618}

# Purple-ish colours and keywords that are disallowed outright.
BANNED_PURPLES = [
    '#8B5CF6', '#A855F7', '#9333EA', '#7C3AED', '#6D28D9',
    '#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE', '#EDE9FE',
    '#8b5cf6', '#a855f7', '#9333ea', '#7c3aed', '#6d28d9',
    'purple', 'violet', 'fuchsia', 'magenta', 'lavender',
]


class DesignLinter:
    """Accumulates findings while walking files one at a time."""

    def __init__(self):
        # Hard failures.
        self.issues = []
        # Advisory notes.
        self.warnings = []
        # Tally of explicitly satisfied checks.
        self.passed_count = 0
        # How many files were actually read.
        self.files_checked = 0

    # -- entry points -----------------------------------------------------

    def scan_path(self, target):
        """Audit a single file or recurse a directory tree."""
        if os.path.isfile(target):
            self.scan_file(target)
        else:
            self.scan_tree(target)

    def scan_tree(self, root_dir):
        """Walk ``root_dir`` and audit every file with a known suffix."""
        for current, subdirs, names in os.walk(root_dir):
            # Mutate in place so os.walk skips pruned directories.
            subdirs[:] = [d for d in subdirs if d not in PRUNED_DIRS]
            for name in names:
                if Path(name).suffix in SCANNED_SUFFIXES:
                    self.scan_file(os.path.join(current, name))

    def scan_file(self, path):
        """Read one file and run the full battery of checks against it."""
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as handle:
                source = handle.read()
        except Exception:
            return

        self.files_checked += 1
        label = os.path.basename(path)

        # A small bag of frequently reused signals, computed once.
        facts = self._collect_signals(source)

        # Run each themed group of checks.
        self._check_perception_laws(label, source, facts)
        self._check_emotional_design(label, source, facts)
        self._check_trust(label, source, facts)
        self._check_cognitive_load(label, source, facts)
        self._check_persuasion(label, source, facts)
        self._check_typography(label, source, facts)
        self._check_visual_effects(label, source, facts)
        self._check_colour(label, source, facts)
        self._check_animation(label, source, facts)
        self._check_motion_graphics(label, source, facts)
        self._check_accessibility(label, source, facts)

    # -- shared signal extraction ----------------------------------------

    def _collect_signals(self, source):
        """Pre-compute flags and counts shared across multiple rule groups."""
        return {
            'long_text': bool(re.search(
                r'<p|<div.*class=.*text|article|<span.*text',
                source, re.IGNORECASE)),
            'form': bool(re.search(
                r'<form|<input|password|credit|card|payment',
                source, re.IGNORECASE)),
            'field_like': len(re.findall(
                r'<input|<select|<textarea|<option',
                source, re.IGNORECASE)),
            'hero': bool(re.search(r'hero|<h1|banner', source, re.IGNORECASE)),
            'nav_count': len(re.findall(
                r'<NavLink|<Link|<a\s+href|nav-item', source, re.IGNORECASE)),
        }

    # -- 1. perceptual / cognitive laws ----------------------------------

    def _check_perception_laws(self, label, source, facts):
        nav_count = facts['nav_count']

        # Hick: navigation that fans out too far slows decisions.
        if nav_count > 7:
            self.warnings.append(
                f"[Hick's Law] {label}: {nav_count} nav items (Max 7). "
                f"Group them into categorised submenus.")

        # Fitts: very short controls are hard to hit, especially on touch.
        if re.search(r'height:\s*([0-3]\d)px', source) or \
                re.search(r'h-[1-9]\b|h-10\b', source):
            self.warnings.append(
                f"[Fitts' Law] {label}: Small targets (< 44px)")

        # Miller: long single-step forms overload working memory.
        field_count = len(re.findall(
            r'<input|<select|<textarea', source, re.IGNORECASE))
        if field_count > 7 and not re.search(
                r'step|wizard|stage', source, re.IGNORECASE):
            self.warnings.append(
                f"[Miller's Law] {label}: Complex form ({field_count} fields)")

        # Von Restorff: one action should visually stand apart.
        if 'button' in source.lower() and not re.search(
                r'primary|bg-primary|Button.*primary|variant=["\']primary',
                source, re.IGNORECASE):
            self.warnings.append(f"[Von Restorff] {label}: No primary CTA")

        # Serial position: the final nav slot should hold something useful.
        if nav_count > 3:
            link_texts = re.findall(
                r'<NavLink|<Link|<a\s+href[^>]*>([^<]+)</a>',
                source, re.IGNORECASE)
            if link_texts and len(link_texts) > 2:
                tail = link_texts[-1].lower() if link_texts else ''
                key_words = ['contact', 'login', 'sign', 'get started',
                             'cta', 'button']
                if not any(word in tail for word in key_words):
                    self.warnings.append(
                        f"[Serial Position] {label}: Last nav item may not be "
                        f"important. Place key actions at start/end.")

    # -- 1.5 emotional design --------------------------------------------

    def _check_emotional_design(self, label, source, facts):
        # Visceral: a hero with no visual treatment feels flat.
        if facts['hero']:
            gradient = bool(re.search(
                r'gradient|linear-gradient|radial-gradient', source))
            animated = bool(re.search(
                r'@keyframes|transition:|animate-', source))
            if not (gradient or animated) and not re.search(
                    r'background:|bg-', source):
                self.warnings.append(
                    f"[Visceral] {label}: Hero section lacks visual appeal. "
                    f"Try gradients or subtle animations.")

        # Behavioural: clickable things should react somehow.
        if 'onClick' in source or '@click' in source or 'onclick' in source:
            reacts = re.search(
                r'transition|animate|hover:|focus:|disabled|loading|spinner',
                source, re.IGNORECASE)
            stateful = re.search(r'setState|useState|disabled|loading', source)
            if not reacts and not stateful:
                self.warnings.append(
                    f"[Behavioral] {label}: Interactive elements give no "
                    f"immediate feedback. Add hover/focus/disabled states.")

        # Reflective: long pages benefit from brand/identity content.
        identity = bool(re.search(
            r'about|story|mission|values|why we|our journey|testimonials',
            source, re.IGNORECASE))
        if facts['long_text'] and not identity:
            self.warnings.append(
                f"[Reflective] {label}: Long-form content with no brand "
                f"story/values. Add an 'About' or 'Why We Exist' section.")

    # -- 1.6 trust building ----------------------------------------------

    def _check_trust(self, label, source, facts):
        # Reassure users when collecting input.
        if facts['form']:
            sec_hits = re.findall(
                r'ssl|secure|encrypt|lock|padlock|https',
                source, re.IGNORECASE)
            if len(sec_hits) == 0 and not re.search(
                    r'checkout|payment', source, re.IGNORECASE):
                self.warnings.append(
                    f"[Trust] {label}: Form without security indicators. "
                    f"Add 'SSL Secure' or a lock icon.")

        # Social proof: presence counts as a pass, absence as a nudge.
        proof_hits = re.findall(
            r'review|testimonial|rating|star|trust|trusted by|customer|logo',
            source, re.IGNORECASE)
        if len(proof_hits) > 0:
            self.passed_count += 1
        elif facts['long_text']:
            self.warnings.append(
                f"[Trust] {label}: No social proof detected. Consider "
                f"testimonials, ratings, or 'Trusted by' logos.")

        # Authority markers usually live in the footer.
        if re.search(r'footer|<footer', source, re.IGNORECASE):
            auth_hits = re.findall(
                r'certif|award|media|press|featured|as seen in',
                source, re.IGNORECASE)
            if len(auth_hits) == 0:
                self.warnings.append(
                    f"[Trust] {label}: Footer lacks authority signals. Add "
                    f"certifications, awards, or media mentions.")

    # -- 1.7 cognitive load ----------------------------------------------

    def _check_cognitive_load(self, label, source, facts):
        # Lots of controls without any way to defer them.
        if facts['field_like'] > 5:
            staged = re.search(
                r'step|wizard|stage|accordion|collapsible|tab|more\.\.\.|'
                r'advanced|show more', source, re.IGNORECASE)
            if not staged:
                self.warnings.append(
                    f"[Cognitive Load] {label}: Many form elements without "
                    f"progressive disclosure. Try an accordion, tabs, or an "
                    f"'Advanced' toggle.")

        # Too much colour and bordering at once reads as clutter.
        many_colours = len(re.findall(
            r'#[0-9a-fA-F]{3,6}|rgb|hsl', source)) > 15
        many_borders = len(re.findall(r'border:|border-', source)) > 10
        if many_colours and many_borders:
            self.warnings.append(
                f"[Cognitive Load] {label}: High visual noise. Many colours "
                f"and borders raise cognitive load.")

        # Unlabelled inputs are a usability and a11y problem (hard fail).
        if re.search(r'<input|<select|<textarea', source, re.IGNORECASE):
            labelled = bool(re.search(
                r'<label|placeholder|aria-label|htmlFor',
                source, re.IGNORECASE))
            if not labelled:
                self.issues.append(
                    f"[Cognitive Load] {label}: Form inputs without labels. "
                    f"Use <label> for clarity and accessibility.")

    # -- 1.8 persuasion ---------------------------------------------------

    def _check_persuasion(self, label, source, facts):
        is_form = facts['form']
        field_like = facts['field_like']

        # Pre-select the recommended radio option.
        if is_form:
            defaulted = bool(re.search(
                r'checked|selected|default|value=["\'].*["\']', source))
            radios = len(re.findall(r'type=["\']radio', source, re.IGNORECASE))
            if radios > 0 and not defaulted:
                self.warnings.append(
                    f"[Persuasion] {label}: Radio buttons without a default. "
                    f"Pre-select the recommended option.")

        # Anchor discounted prices against an original.
        if re.search(r'price|pricing|cost|\$\d+', source, re.IGNORECASE):
            anchored = bool(re.search(
                r'original|was|strike|del|save \d+%', source, re.IGNORECASE))
            if not anchored:
                self.warnings.append(
                    f"[Persuasion] {label}: Prices without anchoring. Show an "
                    f"original price to frame the discount.")

        # Quantify social proof.
        if re.search(r'join|subscriber|member|user', source, re.IGNORECASE):
            quantified = bool(re.findall(r'\d+[+kmb]|\d+,\d+', source))
            if not quantified:
                self.warnings.append(
                    f"[Persuasion] {label}: Social proof without specific "
                    f"numbers. Use a 'Join 10,000+' style.")

        # Long forms should show progress.
        if is_form:
            progressed = bool(re.search(
                r'progress|step \d+|complete|%|bar', source, re.IGNORECASE))
            if field_like > 5 and not progressed:
                self.warnings.append(
                    f"[Persuasion] {label}: Long form without a progress "
                    f"indicator. Add a bar or 'Step X of Y'.")

    # -- 2. typography ----------------------------------------------------

    def _check_typography(self, label, source, facts):
        long_text = facts['long_text']

        # 2.1 Distinct font families.
        families = set()
        face_decls = re.findall(
            r'@font-face\s*\{[^}]*family:\s*["\']?([^;"\'\s}]+)',
            source, re.IGNORECASE)
        google_decls = re.findall(
            r'fonts\.googleapis\.com[^"\']*family=([^"&]+)',
            source, re.IGNORECASE)
        stack_decls = re.findall(r'font-family:\s*([^;]+)', source, re.IGNORECASE)

        for face in face_decls:
            families.add(face.strip().lower())
        for entry in google_decls:
            for piece in entry.replace('+', ' ').split('|'):
                families.add(piece.split(':')[0].strip().lower())
        for stack in stack_decls:
            head = stack.split(',')[0].strip().strip('"\'')
            if head.lower() not in GENERIC_FONTS:
                families.add(head.lower())

        if len(families) > 3:
            self.issues.append(
                f"[Typography] {label}: {len(families)} font families "
                f"detected. Keep it to 2-3 for cohesion.")

        # 2.2 Line length / measure.
        if long_text and not re.search(
                r'max-w-(?:prose|[\[\\]?\d+ch[\]\\]?)|max-width:\s*\d+ch',
                source):
            self.warnings.append(
                f"[Typography] {label}: No line-length constraint (45-75ch). "
                f"Use max-w-prose or max-w-[65ch].")

        # 2.3 Leading.
        text_count = len(re.findall(
            r'<p|<span|<div.*text|<h[1-6]', source, re.IGNORECASE))
        if text_count > 0 and not re.search(
                r'leading-|line-height:', source):
            self.warnings.append(
                f"[Typography] {label}: Text without line-height. Body: "
                f"1.4-1.6, Headings: 1.1-1.3")

        if re.search(r'<h[1-6]|text-(?:xl|2xl|3xl|4xl|5xl|6xl)',
                     source, re.IGNORECASE):
            for value in re.findall(
                    r'(?:leading-|line-height:\s*)([\d.]+)', source):
                if float(value) > 1.5:
                    self.warnings.append(
                        f"[Typography] {label}: Heading line-height {value} "
                        f"(>1.3). Headings should be tighter (1.1-1.3).")

        # 2.4 Tracking.
        if re.search(r'uppercase|text-transform:\s*uppercase',
                     source, re.IGNORECASE):
            if not re.search(r'tracking-|letter-spacing:', source):
                self.warnings.append(
                    f"[Typography] {label}: Uppercase text without tracking. "
                    f"ALL CAPS wants +5-10% spacing.")

        if re.search(r'text-(?:4xl|5xl|6xl|7xl|8xl|9xl)|font-size:\s*[3-9]\dpx',
                     source):
            if not re.search(r'tracking-tight|letter-spacing:\s*-[0-9]', source):
                self.warnings.append(
                    f"[Typography] {label}: Large display text without "
                    f"tracking-tight. Big text wants -1% to -4% spacing.")

        # 2.5 Weight contrast.
        weight_values = self._extract_weights(source)
        for idx in range(len(weight_values) - 1):
            if abs(weight_values[idx] - weight_values[idx + 1]) == 100:
                self.warnings.append(
                    f"[Typography] {label}: Adjacent font weights "
                    f"({weight_values[idx]}/{weight_values[idx + 1]}). "
                    f"Skip at least two levels for contrast.")
        distinct_weights = set(weight_values)
        if len(distinct_weights) > 4:
            self.warnings.append(
                f"[Typography] {label}: {len(distinct_weights)} font weights. "
                f"Keep it to 3-4 per page.")

        # 2.6 Fluid sizing.
        if bool(re.search(r'font-size:|text-(?:xs|sm|base|lg|xl|2xl)', source)) \
                and not re.search(r'clamp\(|responsive:', source):
            self.warnings.append(
                f"[Typography] {label}: Fixed font sizes without clamp(). "
                f"Consider fluid type: clamp(MIN, PREFERRED, MAX)")

        # 2.7 Heading order.
        levels = re.findall(r'<(h[1-6])', source, re.IGNORECASE)
        if levels:
            for idx in range(len(levels) - 1):
                here = int(levels[idx][1])
                nxt = int(levels[idx + 1][1])
                if nxt > here + 1:
                    self.warnings.append(
                        f"[Typography] {label}: Skipped heading level "
                        f"(h{here} -> h{nxt}). Keep the hierarchy sequential.")
            if 'h1' not in [lv.lower() for lv in levels] and long_text:
                self.warnings.append(
                    f"[Typography] {label}: No h1 found. Each page should have "
                    f"one primary heading.")

        # 2.8 Modular scale.
        self._check_modular_scale(label, source)

        # 2.9 Readability / chunking.
        paras = re.findall(r'<p[^>]*>([^<]+)</p>', source, re.IGNORECASE)
        for para in paras:
            words = len(para.split())
            if words > 100:
                self.warnings.append(
                    f"[Typography] {label}: Long paragraph ({words} words). "
                    f"Break into 3-4 line chunks for readability.")
        if len(paras) > 5:
            if len(re.findall(r'<h[2-6]', source, re.IGNORECASE)) == 0:
                self.warnings.append(
                    f"[Typography] {label}: Long content without subheadings. "
                    f"Add h2/h3 to break up the text.")

    def _extract_weights(self, source):
        """Return numeric font-weight values in document order."""
        raw = re.findall(
            r'font-weight:\s*(\d+)|'
            r'font-(?:thin|extralight|light|normal|medium|semibold|bold|'
            r'extrabold|black)|fw-(\d+)',
            source, re.IGNORECASE)
        values = []
        for first, second in raw:
            token = first or second
            if not token:
                continue
            token = NAMED_WEIGHTS.get(token.lower(), token)
            try:
                values.append(int(token))
            except ValueError:
                pass
        return values

    def _check_modular_scale(self, label, source):
        """Warn when explicit font sizes don't follow a known scale ratio."""
        sizes = []
        for amount, unit in re.findall(
                r'font-size:\s*(\d+(?:\.\d+)?)(px|rem|em)', source):
            if unit in ('rem', 'em'):
                sizes.append(float(amount))
            elif unit == 'px':
                sizes.append(float(amount) / 16)  # px -> rem at 16px base

        if len(sizes) <= 2:
            return

        ordered = sorted(set(sizes))
        steps = []
        for idx in range(1, len(ordered)):
            if ordered[idx - 1] > 0:
                steps.append(ordered[idx] / ordered[idx - 1])

        for step in steps[:3]:
            if not any(abs(step - known) < 0.05 for known in SCALE_RATIOS):
                self.warnings.append(
                    f"[Typography] {label}: Font sizes may not follow a "
                    f"modular scale (ratio: {step:.2f}). Try a consistent "
                    f"ratio like 1.25 (Major Third).")
                break

    # -- 3. visual effects ------------------------------------------------

    def _check_visual_effects(self, label, source, facts):
        # Glassmorphism needs blur AND translucency together.
        if 'backdrop-filter' in source or 'blur(' in source:
            if not re.search(
                    r'background:\s*rgba|bg-opacity|bg-[a-z0-9]+\/\d+', source):
                self.warnings.append(
                    f"[Visual] {label}: Blur used without a semi-transparent "
                    f"background (Glassmorphism fail)")

        # Animating layout-affecting properties is expensive.
        if re.search(r'@keyframes|transition:', source):
            costly = re.findall(
                r'width|height|top|left|right|bottom|margin|padding', source)
            if costly:
                self.warnings.append(
                    f"[Performance] {label}: Animating expensive properties "
                    f"({', '.join(set(costly))}). Prefer transform/opacity.")
            if not re.search(r'prefers-reduced-motion', source):
                self.warnings.append(
                    f"[Accessibility] {label}: Animations found without a "
                    f"prefers-reduced-motion check")

        shadows = re.findall(r'box-shadow:\s*([^;]+)', source)

        # Flat single-layer shadows look unnatural.
        for shadow in shadows:
            if ',' not in shadow and not re.search(r'\d+px\s+[1-9]\d*px', shadow):
                self.warnings.append(
                    f"[Visual] {label}: Simple/unnatural shadow. Use multiple "
                    f"layers or a Y > X offset for realism.")

        # 3.1 Neumorphism inset.
        for shadow in shadows:
            if ',' in shadow and '-' in shadow and 'inset' in shadow:
                self.warnings.append(
                    f"[Visual] {label}: Neomorphism inset detected. Ensure "
                    f"adequate contrast for accessibility.")

        # 3.2 Shadow elevation hierarchy.
        shadow_count = len(shadows)
        if shadow_count > 0:
            faint = [float(o) for o in re.findall(
                r'rgba?\([^)]+,\s*([\d.]+)\)', source) if float(o) < 0.5]
            if shadow_count >= 3 and len(faint) > 0:
                if len(set(faint)) < 2:
                    self.warnings.append(
                        f"[Visual] {label}: All shadows share one opacity. "
                        f"Vary intensity to express elevation.")

        # 3.3 Gradients.
        gradient = bool(re.search(
            r'gradient|linear-gradient|radial-gradient|conic-gradient', source))
        if gradient:
            grad_count = len(re.findall(r'gradient', source, re.IGNORECASE))
            if grad_count > 5:
                self.warnings.append(
                    f"[Visual] {label}: Many gradients ({grad_count}). Make "
                    f"sure they serve a purpose, not decoration.")
        elif facts['hero'] and not re.search(r'background:|bg-', source):
            self.warnings.append(
                f"[Visual] {label}: Hero section without visual interest. "
                f"Consider a gradient for depth.")

        # 3.4 Borders.
        if re.search(r'border:|border-', source):
            border_count = len(re.findall(r'border:', source))
            if border_count > 8:
                self.warnings.append(
                    f"[Visual] {label}: Many border declarations "
                    f"({border_count}). Simplify for a cleaner look.")

        # 3.5 Glow.
        for ts in re.findall(r'text-shadow:', source):
            if ',' in ts:
                self.warnings.append(
                    f"[Visual] {label}: Text glow detected. Make sure "
                    f"readability holds up.")
        if len(re.findall(r'box-shadow:\s*[^;]*0\s+0\s+', source)) > 2:
            self.warnings.append(
                f"[Visual] {label}: Multiple glow effects. Reserve them for "
                f"emphasis only.")

        # 3.6 Image overlays.
        has_imagery = bool(re.search(
            r'<img|background-image:|bg-\[url', source))
        if has_imagery and facts['long_text']:
            if not re.search(
                    r'overlay|rgba\(0|gradient.*transparent|::after|::before',
                    source):
                self.warnings.append(
                    f"[Visual] {label}: Text over an image without an overlay. "
                    f"Add a gradient overlay for readability.")

        # 3.7 will-change discipline.
        if re.search(r'will-change:', source):
            for prop in re.findall(r'will-change:\s*([^;]+)', source):
                prop = prop.strip().lower()
                if prop in LAYOUT_PROPS:
                    self.issues.append(
                        f"[Performance] {label}: will-change on '{prop}' "
                        f"(layout property). Use only for transform/opacity.")
        wc_count = len(re.findall(r'will-change:', source))
        if wc_count > 3:
            self.warnings.append(
                f"[Performance] {label}: Many will-change declarations "
                f"({wc_count}). Reserve it for heavy animations.")

        # 3.8 Effect-vs-decoration balance.
        effect_total = (
            (1 if gradient else 0)
            + shadow_count
            + len(re.findall(r'backdrop-filter|blur\(', source))
            + len(re.findall(r'text-shadow:', source))
        )
        if effect_total > 10:
            self.warnings.append(
                f"[Visual] {label}: Many visual effects ({effect_total}). "
                f"Make sure they serve a purpose, not decoration.")
        if facts['long_text'] and effect_total == 0:
            self.warnings.append(
                f"[Visual] {label}: Flat design with no depth. Consider "
                f"shadows or subtle gradients for hierarchy.")

    # -- 4. colour --------------------------------------------------------

    def _check_colour(self, label, source, facts):
        lowered = source.lower()

        # 4.1 Purple ban (hard fail on first match).
        for swatch in BANNED_PURPLES:
            if swatch.lower() in lowered:
                self.issues.append(
                    f"[Color] {label}: PURPLE DETECTED ('{swatch}'). Banned by "
                    f"Maestro rules. Use Teal/Cyan/Emerald instead.")
                break

        # 4.2 60-30-10 sanity check.
        total_colours = len(re.findall(r'#[0-9a-fA-F]{3,6}', source)) \
            + len(re.findall(r'hsl\(', source))
        if total_colours > 3:
            bg_decls = re.findall(r'(?:background|bg-|bg\[)([^;}\s]+)', source)
            fg_decls = re.findall(r'(?:color|text-)([^;}\s]+)', source)
            if len(bg_decls) > 0 and len(fg_decls) > 0:
                distinct = set(re.findall(r'#[0-9a-fA-F]{6}', source))
                if len(distinct) > 5:
                    self.warnings.append(
                        f"[Color] {label}: {len(distinct)} distinct colours. "
                        f"Apply 60-30-10: dominant (60%), secondary (30%), "
                        f"accent (10%).")

        # 4.3 Monochromatic scheme.
        hsl_hues = re.findall(r'hsl\((\d+),\s*\d+%,\s*\d+%\)', source)
        if len(hsl_hues) >= 3:
            hues = [int(h) for h in hsl_hues]
            spread = max(hues) - min(hues)
            if spread < 10:
                self.warnings.append(
                    f"[Color] {label}: Monochromatic palette (hue variance: "
                    f"{spread}deg). Ensure adequate contrast.")

        # 4.4 Dark-mode purity.
        if re.search(r'color:\s*#000000|#000\b', source):
            self.warnings.append(
                f"[Color] {label}: Pure black (#000000) detected. Prefer "
                f"#1a1a1a or darker greys for dark mode.")
        if re.search(r'background:\s*#ffffff|#fff\b', source) and \
                re.search(r'dark:\s*|dark:', source):
            self.warnings.append(
                f"[Color] {label}: Pure white background in a dark-mode "
                f"context. Use a soft off-white (#f9fafb) to ease eye strain.")

        # 4.5 Contrast risk.
        pale_on_pale = bool(re.search(
            r'bg-(?:gray|slate|zinc)-50|bg-white.*text-(?:gray|slate)-[12]',
            source))
        dark_on_dark = bool(re.search(
            r'bg-(?:gray|slate|zinct)-9|bg-black.*text-(?:gray|slate)-[89]',
            source))
        if pale_on_pale or dark_on_dark:
            self.warnings.append(
                f"[Color] {label}: Possible low-contrast pairing. Verify "
                f"WCAG AA (4.5:1 for text).")

        # 4.6 Contextual colour psychology.
        blueish = bool(re.search(
            r'bg-blue|text-blue|from-blue|'
            r'#[0-9a-fA-F]*00[0-9A-Fa-f]{2}|#[0-9a-fA-F]*1[0-9A-Fa-f]{2}',
            source))
        food = bool(re.search(
            r'restaurant|food|cooking|recipe|menu|dish|meal',
            source, re.IGNORECASE))
        if blueish and food:
            self.warnings.append(
                f"[Color] {label}: Blue in a food context. Blue suppresses "
                f"appetite; prefer warm tones (red, orange, yellow).")

        # 4.7 HSL-based palettes.
        if bool(re.search(
                r'--color-|color-|primary-|secondary-', source)) \
                and not re.search(r'hsl\(', source):
            self.warnings.append(
                f"[Color] {label}: Colour variables without HSL. HSL makes "
                f"palette tuning easier (Hue, Saturation, Lightness).")

    # -- 5. animation -----------------------------------------------------

    def _check_animation(self, label, source, facts):
        # 5.1 Duration bounds.
        for amount, unit in re.findall(
                r'(?:duration|animation-duration|transition-duration):'
                r'\s*([\d.]+)(s|ms)', source):
            millis = float(amount) * (1000 if unit == 's' else 1)
            if millis < 50:
                self.warnings.append(
                    f"[Animation] {label}: Very fast animation "
                    f"({amount}{unit}). Use at least 50ms.")
            elif millis > 1000 and 'transition' in source.lower():
                self.warnings.append(
                    f"[Animation] {label}: Long transition ({amount}{unit}). "
                    f"Keep transitions in the 100-300ms range.")

        # 5.2 Easing direction.
        if re.search(r'ease-in\s+.*entry|fade-in.*ease-in', source):
            self.warnings.append(
                f"[Animation] {label}: Entry animation with ease-in. Entries "
                f"should use ease-out for a snappy feel.")
        if re.search(r'ease-out\s+.*exit|fade-out.*ease-out', source):
            self.warnings.append(
                f"[Animation] {label}: Exit animation with ease-out. Exits "
                f"should use ease-in for a natural feel.")

        # 5.3 Interaction micro-feedback.
        clickable = len(re.findall(r'<button|<a\s+href|onClick|@click', source))
        if clickable > 2 and not re.search(
                r'hover:|focus:|:hover|:focus', source):
            self.warnings.append(
                f"[Animation] {label}: Interactive elements without "
                f"hover/focus states. Add micro-interactions for feedback.")

        # 5.4 Loading states.
        async_work = bool(re.search(
            r'async|await|fetch|axios|loading|isLoading', source))
        loading_ui = bool(re.search(
            r'skeleton|spinner|progress|loading|<circle.*animate', source))
        if async_work and not loading_ui:
            self.warnings.append(
                f"[Animation] {label}: Async work without a loading "
                f"indicator. Add a skeleton or spinner for perceived speed.")

        # 5.5 Route transitions.
        routing = bool(re.search(
            r'router|navigate|Link.*to|useHistory', source))
        route_anim = bool(re.search(
            r'AnimatePresence|motion\.|transition.*page|fade.*route', source))
        if routing and not route_anim:
            self.warnings.append(
                f"[Animation] {label}: Routing without page transitions. "
                f"Consider fade/slide for continuity.")

        # 5.6 Scroll-handler performance (hard fail).
        scroll_anim = bool(re.search(
            r'onScroll|scroll.*trigger|IntersectionObserver', source))
        if scroll_anim and re.search(
                r'onScroll.*[^\w](width|height|top|left)', source):
            self.issues.append(
                f"[Animation] {label}: Scroll handler animating layout "
                f"properties. Use transform/opacity for 60fps.")

    # -- 6. motion graphics ----------------------------------------------

    def _check_motion_graphics(self, label, source, facts):
        # 6.1 Lottie fallbacks.
        has_lottie = bool(re.search(r'lottie|Lottie|@lottie-react', source))
        if has_lottie and not re.search(
                r'prefers-reduced-motion.*lottie|lottie.*isPaused|lottie.*stop',
                source):
            self.warnings.append(
                f"[Motion] {label}: Lottie animation without a reduced-motion "
                f"fallback. Provide pause/stop for accessibility.")

        # 6.2 GSAP teardown (hard fail).
        has_gsap = bool(re.search(r'gsap|ScrollTrigger|from\(.*gsap', source))
        if has_gsap and not re.search(
                r'kill\(|revert\(|useEffect.*return.*gsap', source):
            self.issues.append(
                f"[Motion] {label}: GSAP animation without cleanup "
                f"(kill/revert). Risk of a memory leak on unmount.")

        # 6.3 SVG animation cost.
        if len(re.findall(
                r'<animate|<animateTransform|stroke-dasharray|'
                r'stroke-dashoffset', source)) > 3:
            self.warnings.append(
                f"[Motion] {label}: Multiple SVG animations. Use "
                f"stroke-dashoffset sparingly for mobile performance.")

        # 6.4 3D transform setup.
        if bool(re.search(
                r'transform3d|perspective\(|rotate3d|translate3d', source)):
            if not re.search(r'perspective:\s*\d+px|perspective\s*\(', source):
                self.warnings.append(
                    f"[Motion] {label}: 3D transform without a perspective "
                    f"parent. Add perspective: 1000px for realistic depth.")
            self.warnings.append(
                f"[Motion] {label}: 3D transforms detected. Test on mobile; "
                f"they can hurt low-end performance.")

        # 6.5 Particle fallbacks.
        if bool(re.search(
                r'particle|canvas.*loop|requestAnimationFrame.*draw|Three\.js',
                source)):
            self.warnings.append(
                f"[Motion] {label}: Particle effects detected. Provide a "
                f"fallback or reduced-quality mode for mobile.")

        # 6.6 Scroll-driven throttling (hard fail).
        if bool(re.search(
                r'IntersectionObserver.*animate|scroll.*progress|view-timeline',
                source)):
            if not re.search(r'throttle|debounce|requestAnimationFrame', source):
                self.issues.append(
                    f"[Motion] {label}: Scroll-driven animation without "
                    f"throttling. Use requestAnimationFrame for 60fps.")

        # 6.7 Functional vs decorative balance.
        anim_total = (
            len(re.findall(r'@keyframes|transition:|animate-', source))
            + (1 if has_lottie else 0)
            + (1 if has_gsap else 0)
        )
        if anim_total > 5:
            functional = len(re.findall(
                r'hover:|focus:|disabled|loading|error|success', source))
            if functional < anim_total / 2:
                self.warnings.append(
                    f"[Motion] {label}: Many animations ({anim_total}). Ensure "
                    f"most serve a function (feedback, guidance), not "
                    f"decoration.")

    # -- 7. accessibility -------------------------------------------------

    def _check_accessibility(self, label, source, facts):
        # Images need alternative text.
        if re.search(r'<img(?![^>]*alt=)[^>]*>', source):
            self.issues.append(
                f"[Accessibility] {label}: Missing img alt text")

    # -- reporting --------------------------------------------------------

    def build_report(self):
        """Assemble the result payload consumed by the CLI / JSON output."""
        return {
            "files_checked": self.files_checked,
            "issues": self.issues,
            "warnings": self.warnings,
            "passed_checks": self.passed_count,
            "compliant": len(self.issues) == 0,
        }


def render_text_report(report):
    """Print the human-readable summary (ASCII-only for Windows consoles)."""
    print(f"\n[UX AUDIT] {report['files_checked']} files checked")
    print("-" * 50)

    if report['issues']:
        print(f"[!] ISSUES ({len(report['issues'])}):")
        for entry in report['issues'][:10]:
            print(f"  - {entry}")

    if report['warnings']:
        print(f"[*] WARNINGS ({len(report['warnings'])}):")
        for entry in report['warnings'][:15]:
            print(f"  - {entry}")

    print(f"[+] PASSED CHECKS: {report['passed_checks']}")
    print(f"STATUS: {'PASS' if report['compliant'] else 'FAIL'}")


def main(argv=None):
    args = sys.argv if argv is None else argv

    # A path argument is mandatory.
    if len(args) < 2:
        sys.exit(1)

    target = args[1]
    as_json = "--json" in args

    linter = DesignLinter()
    linter.scan_path(target)
    report = linter.build_report()

    if as_json:
        print(json.dumps(report))
    else:
        render_text_report(report)

    # Non-zero exit whenever any hard issue was recorded.
    sys.exit(0 if report['compliant'] else 1)


if __name__ == "__main__":
    main()
