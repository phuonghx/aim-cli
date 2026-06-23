#!/usr/bin/env python3
"""Static linter for React Native and Flutter source against mobile UX rules.

The scanner walks a project (or a single file), figures out which mobile
framework each file belongs to, and runs a battery of regular-expression
heuristics grouped into themed inspections:

  * touch ergonomics .... target size, spacing, reach, gesture fallbacks,
                          haptics and tap feedback
  * runtime cost ........ list virtualization, memoization, stable keys,
                          native-driver animations, leaks, stray logging
  * navigation .......... tab count, state retention, back handling, links
  * type ................ system fonts, scaling, line height, size bounds,
                          platform type scales, line length, weight balance
  * color ............... pure black, OLED tuning, saturation, contrast,
                          dark-mode text
  * iOS ................. SF symbols/fonts, semantic colors, safe areas, nav
  * Android ............. Material icons/fonts, ripple, elevation, nav rails
  * backend ............. secure storage, offline awareness, push handling
  * quality ............. test tooling, a11y labels, error boundaries

Findings are split into two buckets: blocking ``issues`` and softer
``warnings``. The process exits non-zero when any blocking issue is found,
which makes it usable as a CI gate.

Usage:
    python mobile_audit.py <path> [--json]

Pure standard library, compatible with Python 3.8 and newer.
"""

import json
import os
import re
import sys
from pathlib import Path

# Severity tags used when a check records a finding.
BLOCKING = "issue"
ADVISORY = "warning"

# Folders that never contain reviewable app source.
SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next",
    "ios", "android", ".idea",
}

# File extensions we treat as candidate mobile source.
SOURCE_SUFFIXES = {".tsx", ".ts", ".jsx", ".js", ".dart"}


class FileUnderReview:
    """A single source file plus the framework facts we derive about it.

    Detection is intentionally cheap: we only need to know whether the file
    looks like React Native and/or Flutter so the right checks fire. Files
    that match neither are skipped entirely by the caller.
    """

    RN_SIGNATURE = re.compile(r"react-native|@react-navigation|React\.Native")
    FLUTTER_SIGNATURE = re.compile(r"import 'package:flutter|MaterialApp|Widget\.build")

    def __init__(self, path, text):
        self.path = path
        self.name = os.path.basename(path)
        self.text = text
        self.is_rn = bool(self.RN_SIGNATURE.search(text))
        self.is_flutter = bool(self.FLUTTER_SIGNATURE.search(text))

    @property
    def is_mobile(self):
        """True when the file belongs to either supported framework."""
        return self.is_rn or self.is_flutter


class Ledger:
    """Accumulates findings and a running tally of satisfied checks."""

    def __init__(self):
        self._blocking = []
        self._advisory = []
        self.good_marks = 0
        self.scanned = 0

    def flag(self, severity, source, message):
        """Record one finding, prefixed with the originating file name."""
        line = "[{0}] {1}".format(source.name, message)
        if severity == BLOCKING:
            self._blocking.append(line)
        else:
            self._advisory.append(line)

    def credit(self, amount=1):
        """Note that a positive pattern was satisfied."""
        self.good_marks += amount

    @property
    def blocking(self):
        return self._blocking

    @property
    def advisory(self):
        return self._advisory

    def summary(self):
        """Return the machine-readable report dictionary."""
        return {
            "files_checked": self.scanned,
            "issues": self._blocking,
            "warnings": self._advisory,
            "passed_checks": self.good_marks,
            "compliant": len(self._blocking) == 0,
        }


# --------------------------------------------------------------------------- #
# Touch ergonomics
# --------------------------------------------------------------------------- #

