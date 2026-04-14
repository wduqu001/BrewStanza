# BrewStanza — Product Requirements Document
**Version:** 1.1 (March 2026)
**Status:** MVP in development

---

## 1. Executive Summary

BrewStanza is a Python CLI tool that gives macOS developers a **single command to snapshot and restore their entire development environment**. It inventories Homebrew packages and installed applications, measures their disk footprint, and commits a reproducible configuration to GitHub — so moving to a new Mac is a one-command operation.

The v1.1 revision narrows scope to keep the tool focused: leftover file scanning, Markdown export, and per-app detail commands have been removed. What remains is lean, defensible, and shippable in three weeks.

---

## 2. Project Identity

| Attribute | Value |
| :--- | :--- |
| **Project name** | BrewStanza |
| **Tech stack** | Python 3.11+, asyncio, Click, Rich, TOML |
| **Target OS** | macOS Tahoe — Apple Silicon M1/M2/M3/M4 |
| **Distribution** | Homebrew tap + PyPI |
| **Repository** | `github.com/<user>/brewstanza` |

---

## 3. Problem Statement

A developer getting a new Mac faces a multi-hour manual process: reinstalling Homebrew, hunting down packages from memory, reconfiguring dotfiles, and discovering missing tools only when something breaks. Existing tools address pieces of this — Homebrew handles packages, AppCleaner handles cleanup — but nothing ties the full picture together in a developer-centric CLI workflow.

---

## 4. Goals

- Provide a single tool to snapshot the full software inventory (Homebrew + apps) with storage sizes
- Generate a Brewfile and JSON export that reproduce the environment on a fresh Mac
- Sync the snapshot to GitHub automatically so it stays current with zero friction
- Ship a polished, well-tested open-source project worthy of a senior engineering portfolio

---

## 5. Non-Goals (v1.1)

- Automated app uninstallation (BrewStanza shows sizes and uninstall commands; it does not execute them)
- `~/Library` leftover scanning — deferred; too much sandboxing friction for v1
- App categorisation via `Info.plist` — deferred to v2.0
- Cross-platform support (macOS only by design)
- GUI or web interface

---

## 6. Target Audience

| Audience | Need |
| :--- | :--- |
| **Primary — the developer themselves** | Maintain a live snapshot of their Mac; migrate cleanly to new hardware |
| **Secondary — potential employers** | Review portfolio; assess code quality, architecture decisions, documentation |
| **Tertiary — open-source community** | Reuse or extend the tool; contribute Homebrew tap formula |

---

## 7. Competitive Landscape

| Tool | Focus | BrewStanza gap |
| :--- | :--- | :--- |
| `brew bundle` | Brewfile export only | No app inventory, no storage data, no GitHub sync |
| mackup | Dotfile sync | No package inventory, no storage analysis |
| AppCleaner | App removal + leftovers | No Homebrew integration, no export, no sync |
| CleanMyMac | Full disk cleaner | Paid, GUI-only, no CLI or export |

**Unique position:** BrewStanza is the only tool that combines Homebrew inventory, app discovery, storage analytics, and GitHub sync in a single developer-centric CLI.

---

## 8. Feature Requirements

### 8.1 Homebrew Management

| Feature | Priority | Approach |
| :--- | :--- | :--- |
| List installed formulae | High | `brew list --formula` via subprocess |
| List installed casks | High | `brew list --cask` via subprocess |
| Show package metadata | High | `brew info --json` |
| Disk usage per package | High | Cellar paths fed to async `DiskScanner` |
| Detect outdated packages | Medium | `brew outdated` |
| Generate upgrade/uninstall commands | High | String formatting from package names |

### 8.2 Application Scanning

| Feature | Priority | Approach |
| :--- | :--- | :--- |
| Scan `/Applications` | High | `pathlib` glob for `.app` bundles |
| Scan `~/Applications` | High | `Path.home() / "Applications"` |
| Show size per app | High | Async `DiskScanner` on demand |
| Show primary path | High | Resolved from glob result |

### 8.3 Storage Analytics

