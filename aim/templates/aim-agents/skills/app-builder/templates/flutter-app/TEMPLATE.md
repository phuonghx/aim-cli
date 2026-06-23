---
name: flutter-app
description: Guiding principles for a Flutter mobile starter — Riverpod, Go Router, clean architecture.
---

# Flutter App Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Framework | Flutter 3.x |
| Language | Dart 3.x |
| State | Riverpod 3 (with codegen) |
| Navigation | Go Router |
| HTTP | Dio |
| Storage | Hive |

---

## Folder Layout

```
project_name/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── core/
│   │   ├── constants/
│   │   ├── theme/
│   │   ├── router/
│   │   └── utils/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   └── home/
│   ├── shared/
│   │   ├── widgets/
│   │   └── providers/
│   └── services/
│       ├── api/
│       └── storage/
├── test/
└── pubspec.yaml
```

---

## The Architecture Layers

| Layer | Holds |
|-------|-------|
| Presentation | screens, widgets, providers |
| Domain | entities, use cases |
| Data | repositories, models |

---

## The Key Packages

| Package | Why it's here |
|---------|---------------|
| flutter_riverpod | state management |
| riverpod_annotation | code generation |
| go_router | navigation |
| dio | HTTP client |
| freezed | immutable models |
| hive | local storage |

---

## Getting Set Up

1. `flutter create {{name}} --org com.{{bundle}}`
2. Update `pubspec.yaml`
3. `flutter pub get`
4. Generate code: `dart run build_runner build`
5. `flutter run`

---

## Practices Worth Following

- Lay out folders feature-first (data / domain / presentation inside each feature)
- Use Riverpod 3 with `riverpod_annotation` codegen (the generated ref is just `Ref`; use a plain `Notifier`, no `AutoDisposeNotifier`)
- Pull the legacy `StateProvider` / `StateNotifierProvider` from `package:riverpod/legacy.dart`
- Model immutable data with Freezed
- Navigate declaratively with Go Router
- Theme with Material 3