def inspect_touch(unit, ledger):
    """Flag tap targets that are too small, too crowded, or hard to reach."""
    body = unit.text

    # Width/height/size literals in the 0-39 range are below any platform
    # minimum once they describe a tappable element.
    for raw in re.findall(r"(?:width|height|size):\s*([0-3]\d)", body):
        if int(raw) < 44:
            ledger.flag(
                BLOCKING, unit,
                "Touch Target: {0}px is under the 44px floor "
                "(iOS 44pt, Android 48dp)".format(raw),
            )

    # Gaps smaller than 8 invite accidental taps on the neighbour.
    for raw in re.findall(r"(?:margin|gap):\s*([0-7])\s*(?:px|dp)", body):
        if int(raw) < 8:
            ledger.flag(
                ADVISORY, unit,
                "Touch Spacing: {0}px gap risks mis-taps; keep >=8px "
                "between targets".format(raw),
            )

    # Primary calls-to-action should sit low on the screen, in the thumb arc.
    has_primary_cta = re.search(
        r"(?:testID|id):\s*[\"'](?:.*(?:primary|cta|submit|confirm)[^\"']*)[\"']",
        body, re.IGNORECASE,
    )
    sits_low = re.search(
        r"position:\s*[\"']?absolute[\"']?|bottom:\s*\d+|style.*bottom"
        r"|justifyContent:\s*[\"']?flex-end",
        body,
    )
    if has_primary_cta and not sits_low:
        ledger.flag(
            ADVISORY, unit,
            "Thumb Zone: primary CTA may sit outside easy reach; "
            "anchor key actions near the bottom",
        )

    # Swipe affordances need a visible button equivalent for accessibility.
    has_swipe = re.search(r"Swipeable|onSwipe|PanGestureHandler|swipe", body)
    has_button = re.search(
        r"Button.*(?:delete|archive|more)|TouchableOpacity|Pressable", body
    )
    if has_swipe and not has_button:
        ledger.flag(
            ADVISORY, unit,
            "Gestures: swipe actions lack a visible button alternative for "
            "motor-impaired users",
        )

    # Meaningful actions feel better with a haptic confirmation.
    has_action = re.search(
        r"(?:onPress|onSubmit|delete|remove|confirm|purchase)", body
    )
    has_haptics = re.search(
        r"Haptics|Vibration|react-native-haptic-feedback|FeedbackManager", body
    )
    if has_action and not has_haptics:
        ledger.flag(
            ADVISORY, unit,
            "Haptics: consider adding haptic confirmation to important actions",
        )

    # A tappable element with no pressed-state style gives no feedback.
    if unit.is_rn:
        pressables = re.search(r"Pressable|TouchableOpacity", body)
        feedback = re.search(r"pressed|style.*opacity|underlay", body)
        if pressables and not feedback:
            ledger.flag(
                ADVISORY, unit,
                "Touch Feedback: pressable has no visual pressed state; "
                "add an opacity or scale change",
            )


# --------------------------------------------------------------------------- #
# Runtime cost / performance
# --------------------------------------------------------------------------- #