| Feature | Priority | Approach |
| :--- | :--- | :--- |
| Total Homebrew storage | High | Aggregate from `ScanSummary` |
| Total application storage | High | Aggregate from `ScanSummary` |
| Top 10 consumers | High | `ScanSummary.top(10)` |
| Percentage share per item | Medium | `size / total * 100` |

### 8.4 Export

| Format | Priority | Use case |
| :--- | :--- | :--- |
| JSON | High | Machine-readable full snapshot |
| Brewfile | High | `brew bundle install` for environment restore |

### 8.5 GitHub Sync

| Feature | Priority | Approach |
| :--- | :--- | :--- |
| Commit export to GitHub | High | subprocess git + PAT from config.toml |
| Timestamped commit messages | High | `datetime.now().isoformat()` |
| Private repository support | High | PAT-based HTTPS authentication |
| First-run config wizard | Medium | Prompt for PAT, write config.toml |

---

## 9. Technical Architecture

### 9.1 Tech Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| Language | Python 3.11+ | No Xcode required; rich ecosystem; easy distribution |
| Concurrency | asyncio | I/O-bound disk scanning; integrates with Click via `asyncio.run()` |
| CLI framework | Click | Battle-tested; subcommand support; auto-generated help |
| TUI library | Rich | Tables, progress bars, panels; `transient=True` for clean scan output |
| Config | TOML | Human-readable; version-control friendly |
| Testing | pytest + pytest-asyncio | Async test support; subprocess mocking via `pytest-mock` |
| Distribution | Homebrew tap + PyPI | Native macOS install experience |

### 9.2 Project Structure

```
brewstanza/
├── cli.py
├── scanner/
│   ├── homebrew.py
│   ├── apps.py
│   └── disk.py          ← async DiskScanner
├── analyzer/
│   └── storage.py
├── exporter/
│   └── export.py
└── ui/
    └── renderer.py
tests/
├── scanner/
│   ├── test_homebrew.py
│   ├── test_apps.py
│   └── test_disk.py     ← mock subprocess calls
├── analyzer/
│   └── test_storage.py
└── exporter/
    └── test_export.py
.github/
└── workflows/
    └── ci.yml           ← pytest + ruff + mypy on every push
```

---

## 10. Command Reference

| Command | Description |
| :--- | :--- |
| `brewstanza brew list` | Lists Homebrew packages with sizes |
| `brewstanza brew info <pkg>` | Shows detailed package metadata |
| `brewstanza apps list` | Lists installed apps with path and size |
| `brewstanza storage` | Displays storage breakdown and top 10 consumers |
| `brewstanza export [json\|brewfile]` | Exports inventory to file |
| `brewstanza sync` | Commits latest export to GitHub |

---

## 11. Development Timeline

### Week 1 — Foundation
- Project scaffold: `pyproject.toml`, `src/` layout, pytest config, GitHub Actions CI
- `HomebrewScanner` — `brew list`, `brew info --json`, `brew outdated`
- `AppScanner` — glob `.app` bundles in both locations
- `DiskScanner` — async scanner with `asyncio.Semaphore`, `ScanResult`, `ScanSummary`
- Unit tests for all three scanners (mocked subprocess)

### Week 2 — Core features
- `StorageAnalyzer` — aggregation, top-N, percentage share
- `brewstanza brew list`, `brewstanza apps list`, `brewstanza storage` commands
- Rich output: tables with inline size bars, progress bar during scanning
- Integration test: run against live Homebrew on dev machine

### Week 3 — Export, sync, polish
- `ExportManager` — JSON serialisation, Brewfile generation
- `brewstanza export`, `brewstanza sync` commands
- First-run config wizard (PAT prompt, write `config.toml`)
- README with install instructions, demo GIF, and `--demo` flag for reviewers
- Publish Homebrew tap formula

---

## 12. Success Metrics

| Metric | Target |
| :--- | :--- |
| Test coverage | ≥ 80% (enforced in CI) |
| CI pipeline | pytest + ruff + mypy green on every push |
| Scan performance | Full app scan completes in under 5 seconds on a typical Mac |
| Distribution | Installable via `brew install` from a public tap |
| Portfolio signal | Public GitHub repo with README, demo GIF, and passing CI badge |
