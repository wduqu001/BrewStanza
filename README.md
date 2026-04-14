# BrewStanza

> Reproducible Mac migration for developers — in one CLI.

[![CI](https://github.com/wduqu001/brewstanza/actions/workflows/ci.yml/badge.svg)](https://github.com/wduqu001/brewstanza/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://img.shields.io/badge/macOS-Tahoe+-silver.svg)](https://www.apple.com/macos/)

BrewStanza helps you answer a simple question quickly:

**“What exactly is installed on this Mac, and how do I recreate it on another one?”**

It focuses on the essentials:

- Homebrew inventory (formulae + casks)
- Installed app inventory (`.app` bundles)
- Storage analytics (what is taking space)
- Export to JSON/Brewfile for repeatable migration

## Why people use BrewStanza

- **Migrate faster:** move from old Mac to new Mac without guesswork.
- **Keep environments reproducible:** export snapshots you can version.
- **Stay lightweight:** no heavy agent, no full-screen UI required.

## What’s in v1.1

The v1.1 scope is intentionally focused on migration outcomes:

- ✅ Async concurrent disk scanning (`du -sk` + semaphore) for faster size analysis
- ✅ JSON export for automation
- ✅ Brewfile export for `brew bundle` restore flows
- ✅ GitHub sync with timestamped commits

Removed/deferred in v1.1 (by design):

- ❌ `~/Library` leftover scanning
- ❌ Markdown export
- ❌ `apps info <app>` detail flow
- ⏭️ Auto-categorization of apps (deferred to v2)

See `docs/FDD_v1.1.md` for full design rationale.

## Installation

### Homebrew (recommended)

```bash
brew tap yourusername/brewstanza
brew install brewstanza
```

### pip

```bash
pip install brewstanza
```

### From source

```bash
git clone https://github.com/wduqu001/brewstanza.git
cd brewstanza
pip install -e .
```

## Quick start

```bash
# Check install
brewstanza --version

# Homebrew inventory
brewstanza brew list
brewstanza brew info node@20
brewstanza brew outdated

# Applications + storage
brewstanza apps list
brewstanza storage

# Export migration artifacts
brewstanza export json
brewstanza export brewfile

# Sync latest snapshot to GitHub
brewstanza sync
```

## Command guide

| Area | Command | What it does |
|---|---|---|
| Homebrew | `brewstanza brew list` | Lists installed formulae/casks |
| Homebrew | `brewstanza brew info <pkg>` | Shows package metadata |
| Homebrew | `brewstanza brew outdated` | Shows outdated packages |
| Apps | `brewstanza apps list` | Lists installed `.app` bundles |
| Storage | `brewstanza storage` | Shows aggregate usage + top consumers |
| Export | `brewstanza export json` | Writes machine-readable inventory |
| Export | `brewstanza export brewfile` | Writes restore-ready Brewfile |
| Sync | `brewstanza sync` | Commits snapshot to configured repo |

Global flags:

- `--help` shows usage
- `--version` shows installed version
- `--no-color` disables ANSI formatting

## Configuration

Config file path:

- `~/.config/brewstanza/config.toml`

Example:

```toml
[github]
token      = "ghp_..."
repository = "user/dotfiles"
branch     = "main"

[scanner]
concurrency = 8
timeout     = 30
```

### GitHub sync notes

- Works with private repositories
- Commit messages include timestamps for easy history tracking
- If config is missing, first-run setup should guide token/repository entry

## Architecture (at a glance)

```text
brewstanza/
├── cli.py
├── scanner/
│   ├── homebrew.py
│   ├── apps.py
│   └── disk_scanner.py
├── analyzer/
│   └── storage.py
├── exporter/
│   └── export.py
└── ui/
    └── renderer.py
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest
ruff check src/ tests/
mypy src/
```

## Roadmap (v2+)

- App auto-categorization
- AI config inventory support
- Dependency tree insights
- Interactive TUI experience

## Contributing

Pull requests are welcome. For larger changes, open an issue first so we can align scope and design.

## License

MIT — see `LICENSE`.