def inspect_performance(unit, ledger):
    """Catch the patterns that wreck scroll, animation, and memory budgets."""
    body = unit.text

    # A ScrollView that maps over data renders everything up front.
    scrollview = re.search(r"<ScrollView|ScrollView\.", body)
    mapped_in_scroll = re.search(r"ScrollView.*\.map\(|ScrollView.*\{.*\.map", body)
    if scrollview and mapped_in_scroll:
        ledger.flag(
            BLOCKING, unit,
            "Performance: ScrollView is mapping a list; switch to FlatList "
            "to avoid mounting every row",
        )

    if unit.is_rn:
        uses_list = re.search(r"FlatList|FlashList|SectionList", body)
        uses_flatlist = re.search(r"FlatList|FlashList", body)
        strict_flatlist = re.search(r"FlatList", body)

        # List rows must be memoized or they re-render with the parent.
        if uses_list and not re.search(r"React\.memo|memo\(", body):
            ledger.flag(
                ADVISORY, unit,
                "Performance: list rows are not wrapped in React.memo; they "
                "re-render on every parent update",
            )

        # renderItem closures should be stabilized with useCallback.
        if uses_flatlist and not re.search(r"useCallback", body):
            ledger.flag(
                ADVISORY, unit,
                "Performance: renderItem is not memoized with useCallback; a "
                "new function is built each render",
            )

        # keyExtractor is mandatory; index keys are a correctness bug.
        if strict_flatlist and not re.search(r"keyExtractor", body):
            ledger.flag(
                BLOCKING, unit,
                "Performance: FlatList is missing keyExtractor; index keys "
                "break on reorder or delete",
            )
        if re.search(r"key=\{.*index.*\}|key:\s*index", body):
            ledger.flag(
                BLOCKING, unit,
                "Performance: index is used as a key; rows recycle wrongly "
                "when the data changes",
            )

        # Animations should run on the native thread where possible.
        animated = re.search(r"Animated\.", body)
        if animated and re.search(r"useNativeDriver:\s*false", body):
            ledger.flag(
                ADVISORY, unit,
                "Performance: useNativeDriver is false; set it true for 60fps "
                "(transform/opacity only)",
            )
        if animated and not re.search(r"useNativeDriver:\s*true", body):
            ledger.flag(
                ADVISORY, unit,
                "Performance: Animated value without useNativeDriver; add "
                "useNativeDriver: true",
            )

        # Effects that subscribe must also unsubscribe.
        effect = re.search(r"useEffect", body)
        cleanup = re.search(r"return\s*\(\)\s*=>|return\s+function", body)
        subscribes = re.search(r"addEventListener|subscribe|\.focus\(\)|\.off\(", body)
        if effect and subscribes and not cleanup:
            ledger.flag(
                BLOCKING, unit,
                "Memory Leak: useEffect subscribes but never returns a "
                "cleanup; the listener leaks on unmount",
            )

        # Too many inline handlers means churn on every render.
        inline = re.findall(
            r"(?:onPress|onPressIn|onPressOut|renderItem):\s*\([^)]*\)\s*=>", body
        )
        if len(inline) > 3:
            ledger.flag(
                ADVISORY, unit,
                "Performance: {0} inline arrow handlers rebuild each render; "
                "hoist them with useCallback".format(len(inline)),
            )

    # Excessive logging stalls the JS thread in production.
    log_count = len(re.findall(
        r"console\.log|console\.warn|console\.error|console\.debug", body
    ))
    if log_count > 5:
        ledger.flag(
            ADVISORY, unit,
            "Performance: {0} console statements found; strip them before "
            "release".format(log_count),
        )

    # Animating layout properties triggers reflow.
    if re.search(r"Animated\.timing.*(?:width|height|margin|padding)", body):
        ledger.flag(
            BLOCKING, unit,
            "Performance: animating layout props (width/height/margin); "
            "animate transform/opacity instead",
        )


# --------------------------------------------------------------------------- #
# Navigation
# --------------------------------------------------------------------------- #

def inspect_navigation(unit, ledger):
    """Check tab counts, state retention, back handling, and deep links."""
    body = unit.text

    # More than five tabs gets cramped and hard to hit.
    tab_count = len(re.findall(
        r"Tab\.Screen|createBottomTabNavigator|BottomTab", body
    ))
    if tab_count > 5:
        ledger.flag(
            ADVISORY, unit,
            "Navigation: {0} tab items exceeds the recommended max of "
            "5".format(tab_count),
        )

    # Tab navigators drop screen state unless lazy is disabled.
    if re.search(r"createBottomTabNavigator|Tab\.Navigator", body):
        if not re.search(r"lazy:\s*false", body):
            ledger.flag(
                ADVISORY, unit,
                "Navigation: tabs may lose state on switch; set lazy: false "
                "to preserve each stack",
            )

    # Custom back logic needs a real listener behind it.
    custom_back = re.search(r"onBackPress|handleBackPress", body)
    back_listener = re.search(
        r"BackHandler|useFocusEffect|navigation\.addListener", body
    )
    if custom_back and not back_listener:
        ledger.flag(
            ADVISORY, unit,
            "Navigation: custom back handling without a BackHandler listener "
            "may not fire",
        )

    # Deep linking without config is fragile; absence of both is fine.
    linking = re.search(r"Linking\.|Linking\.openURL|deepLink|universalLink", body)
    link_config = re.search(r"apollo-link|react-native-screens|navigation\.link", body)
    if not linking and not link_config:
        ledger.credit()
    elif linking and not link_config:
        ledger.flag(
            ADVISORY, unit,
            "Navigation: deep linking present but possibly unconfigured; "
            "verify notification and share flows",
        )


# --------------------------------------------------------------------------- #
# Typography
# --------------------------------------------------------------------------- #

# Approximate iOS HIG text-style sizes, used to judge "native-feeling" scales.
IOS_SCALE = (34, 28, 22, 20, 17, 16, 15, 13, 12, 11)

# Modular-scale ratios designers commonly reach for.
NICE_RATIOS = (1.125, 1.2, 1.25, 1.333, 1.5)


