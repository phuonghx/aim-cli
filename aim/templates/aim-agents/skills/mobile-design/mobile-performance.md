# Mobile Performance Reference

> Keeping React Native and Flutter at 60fps: virtualized lists, native-thread animation, disciplined memory and battery use.
> This is the area where generated mobile code most often falls down.

---

## 1. The frame budget

A phone is not a workstation. Power, RAM, thermal headroom, and the network are all constrained, while the user's patience is shorter than on desktop.

```
desktop assumption        mobile reality
──────────────────        ──────────────
plenty of power           battery is finite
spare RAM                 RAM is shared and tight
stable network            network drops and stalls
CPU always free           CPU throttles when hot
fast is nice              instant is expected
```

Every frame has a hard deadline:

```
60fps  → 16.67ms per frame
120fps → 8.33ms per frame  (ProMotion)
```

Blow the budget and frames drop. Dropped frames read as "slow" or "broken," and that is what gets an app uninstalled.

---

## 2. React Native

### The classic mistake: a ScrollView full of rows

```jsx
// Wrong — mounts every row at once
<ScrollView>
  {rows.map(row => <RowCard key={row.id} row={row} />)}
</ScrollView>
```

With a thousand rows that is a thousand simultaneous mounts: memory spikes, the first paint takes seconds, and scrolling stutters. A virtualized list renders only what is near the viewport.

```jsx
// Right — FlatList virtualizes
<FlatList data={rows} renderItem={renderRow} keyExtractor={r => r.id} />
```

### Tuning a FlatList

```jsx
// 1. Memoize the row so it ignores unrelated parent renders
const RowCard = React.memo(({ row }: { row: Row }) => (
  <Pressable style={styles.row}><Text>{row.title}</Text></Pressable>
));

// 2. Stabilize renderItem so it is not rebuilt each render
const renderRow = useCallback(
  ({ item }: { item: Row }) => <RowCard row={item} />,
  [],
);

// 3. Stable key from the data — never the array index
const getKey = useCallback((row: Row) => row.id, []);

// 4. For fixed-height rows, skip async measurement
const measure = useCallback(
  (_: Row[] | null, index: number) => ({
    length: ROW_HEIGHT,
    offset: ROW_HEIGHT * index,
    index,
  }),
  [],
);

<FlatList
  data={rows}
  renderItem={renderRow}
  keyExtractor={getKey}
  getItemLayout={measure}
  removeClippedSubviews        // detach off-screen views (esp. Android)
  maxToRenderPerBatch={10}
  windowSize={5}               // ~2 screens of buffer each side
  initialNumToRender={10}
  updateCellsBatchingPeriod={50}
/>
```

### Why each prop earns its place

| Prop | Prevents | Priority |
|------|----------|----------|
| `React.memo` | rows re-rendering on parent change | critical |
| `useCallback` on renderItem | a fresh closure every render | critical |
| stable `keyExtractor` | wrong row recycling | critical |
| `getItemLayout` | async layout passes | high |
| `removeClippedSubviews` | memory from off-screen rows | high |
| `maxToRenderPerBatch` | long main-thread blocks | medium |
| `windowSize` | excess memory | medium |

### When FlatList is not enough

```jsx
import { FlashList } from "@shopify/flash-list";

<FlashList
  data={rows}
  renderItem={renderRow}
  estimatedItemSize={ROW_HEIGHT}
  keyExtractor={getKey}
/>
```

FlashList recycles more aggressively, uses less memory, needs fewer tuning props, and has a simpler API.

### Animation: stay on the native thread

```jsx
// Wrong — driven by the JS thread, stutters under load
Animated.timing(v, { toValue: 1, duration: 300, useNativeDriver: false }).start();

// Right — runs on the UI thread
Animated.timing(v, { toValue: 1, duration: 300, useNativeDriver: true }).start();
```

The native driver supports only `transform` (translate, scale, rotate) and `opacity`. It cannot animate width, height, `backgroundColor`, border radius, margin, or padding.

For anything the native driver cannot handle, reach for Reanimated, which runs worklets on the UI thread:

```jsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';

function Card() {
  const x = useSharedValue(0);
  const style = useAnimatedStyle(() => ({ transform: [{ translateX: withSpring(x.value) }] }));
  return <Animated.View style={style} />;
}
```

### Don't leak

```jsx
// Wrong — the interval outlives the component
useEffect(() => {
  const id = setInterval(poll, 5000);
}, []);

// Right — clean it up
useEffect(() => {
  const id = setInterval(poll, 5000);
  return () => clearInterval(id);
}, []);
```

