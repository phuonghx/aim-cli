# Mobile Debugging Guide

> Put down the `console.log`. Mobile apps have a native layer underneath the JavaScript, and text logs alone will not reach it.
> This is about debugging mobile effectively, not by guesswork.

---

## The mindset

A browser tab gives you DevTools, a network panel, and a refresh button. A mobile app gives you a JS bridge sitting on top of native UI, GPU and memory pressure, and multiple threads — and you cannot simply refresh.

```
web                     mobile
───                     ──────
browser DevTools        JS ↔ native bridge
network tab             native UI layer
one runtime             GPU / memory / threads
```

Four things that bite repeatedly:

1. **There is a native layer.** If the JavaScript looks fine but the app dies, suspect the native side (Java/Kotlin, Obj-C/Swift).
2. **You cannot just refresh.** State gets lost or stuck between reloads.
3. **The network is harder to see.** SSL pinning and proxy setup get in the way.
4. **Device logs are the truth.** `adb logcat` and Console are where the real story is.

---

## Reflexes to replace

| Reflex | Mobile-correct move |
|--------|---------------------|
| "add more console.logs" | React Native DevTools / Reactotron |
| "check the network tab" | Charles / Proxyman |
| "it works on the simulator" | run it on a real device (hardware-specific bugs) |
| "reinstall node_modules" | clean the native build (Gradle / Pod caches) |
| ignore the native logs | read logcat / Xcode logs |

---

## 1. The toolset

### React Native and Expo

| Tool | Covers | Best for |
|------|--------|----------|
| Reactotron | state, API, Redux | JS-side debugging |
| React Native DevTools | console, network, components, profiler | the default debugger (RN 0.76+) |
| Expo tools | element inspector | quick UI checks |

### The native layer

| Tool | Platform | How | Use for |
|------|----------|-----|---------|
| Logcat | Android | `adb logcat` | native crashes, ANRs |
| Console | iOS | via Xcode | native exceptions, memory |
| Layout Inspector | Android | Android Studio | view-hierarchy bugs |
| View Debugger | iOS | Xcode | view-hierarchy bugs |

---

## 2. Workflows

### "The app crashed" — red screen or back to the home screen?

```
Red screen (JS error)
  cause: undefined is not an object, a bad import
  fix:   read the on-screen stack trace; it is usually clear

Crash to the home screen (native crash)
  cause: native module failure, out-of-memory, using a permission you never declared
  tools: Android → adb logcat *:E   (errors only)
         iOS     → Xcode → Window → Devices → View Device Logs
```

> An immediate crash on launch is almost always native configuration — `Info.plist` or `AndroidManifest.xml`.

### "The request failed" — network

On the web you open the network tab. On mobile you usually cannot see it directly.

```
React Native DevTools / Reactotron   inspect requests in the monitoring app
proxy (Charles / Proxyman)           harder to set up, but shows ALL traffic,
                                     including native SDKs (requires an SSL cert on the device)
```

### "The UI is laggy" — performance

Measure; do not guess.

```
React Native   Performance Monitor (shake menu)
Android        "Profile GPU Rendering" in Developer Options

JS FPS drop    heavy computation on the JS thread
UI FPS drop    too many views, a deep hierarchy, heavy images
```

---

## 3. Platform headaches

```
Android
  Gradle sync fails      usually a Java version mismatch or duplicate classes
  emulator networking    localhost is 10.0.2.2, not 127.0.0.1
  stale builds           ./gradlew clean is your friend

iOS
  CocoaPods trouble      pod deintegrate && pod install
  signing errors         check Team ID and Bundle Identifier
  stale cache            Xcode → Product → Clean Build Folder
```

---

## Checklist

- [ ] Is it a JS crash or a native crash? (red screen vs home screen)
- [ ] Did you do a clean build? (native caches are stubborn)
- [ ] Are you on a real device? (simulators hide concurrency bugs)
- [ ] Did you read the native logs, not just the terminal?

> When the JavaScript looks perfect but the app still fails, look harder at the native side.
