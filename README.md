> A minimalist macOS CLI tool for managing Homebrew packages, installed applications, and storage analytics.

[![CI](https://github.com/yourusername/brewstanza/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/brewstanza/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://img.shields.io/badge/macOS-Tahoe+-silver.svg)](https://www.apple.com/macos/)

## ✨ Features

### MVP (v1.0)

- **🍺 Homebrew Management**
  - List installed formulae and casks with sizes on demand
  - Show package descriptions and versions
  - Detect outdated packages with upgrade commands

- **📱 Application Scanner**
  - Scan `/Applications` and `~/Applications` for installed `.app` bundles
  - Calculate app sizes on demand via concurrent async `du` calls
  - Fast, non-blocking operations with semaphore-controlled concurrency

- **💾 Storage Analytics**
  - Aggregate total disk usage for Homebrew packages and applications
  - Top 10 storage consumers with percentage share and inline bars
  - Side-by-side comparison of Homebrew vs. Application storage

- **📤 Export & Sync**
  - Export to **JSON** (full machine-readable snapshot) and **Brewfile** (standard `brew bundle` format)
  - GitHub repository sync with timestamped commits
  - Private repository support via Personal Access Token (PAT)

### Phase 2 (Planned)

- **🤖 AI Configuration Scanner** - Manage Claude, Gemini, Cursor, and other AI tool configs
- **📂 Auto-categorize apps** - Group applications by type (Development, Productivity, Media, etc.)
- **🧹 Orphaned File Detection** - Find leftover files from uninstalled apps
- **🌳 Dependencies Tree** - Visualize package dependencies
- **🖥️ Interactive TUI** - Full-screen terminal interface

## 📦 Installation

### Via Homebrew (Recommended)

```bash
brew tap yourusername/brewstanza
brew install brewstanza
```

### Via pip

```bash
pip install brewstanza
```

### From Source

```bash
git clone https://github.com/yourusername/brewstanza.git
cd brewstanza
pip install -e .
```

## 🚀 Quick Start

```bash
# Show version
brewstanza --version

# List all Homebrew packages (formulae + casks)
brewstanza brew list

# List only formulae or casks
brewstanza brew list --formula
brewstanza brew list --cask

# Show package details and cellar path
brewstanza brew info node@20

# List outdated packages
brewstanza brew outdated

# List all installed applications with sizes
brewstanza apps list

# Show comprehensive storage breakdown
brewstanza storage

# Export to JSON or Brewfile
brewstanza export json
brewstanza export brewfile

# Sync current inventory to GitHub
brewstanza sync
```

## 📖 Command Reference

### Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version number |
| `--help` | Show help message |
| `--no-color` | Disable colored output |

### `brewstanza brew`

Manage Homebrew packages.

| Command | Description |
|---------|-------------|
| `brew list` | List all packages (formulae + casks) with version and disk size |
| `brew list --formula` | List only formulae |
| `brew list --cask` | List only casks |
| `brew info <package>` | Show package description, version, cellar path, and size |
| `brew outdated` | List outdated packages with upgrade recommendations |

### `brewstanza apps`

Scan and manage installed applications.

| Command | Description |
|---------|-------------|
| `apps list` | List all installed applications with path and disk size |
| `apps list --json` | Output as JSON for scripting |

### `brewstanza storage`

Display storage analytics.

| Command | Description |
|---------|-------------|
| `storage` | Show Homebrew vs. Application storage comparison with top 10 consumers |
| `storage --json` | Output as JSON for scripting |
| `storage --no-color` | Disable colored terminal output |

### `brewstanza export`

Export current inventory to files.

| Command | Description |
|---------|-------------|
| `export json` | Export full inventory snapshot to `brewstanza-snapshot.json` |
| `export brewfile` | Export packages to `Brewfile` (standard `brew bundle` format) |
| `export --output <path>` | Specify output directory (default: current directory) |

### `brewstanza sync`

Sync configuration to GitHub.

| Option | Description |
|--------|-------------|
| `--repo <repo>` | Target repository (format: owner/repo) |
| `--token <token>` | GitHub personal access token (or set `GITHUB_TOKEN` env) |
| `--message <msg>` | Custom commit message |

## 📁 Application Categories (Phase 2)

Auto-categorization by app bundle type is planned for v2.0. Categories will include:

| Category | Examples |
|----------|----------|
| **Development** | Xcode, VS Code, JetBrains IDEs, Docker, Terminal |
| **Productivity** | Microsoft Office, Notion, Slack, Zoom |
| **Media** | Spotify, VLC, Adobe Creative Suite |
| **Utilities** | Alfred, Rectangle, 1Password |
| **Browser Apps** | Chrome Apps, Edge Apps, PWAs |
| **Games** | Steam, Epic Games |
| **Other** | Everything else |

## 🤖 Phase 2: AI Configuration Scanner

BrewStanza will support scanning AI tool configurations:

| AI Tool | Config Path |
|---------|-------------|
| Claude Code | `~/.claude/` |
| Gemini | `~/.gemini/` |
| Cursor | `~/.cursor/` |
| Windsurf | `~/.windsurf/` |
| Aider | `~/.aider*` |
| OpenCode | `~/.opencode/` |

```bash
# Phase 2 commands
brewstanza ai list              # List all detected AI configs
brewstanza ai info claude       # Show Claude config details
brewstanza ai backup            # Backup all AI configs
brewstanza ai sync              # Sync AI configs to GitHub
```

## ⚙️ Configuration

BrewStanza uses a TOML configuration file at `~/.config/brewstanza/config.toml` (auto-created on first run):

```toml
[github]
token      = "ghp_..."             # Personal Access Token (required for sync)
repository = "yourusername/dotfiles" # Target repository (can be private)
branch     = "main"

[scanner]
concurrency = 8              # Max concurrent du subprocesses (default: 8)
timeout     = 30             # Seconds before abandoning a path scan (default: 30)
```

**First-run wizard:** Run `brewstanza sync` without config to be prompted for your GitHub PAT and repository.

## 🛠️ Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/brewstanza.git
cd brewstanza

# Create virtual environment (recommended: .venv)
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=brewstanza
```

### Project Structure

```
brewstanza/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
├── src/
│   └── brewstanza/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entry point
│       ├── scanner/
│       │   ├── __init__.py
│       │   ├── homebrew.py     # Homebrew package scanner
│       │   ├── apps.py         # Application scanner
│       │   └── disk_scanner.py # Disk usage analysis
│       ├── analyzer/
│       │   ├── __init__.py
│       │   └── storage.py      # Storage calculation & aggregation
│       ├── exporter/
│       │   ├── __init__.py
│       │   └── export.py       # Export to JSON, Brewfile, etc.
│       └── ui/
│           ├── __init__.py
│           └── renderer.py     # Rich terminal output
├── tests/
│   ├── __init__.py
│   ├── analyzer/
│   │   └── test_storage.py
│   ├── cli/
│   │   └── test_cli.py
│   ├── scanner/
│   │   ├── test_apps.py
│   │   └── test_homebrew.py
│   ├── exporter/
│   │   └── test_exporter.py
│   └── ui/
│       └── test_renderer.py
├── docs/
│   ├── README.md
│   ├── TODO.md
│   ├── PRD_v1.1.md
│   └── FDD_v1.1.md
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=brewstanza --cov-fail-under=80

# Lint with ruff
ruff check src/ tests/

# Type-check with mypy
mypy src/

# Run CLI directly
python -m brewstanza --help

# Or use the installed command
brewstanza --help
```



## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Homebrew](https://brew.sh/) - The missing package manager for macOS
- [Click](https://click.palletsprojects.com/) - Python CLI framework
- [Rich](https://github.com/Textualize/rich) - Python library for rich text and beautiful formatting
- Inspired by [Claude Code](https://claude.ai/) and [OpenCode](https://opencode.ai/) CLI designs

---

<p align="center">
  Made with ❤️ for macOS developers
</p>