Usual culprits: timers, event listeners, sockets and subscriptions, async work that sets state after unmount, and unbounded image caches.

### RN checklist

```
Lists
- [ ] FlatList / FlashList, not ScrollView
- [ ] renderItem wrapped in useCallback
- [ ] rows wrapped in React.memo
- [ ] keyExtractor uses a stable id
- [ ] getItemLayout for fixed heights

Animation
- [ ] useNativeDriver: true where possible
- [ ] Reanimated for the complex cases
- [ ] only transform / opacity animated
- [ ] tested on a cheap Android phone

Release
- [ ] console.* stripped
- [ ] every useEffect cleans up
- [ ] profiler shows no leak
- [ ] measured in a release build
```

---

## 3. Flutter

### The classic mistake: setState too high

```dart
// Wrong — rebuilds the whole subtree on every tick
class _CounterState extends State<Counter> {
  int _n = 0;
  void _bump() => setState(() => _n++);

  @override
  Widget build(BuildContext context) => Column(children: [
    Text('Count: $_n'),
    ExpensiveWidget(),        // rebuilt needlessly
    AnotherExpensive(),       // rebuilt needlessly
  ]);
}
```

### `const` is the cheap win

```dart
// Right — const children never rebuild
class _CounterState extends State<Counter> {
  int _n = 0;

  @override
  Widget build(BuildContext context) => Column(children: [
    Text('Count: $_n'),
    const ExpensiveWidget(),   // skipped on rebuild
    const AnotherExpensive(),  // skipped on rebuild
  ]);
}
```

Rule of thumb: mark every widget `const` that does not depend on changing state.

### Rebuild narrowly

```dart
// Wrong — whole tree rebuilds
setState(() => _value = next);

// Right — only the listener rebuilds
ValueListenableBuilder<int>(
  valueListenable: counter,
  builder: (context, value, _) => Text('$value'),
  child: const Icon(Icons.star),   // not rebuilt
);
```

With Riverpod or Provider, select the slice you need instead of watching the whole object:

```dart
// Wrong — rebuilds on any field change
final state = ref.watch(profileProvider);
return Text(state.name);

// Right — rebuilds only when name changes
final name = ref.watch(profileProvider.select((s) => s.name));
return Text(name);
```

### Lists and images

```dart
// Wrong — builds all children up front
ListView(children: rows.map((r) => RowTile(r)).toList());

// Right — lazy
ListView.builder(
  itemCount: rows.length,
  itemBuilder: (context, i) => RowTile(rows[i]),
  itemExtent: 56,     // fixed height speeds layout
  cacheExtent: 100,
);

// With dividers
ListView.separated(
  itemCount: rows.length,
  itemBuilder: (context, i) => RowTile(rows[i]),
  separatorBuilder: (context, _) => const Divider(),
);
```

```dart
// Cache images and decode them at display size
CachedNetworkImage(
  imageUrl: url,
  width: 100, height: 100, fit: BoxFit.cover,
  memCacheWidth: 200, memCacheHeight: 200,   // 2x for retina
  placeholder: (c, _) => const Skeleton(),
  errorWidget: (c, _, __) => const Icon(Icons.error),
);
```

### Always dispose

```dart
class _ScreenState extends State<Screen> {
  late final StreamSubscription _sub;
  late final AnimationController _anim;
  late final TextEditingController _text;

  @override
  void initState() {
    super.initState();
    _sub = stream.listen((_) {});
    _anim = AnimationController(vsync: this);
    _text = TextEditingController();
  }

  @override
  void dispose() {
    _text.dispose();   // reverse order of creation
    _anim.dispose();
    _sub.cancel();
    super.dispose();
  }
}
```

### Flutter checklist

```
Widgets
- [ ] const constructor where no runtime args
- [ ] const on static children
- [ ] minimal setState scope
- [ ] provider selectors, not whole-object watches

Lists
- [ ] ListView.builder, not ListView(children:)
- [ ] itemExtent for fixed heights
- [ ] cached, sized images

Release
- [ ] every dispose() implemented
- [ ] no print() in production
- [ ] measured in profile/release mode
- [ ] performance overlay checked
```

---

## 4. Animation on both platforms

The eye is unforgiving:

```
< 24 fps   slideshow
24-30 fps  choppy
30-45 fps  visibly rough
45-60 fps  acceptable
60 fps     the target
120 fps    premium (ProMotion)
```

### GPU vs CPU

