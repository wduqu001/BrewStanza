# Design System: BrewStanza
**Project ID:** brewstanza-cli

## 1. Visual Theme & Atmosphere
A restrained, dense, and utilitarian interface tailored for developers. The atmosphere is "Terminal Native" — high contrast, data-dense, and highly functional, resembling a modern developer's IDE or command-line environment. It prioritizes clarity, speed, and typography over decorative elements.

## 2. Color Palette & Roles
- **Terminal Black** (#09090B) — Primary background surface
- **Subtle Surface** (#18181B) — Card and container fill (Zinc-900)
- **Console White** (#FAFAFA) — Primary text, headings
- **Muted Steel** (#A1A1AA) — Secondary text, descriptions, metadata
- **Whisper Border** (rgba(255,255,255,0.1)) — Structural lines, dividers, and faint borders
- **Stanza Blue** (#3B82F6) — Primary accent for branding and core actions (CLI titles)
- **Process Cyan** (#06B6D4) — In-progress states and active task highlights
- **Success Green** (#10B981) — Completed backups and positive reinforcement
- **Warning Yellow** (#F59E0B) — Skipped items, warnings, and alerts
- **Error Red** (#EF4444) — Failures, exceptions, and destructive actions

## 3. Typography Rules
- **Display:** JetBrains Mono — Track-tight, controlled scale, weight-driven hierarchy. Used for headers and primary focal points.
- **Body:** Inter — Relaxed leading, 65ch max-width, neutral secondary color. Used for documentation or web interfaces.
- **Mono:** JetBrains Mono — For code, CLI output, metadata, timestamps, and terminal logs.
- **Banned:** Generic serif fonts (Times New Roman, Georgia) for any UI elements.

## 4. Component Stylings
* **Buttons:** Flat, no outer glow. Tactile -1px translate on active. Accent fill for primary, ghost/outline for secondary.
* **Cards/Containers:** Subtly rounded corners (0.5rem). Diffused whisper shadow. High-density: replace with border-top dividers.
* **Inputs/Forms:** Minimalist underline or faint border. Label above, error below. Focus ring in Stanza Blue.
* **Loaders:** Text-based progress indicators or skeletal shimmer matching exact layout dimensions. No circular spinners.

## 5. Layout Principles
Grid-first responsive architecture. Left-aligned, code-like structure. Strict single-column collapse below 768px. Max-width containment. No flexbox percentage math. Generous internal padding for readability.

## 6. Motion & Interaction
Snappy, instantaneous feedback. Fast spring physics (`stiffness: 100, damping: 20`) for web interactions. No long transitions. Hardware-accelerated transforms only.

## 7. Anti-Patterns (Banned)
- No emojis anywhere (use developer-friendly ASCII or crisp SVGs if needed).
- No pure black (`#000000`), use Terminal Black (`#09090B`).
- No neon/outer glow shadows.
- No rounded-full (pill) buttons, keep edges crisp and utilitarian.
- No 3-column equal card layouts.
- No AI copywriting clichés ("Elevate", "Seamless", "Unleash").