def inspect_typography(unit, ledger):
    """Validate font choices, scaling support, and readable sizing."""
    body = unit.text

    if unit.is_rn:
        custom_font = re.search(r"fontFamily:\s*[\"'][^\"']+", body)
        system_font = re.search(
            r"fontFamily:\s*[\"']?(?:System|San Francisco|Roboto|-apple-system)",
            body,
        )
        if custom_font and not system_font:
            ledger.flag(
                ADVISORY, unit,
                "Typography: custom font without a system fallback; SF Pro "
                "(iOS) / Roboto (Android) read more natively",
            )

        # Fixed sizes should still respect the user's text-size preference.
        if re.search(r"fontSize:", body) and not re.search(
            r"allowFontScaling:\s*true|responsiveFontSize|useWindowDimensions", body
        ):
            ledger.flag(
                ADVISORY, unit,
                "Typography: fixed font sizes with no scaling hook; consider "
                "allowFontScaling for accessibility",
            )

    # Mobile line height above ~1.8 looks loose and wastes space.
    for raw in re.findall(r"lineHeight:\s*([\d.]+)", body):
        if float(raw) > 1.8:
            ledger.flag(
                ADVISORY, unit,
                "Typography: lineHeight {0} is loose for mobile; aim for "
                "1.3-1.5".format(raw),
            )

    # Body text below 12 is hard to read; above 32 usually wants scaling.
    for raw in re.findall(r"fontSize:\s*([\d.]+)", body):
        size = float(raw)
        if size < 12:
            ledger.flag(
                ADVISORY, unit,
                "Typography: fontSize {0}px is below the 12px readability "
                "floor".format(size),
            )
        elif size > 32:
            ledger.flag(
                ADVISORY, unit,
                "Typography: fontSize {0}px is very large; prefer responsive "
                "scaling".format(size),
            )

    sizes = [float(s) for s in re.findall(r"fontSize:\s*([\d.]+)", body)]

    if unit.is_rn and len(sizes) > 3:
        # How many sizes land on (or very near) the iOS scale?
        on_scale = sum(
            1 for s in sizes if any(abs(s - ref) < 1 for ref in IOS_SCALE)
        )
        if on_scale < len(sizes) / 2:
            ledger.flag(
                ADVISORY, unit,
                "iOS Typography: sizes stray from the iOS type scale; reuse "
                "iOS text styles for a native feel",
            )

        # Material display/headline sizes should ship in sp units.
        material_big = re.search(r"fontSize:\s*[456][0-9]|display", body) or \
            re.search(r"fontSize:\s*[23][0-9]|headline", body)
        if material_big and not re.search(r"\d+\s*sp\b", body):
            ledger.flag(
                ADVISORY, unit,
                "Android Typography: Material sizes without sp units; use sp "
                "so text honors the user's font setting",
            )

    # A consistent ratio between steps signals an intentional scale.
    ratio_sizes = sorted({float(s) for s in re.findall(r"fontSize:\s*(\d+(?:\.\d+)?)", body)})
    if len(ratio_sizes) > 3:
        steps = [
            ratio_sizes[i] / ratio_sizes[i - 1]
            for i in range(1, len(ratio_sizes))
            if ratio_sizes[i - 1] > 0
        ]
        for step in steps[:3]:
            if not any(abs(step - r) < 0.03 for r in NICE_RATIOS):
                ledger.flag(
                    ADVISORY, unit,
                    "Typography: step ratio {0:.2f} does not match a common "
                    "modular scale".format(step),
                )
                break

    if unit.is_rn:
        # Long text without a width cap exceeds comfortable line length.
        long_text = re.search(r"<Text[^>]*>[^<]{40,}", body)
        capped = re.search(r"maxWidth|max-w-\d+|width:\s*[\"']?\d+", body)
        if long_text and not capped:
            ledger.flag(
                ADVISORY, unit,
                "Mobile Typography: unconstrained text width; keep lines to "
                "roughly 40-60 characters",
            )

        # Mobile copy reads best regular-dominant, not bold-heavy.
        weight_words = re.findall(
            r"fontWeight:\s*[\"']?(\d+|normal|bold|medium|light)", body
        )
        word_to_num = {"normal": "400", "light": "300", "medium": "500", "bold": "700"}
        numeric = []
        for w in weight_words:
            try:
                numeric.append(int(word_to_num.get(w.lower(), w)))
            except ValueError:
                pass
        heavy = sum(1 for n in numeric if n >= 700)
        normal = sum(1 for n in numeric if 400 <= n < 500)
        if heavy > normal:
            ledger.flag(
                ADVISORY, unit,
                "Mobile Typography: more bold than regular weights; mobile "
                "copy should be regular-dominant",
            )


