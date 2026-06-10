# Changelog

All notable changes to the AIM CLI and Control Hub project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-06-10

### Added
- Integrated the raw `taste-skill` ruleset under `aim/skills/taste-skill/SKILL.md` and `aim/templates/aim-agents/skills/taste-skill/SKILL.md` to govern default agent design behaviors on initialization.
- Imported the clean `@phosphor-icons/web` icon set via CDN to evict emojis across all dashboard tabs, headers, metric cards, list nodes, and form components.

### Changed
- Refactored the dashboard CSS variables and templates to conform to a professional dark-mode Zinc palette (Neutral slate theme with `#09090b` background, `#18181b` surface/cards, and `#27272a` borders) and a singular accent Indigo (`#6366f1` / hover `#4f46e5`).
- Unified all component border-radii across buttons, input fields, badges, tabs, cards, and modals to a strict, clean `6px`.
- Implemented snappy active transitions (`transform: scale(0.97)`) on all UI buttons for immediate tactile feedback.

---

## [1.1.0] - 2026-06-09

### Added
- Implemented HTML5 drag-and-drop operations for Kanban board task cards, automatically persisting column moves back to task markdown files.
- Added manual task creation via a `+ New Task` modal form.
- Added live priority editing dropdown inside the task detail modal.
- Added manual task deletion with referential integrity (automatically cleaning up/removing child subtasks and updating markdown files).

---

## [1.0.0] - 2026-06-08

### Added
- Initial release of AIM (Agent Integration Module) CLI and dashboard.
- Key features: local status compilation, task listing, doc library indexing, and project metadata setup.