```
cheap (GPU-composited)      expensive (forces layout)
──────────────────────      ─────────────────────────
transform: translate        width / height
transform: scale            top / left / right / bottom
transform: rotate           margin / padding
opacity                     animated border-radius
                            animated box-shadow
```

Animate `transform` and `opacity`. Everything else recalculates layout.

### Durations

| Kind | Duration | Easing |
|------|----------|--------|
| micro-interaction | 100-200ms | ease-out |
| standard transition | 200-300ms | ease-out |
| page transition | 300-400ms | ease-in-out |
| dramatic | 400-600ms | ease-in-out |
| loading skeleton | 1000-1500ms | linear loop |

### Spring physics

```jsx
// Reanimated
withSpring(target, { damping: 15, stiffness: 150, mass: 1 });
```

```dart
// Flutter
SpringSimulation(
  SpringDescription(mass: 1, stiffness: 150, damping: 15),
  start, end, velocity,
);
```

Natural ranges: damping 10-20 (bouncy → settled), stiffness 100-200 (loose → tight), mass 0.5-2 (light → heavy).

---

## 5. Memory

| Source | Platform | Fix |
|--------|----------|-----|
| timers | both | clear on cleanup/dispose |
| listeners | both | remove on cleanup/dispose |
| subscriptions | both | cancel on cleanup/dispose |
| large images | both | cap cache, resize |
| async after unmount | RN | mounted check / AbortController |
| animation controllers | Flutter | dispose them |

Images are the silent killer. Decoded size is `width × height × 4` bytes:

```
1080p  1920 × 1080 × 4 ≈ 8.3 MB
4K     3840 × 2160 × 4 ≈ 33.2 MB
ten 4K images ≈ 332 MB → crash
```

Always decode to display size (2-3x for retina).

Profile with React Native DevTools, Xcode Instruments, or Android Studio Profiler on the RN side; the DevTools Memory tab or `flutter run --profile` on Flutter.

---

## 6. Battery

| Drain | Severity | Mitigation |
|-------|----------|------------|
| screen on | highest | dark mode on OLED |
| continuous GPS | very high | significant-change updates |
| network requests | high | batch and cache hard |
| animations | medium | dial back on low battery |
| background work | medium | defer the non-urgent |
| heavy CPU | lower | push to the backend |

On OLED, black pixels are simply off and draw no power:

```
#000000 true black → maximum savings
#1a1a1a near black → modest savings
any color          → some draw
#FFFFFF white      → maximum draw
```

Background work has hard platform limits: iOS uses system-scheduled refresh, push for urgent updates, a short list of background modes, and ~30-second tasks. Android offers WorkManager (battery-aware), foreground services (visible, continuous), JobScheduler for batched network, and Doze mode you must respect.

---

## 7. Network

Read from cache first, then refresh from the network in the background:

```
UI  →  Cache (answer immediately)  →  Network (update the cache)
```

That gives instant rendering for cached data, offline capability, less data use, and a better experience on slow links.

To reduce request cost: batch many small calls into one (the radio wakes once), cache with ETag / `If-None-Match` / `Cache-Control` and stale-while-revalidate, and compress with gzip/brotli, request only needed fields (GraphQL), and paginate.

---

## 8. Testing performance

| Metric | Target | Tool |
|--------|--------|------|
| frame rate | ≥ 60fps | performance overlay |
| memory | flat, no growth | profiler |
| cold start | < 2s | manual timing |
| time to interactive | < 3s | tracing |
| list scroll | no jank | feel + profiler |
| animation | no drops | performance monitor |

Test on real, modest hardware:

```
do not trust         do trust
────────────         ────────
simulators (fast)    a cheap Android phone (< $200)
dev builds (slow)    an older iPhone (8 or SE)
flagships only       a release/profile build
10-item datasets     production-scale data
```

---

## 9. Quick card

```jsx
// RN list
<FlatList
  data={data}
  renderItem={useCallback(({item}) => <MemoRow row={item} />, [])}
  keyExtractor={useCallback(r => r.id, [])}
/>
// RN animation: useNativeDriver: true
// RN effect: always return a cleanup
```

```dart
// Flutter widgets: const everywhere static
// Flutter lists: ListView.builder
// Flutter state: ValueListenableBuilder / ref.watch(p.select(...))
// Flutter cleanup: dispose() controllers
```

```
animate: transform + opacity only
budget:  16.67ms / frame
target:  60fps minimum
test on: a low-end Android device
```

---

> Performance is not a polish step; it is baseline quality. A slow app is a broken app. Benchmark against the worst phone your users carry, not the best one on your desk.