# --------------------------------------------------------------------------- #
# Color
# --------------------------------------------------------------------------- #

def _saturation(r, g, b):
    """HSV-style saturation of an RGB triple, each channel 0-255."""
    hi, lo = max(r, g, b), min(r, g, b)
    return (hi - lo) / hi if hi else 0.0


def inspect_color(unit, ledger):
    """Review color choices for OLED, contrast, and dark-mode readability."""
    body = unit.text

    # Pure black backgrounds are fine on OLED but harsh for fills/text.
    if re.search(r"#000000|color:\s*black|backgroundColor:\s*[\"']?black", body):
        ledger.flag(
            ADVISORY, unit,
            "Color: pure black detected; near-black (#1C1C1E iOS, #121212 "
            "Android) is gentler and OLED-friendly",
        )

    # No sign of dark-mode handling at all.
    color_scheme = re.search(
        r"useColorScheme|colorScheme|appearance:\s*[\"']?dark", body
    )
    dark_style = re.search(r"\\\?.*dark|style:\s*.*dark|isDark", body)
    if not color_scheme and not dark_style:
        ledger.flag(
            ADVISORY, unit,
            "Color: no dark-mode support detected; wire up useColorScheme",
        )

    # Reward near-black surfaces; nudge other dark backgrounds toward them.
    if re.search(r"#121212|#1A1A1A|#0D0D0D", body):
        ledger.credit()
    elif re.search(r"backgroundColor:\s*[\"']?#000000", body):
        pass  # pure black background is acceptable on OLED
    elif re.search(r"backgroundColor:\s*[\"']?#[0-9A-Fa-f]{6}", body):
        ledger.flag(
            ADVISORY, unit,
            "Color: consider OLED-tuned dark backgrounds (#121212 Android, "
            "#000000 iOS) to save battery",
        )

    # Many highly saturated colors drain OLED panels faster.
    vivid = 0
    for r, g, b in re.findall(r"#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})", body):
        try:
            if _saturation(int(r, 16), int(g, 16), int(b, 16)) > 0.8:
                vivid += 1
        except ValueError:
            pass
    if vivid > 10:
        ledger.flag(
            ADVISORY, unit,
            "Color: {0} highly saturated colors; desaturating saves OLED "
            "power".format(vivid),
        )

    # Likely low-contrast pairings fail outdoors.
    if re.search(
        r"#[EeEeEeEe].*#ffffff|#999999.*#ffffff|#333333.*#000000|#666666.*#000000",
        body,
    ):
        ledger.flag(
            ADVISORY, unit,
            "Color: possible low-contrast pairing; target WCAG AAA (7:1) for "
            "sunlight legibility",
        )

    # In dark mode, pure white text causes glare.
    dark_mode = re.search(
        r"dark:\s*|isDark|useColorScheme|colorScheme:\s*[\"']?dark", body
    )
    if dark_mode and re.search(
        r"color:\s*[\"']?#ffffff|#fff[\"']?\}|textColor:\s*[\"']?white", body
    ):
        ledger.flag(
            ADVISORY, unit,
            "Color: pure white text in dark mode; soften to #E8E8E8 or light "
            "gray",
        )


# --------------------------------------------------------------------------- #
# iOS specifics
# --------------------------------------------------------------------------- #

def inspect_ios(unit, ledger):
    """React Native checks that keep the iOS build feeling like iOS."""
    if not unit.is_rn:
        return
    body = unit.text

    # Icon set present is a small positive signal.
    if re.search(r"@expo/vector-icons|ionicons", body) and not re.search(
        r"sf-symbol|SF Symbols", body
    ):
        ledger.credit()

    # A haptics library should use the typed feedback generators.
    if re.search(r"expo-haptics|react-native-haptic-feedback", body) and not re.search(
        r"ImpactFeedback|NotificationFeedback|SelectionFeedback", body
    ):
        ledger.flag(
            ADVISORY, unit,
            "iOS Haptics: haptics imported but not using typed generators "
            "(Impact/Notification/Selection)",
        )

    # Content needs a safe area or the notch/home indicator clips it.
    if not re.search(r"SafeAreaView|useSafeAreaInsets|safeArea", body):
        ledger.flag(
            ADVISORY, unit,
            "iOS: no safe-area handling; content may hide behind the notch or "
            "home indicator",
        )

    # Prefer SF Pro when a custom font is in play.
    custom_font = re.search(r"fontFamily:\s*[\"'][^\"']+", body)
    if custom_font and not re.search(r"SF Pro|SFPro|fontFamily:\s*[\"']?[-\s]*SF", body):
        ledger.flag(
            ADVISORY, unit,
            "iOS: custom font without an SF Pro fallback (SF Pro Text for "
            "body, Display for headings)",
        )

    # Hardcoded grays should give way to semantic colors.
    semantic = re.search(r"color:\s*[\"']?label|\.label", body) or \
        re.search(r"secondaryLabel|\.secondaryLabel", body)
    if re.search(r"#[78]0{4}", body) and not semantic:
        ledger.flag(
            ADVISORY, unit,
            "iOS: hardcoded grays; semantic colors (label, secondaryLabel) "
            "adapt to dark mode automatically",
        )

    # A custom brand color with no system accent fallback.
    system_accent = (
        re.search(r"#007AFF|#0A84FF|systemBlue", body)
        or re.search(r"#34C759|#30D158|systemGreen", body)
        or re.search(r"#FF3B30|#FF453A|systemRed", body)
    )
    if re.search(r"primaryColor|theme.*primary|colors\.primary", body) and not system_accent:
        ledger.flag(
            ADVISORY, unit,
            "iOS: custom primary color with no system accent fallback; "
            "systemBlue keeps the iOS feel",
        )

    # A nav bar should carry a title for context.
    nav_bar = re.search(r"navigationOptions|headerStyle|cardStyle", body)
    nav_title = re.search(r"title:\s*[\"']|headerTitle|navigation\.setOptions", body)
    if nav_bar and not nav_title:
        ledger.flag(
            ADVISORY, unit,
            "iOS: navigation bar without a title; iOS screens want clear "
            "context up top",
        )

    # Using native iOS components is a positive signal.
    if (
        re.search(r"Alert\.alert|showAlert", body)
        or re.search(r"ActionSheet|ActionSheetIOS|showActionSheetWithOptions", body)
        or re.search(r"ActivityIndicator|ActivityIndic", body)
    ):
        ledger.credit()


# --------------------------------------------------------------------------- #
# Android specifics
# --------------------------------------------------------------------------- #

def inspect_android(unit, ledger):
    """React Native checks that keep the Android build feeling like Material."""
    if not unit.is_rn:
        return
    body = unit.text

    # Material icon set present is a small positive signal.
    if re.search(r"@expo/vector-icons|MaterialIcons", body):
        ledger.credit()

    # Touchables should ripple on Android.
    if re.search(r"Pressable|Touchable", body) and not re.search(
        r"ripple|android_ripple|foregroundRipple", body
    ):
        ledger.flag(
            ADVISORY, unit,
            "Android: touchable without a ripple; Android users expect ripple "
            "feedback",
        )

    # React Navigation needs a back handler for the hardware back button.
    if re.search(r"@react-navigation", body) and not re.search(
        r"BackHandler|useBackHandler", body
    ):
        ledger.flag(
            ADVISORY, unit,
            "Android: React Navigation without a BackHandler; the hardware "
            "back button may misbehave",
        )

    # Prefer Roboto when a custom font is in play.
    custom_font = re.search(r"fontFamily:\s*[\"'][^\"']+", body)
    if custom_font and not re.search(r"Roboto|fontFamily:\s*[\"']?[-\s]*Roboto", body):
        ledger.flag(
            ADVISORY, unit,
            "Android: custom font without a Roboto fallback; Roboto is tuned "
            "for Android displays",
        )

    # Encourage Material 3 theming.
    dynamic_color = re.search(r"MD3|MaterialYou|dynamicColor|useColorScheme", body)
    theme_provider = re.search(r"MaterialTheme|ThemeProvider|PaperProvider", body)
    if not dynamic_color and not theme_provider:
        ledger.flag(
            ADVISORY, unit,
            "Android: no Material 3 dynamic color; theming gives a "
            "personalized feel",
        )

    # CSS shadows should map onto the Material elevation system.
    if re.search(r"boxShadow:", body) and not re.search(
        r"elevation:\s*\d+|shadowOpacity|shadowRadius|android:elevation", body
    ):
        ledger.flag(
            ADVISORY, unit,
            "Android: box-shadow without elevation; use Material elevation for "
            "consistent depth",
        )

    # Two or more Material components is a positive signal.
    material_hits = sum(bool(p) for p in (
        re.search(r"ripple|android_ripple|foregroundRipple", body),
        re.search(r"Card|Paper|elevation.*\d+", body),
        re.search(r"FAB|FloatingActionButton|fab", body),
        re.search(r"Snackbar|showSnackBar|Toast", body),
    ))
    if material_hits >= 2:
        ledger.credit()

    # Bottom nav is thumb-friendly; a lone top app bar is a nudge.
    bottom_nav = re.search(r"BottomNavigation|BottomNav", body)
    top_bar = re.search(r"TopAppBar|AppBar|CollapsingToolbar", body)
    nav_rail = re.search(r"NavigationRail", body)
    if bottom_nav:
        ledger.credit()
    elif top_bar and not (bottom_nav or nav_rail):
        ledger.flag(
            ADVISORY, unit,
            "Android: top app bar without bottom navigation; bottom nav is "
            "easier to reach one-handed",
        )


# --------------------------------------------------------------------------- #
# Backend / data
# --------------------------------------------------------------------------- #

def inspect_backend(unit, ledger):
    """Review storage, offline handling, and push notification wiring."""
    body = unit.text

    # Auth tokens must not live in plain AsyncStorage.
    plain_storage = re.search(r"AsyncStorage|@react-native-async-storage", body)
    secure_storage = re.search(
        r"SecureStore|Keychain|EncryptedSharedPreferences", body
    )
    token_like = re.search(r"token|jwt|auth.*storage", body, re.IGNORECASE)
    if token_like and plain_storage and not secure_storage:
        ledger.flag(
            BLOCKING, unit,
            "Security: auth tokens in AsyncStorage; move them to SecureStore "
            "(iOS) / EncryptedSharedPreferences (Android)",
        )

    # Network code should account for being offline.
    networking = re.search(
        r"fetch|axios|netinfo|@react-native-community/netinfo", body
    )
    offline_aware = re.search(r"offline|isConnected|netInfo|cache.*offline", body)
    if networking and not offline_aware:
        ledger.flag(
            ADVISORY, unit,
            "Offline: network calls without offline handling; check "
            "connectivity with NetInfo",
        )

    # Push imports need a handler or notifications get dropped.
    push = re.search(
        r"Notifications|pushNotification|Firebase\.messaging|PushNotificationIOS",
        body,
    )
    push_handler = re.search(
        r"onNotification|addNotificationListener|notification\.open", body
    )
    if push and not push_handler:
        ledger.flag(
            ADVISORY, unit,
            "Push: notifications imported but no handler; incoming pushes may "
            "be missed",
        )


# --------------------------------------------------------------------------- #
# Quality: testing, accessibility, debugging
# --------------------------------------------------------------------------- #

def inspect_quality(unit, ledger):
    """Review test tooling, accessibility labels, and crash resilience."""
    body = unit.text

    # Detect which test frameworks are in use.
    tools = []
    if re.search(r"jest|describe\(|test\(|it\(", body):
        tools.append("Jest")
    if re.search(r"react-native-testing-library|@testing-library", body):
        tools.append("RNTL")
    if re.search(r"detox|element\(|by\.text|by\.id", body):
        tools.append("Detox")
    if re.search(r"maestro|\.yaml$", body):
        tools.append("Maestro")
    if not tools:
        ledger.flag(
            ADVISORY, unit,
            "Testing: no test framework detected; pair Jest (unit) with "
            "Detox/Maestro (E2E)",
        )

    # Unit tests with no end-to-end coverage leave device behavior untested.
    unit_tests = len(re.findall(r"\.test\.(tsx|ts|js|jsx)|\.spec\.", body))
    e2e_tests = len(re.findall(r"detox|maestro|e2e|spec\.e2e", body.lower()))
    if unit_tests > 0 and e2e_tests == 0:
        ledger.flag(
            ADVISORY, unit,
            "Testing: unit tests but no E2E; mobile needs on-device E2E "
            "coverage",
        )

    if unit.is_rn:
        # Every touchable needs a label for screen readers.
        if re.search(r"Pressable|TouchableOpacity|TouchableHighlight", body) and not re.search(
            r"accessibilityLabel|aria-label|testID", body
        ):
            ledger.flag(
                ADVISORY, unit,
                "A11y: touchable without accessibilityLabel; screen readers "
                "need a label",
            )

    # Heavy logging hurts debugging and performance alike.
    log_count = len(re.findall(r"console\.(log|warn|error|debug|info)", body))
    if log_count > 10:
        ledger.flag(
            ADVISORY, unit,
            "Debugging: {0} console statements; remove before release as they "
            "block the JS thread".format(log_count),
        )

    # Real profiling tools in the file are a positive signal.
    if re.search(r"Performance|systrace|profile|Flipper", body):
        ledger.credit()

    # An error boundary prevents a single failure from killing the app.
    if unit.is_rn and not re.search(
        r"ErrorBoundary|componentDidCatch|getDerivedStateFromError", body
    ):
        ledger.flag(
            ADVISORY, unit,
            "Debugging: no ErrorBoundary; add one to contain render crashes",
        )

    # Hermes ships by default on modern RN; treat as a baseline positive.
    if unit.is_rn:
        ledger.credit()


# Ordered roster of every inspection the scanner runs per file.
INSPECTIONS = (
    inspect_touch,
    inspect_performance,
    inspect_navigation,
    inspect_typography,
    inspect_color,
    inspect_ios,
    inspect_android,
    inspect_backend,
    inspect_quality,
)


class MobileScanner:
    """Drives the inspections over files or whole directory trees."""

    def __init__(self):
        self.ledger = Ledger()

    def scan_file(self, path):
        """Load one file, identify its framework, and run every inspection."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            return

        self.ledger.scanned += 1
        unit = FileUnderReview(path, text)

        # Non-mobile files contribute nothing; bail before running checks.
        if not unit.is_mobile:
            return

        for inspection in INSPECTIONS:
            inspection(unit, self.ledger)

    def scan_tree(self, root):
        """Recurse a directory, skipping vendored and build output folders."""
        for current, subdirs, files in os.walk(root):
            # Prune ignored directories in place so os.walk skips them.
            subdirs[:] = [d for d in subdirs if d not in SKIP_DIRS]
            for filename in files:
                if Path(filename).suffix in SOURCE_SUFFIXES:
                    self.scan_file(os.path.join(current, filename))

    def report(self):
        return self.ledger.summary()


def render_text(report):
    """Print the human-readable form of a report dictionary."""
    print("\n[MOBILE AUDIT] {0} mobile files checked".format(report["files_checked"]))
    print("-" * 50)

    if report["issues"]:
        print("[!] ISSUES ({0}):".format(len(report["issues"])))
        for entry in report["issues"][:10]:
            print("  - {0}".format(entry))

    if report["warnings"]:
        print("[*] WARNINGS ({0}):".format(len(report["warnings"])))
        for entry in report["warnings"][:15]:
            print("  - {0}".format(entry))

    print("[+] PASSED CHECKS: {0}".format(report["passed_checks"]))
    print("STATUS: {0}".format("PASS" if report["compliant"] else "FAIL"))


def main(argv):
    """Parse arguments, run the scan, emit the report, return an exit code."""
    args = argv[1:]
    if not args:
        print("Usage: python mobile_audit.py <path> [--json]")
        return 1

    as_json = "--json" in args
    targets = [a for a in args if not a.startswith("--")]
    if not targets:
        print("Usage: python mobile_audit.py <path> [--json]")
        return 1
    target = targets[0]

    scanner = MobileScanner()
    if os.path.isfile(target):
        scanner.scan_file(target)
    else:
        scanner.scan_tree(target)

    report = scanner.report()

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        render_text(report)

    # Non-zero exit when blocking issues exist, so CI can fail the build.
    return 0 if report["compliant"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
