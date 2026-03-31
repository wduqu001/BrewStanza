> A minimalist macOS CLI tool for managing Homebrew packages, installed applications, and storage analytics.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[!acOS](https://img.shields.io/badge/macOS-Tahoe+-silver.svg)](https://www.apple.com/macos/)

## ✨ Features

### MVP (v1.0)

- **🍺 Homebrew Management**
  - List installed formulae and casks with sizes
  - Show package descriptions and details
  - Detect outdated packages
  - Generate uninstall commands

- **📱 Application Scanner**
  - Scan `/Applications` and `~/Applications`
  - Calculate app sizes on demand
  - Auto-categorize apps (Development, Productivity, Media, Utilities, Browser Apps, Games)
  - Show manual removal instructions

- **💾 Storage Analytics**
  - Total Homebrew storage
  - Total Application storage
  - Category breakdown
  - Top storage consumers

- **📤 Export & Sync**
  - Export to JSON, Markdown, or Brewfile
  - GitHub repository sync
  - Private repository support

### Phase 2 (Planned)

- **🤖 AI Configuration Scanner** - Manage Claude, Gemini, Cursor, and other AI tool configs
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

# List all Homebrew packages
brewstanza brew list

# List only formulae
brewstanza brew list --formula

# List only casks
brewstanza brew list --cask

# Show package details
brewstanza brew info node@20

# List all installed applications
brewstanza apps list

# List apps by category
brewstanza apps list --category

# Show app details with removal instructions
brewstanza apps info "Visual Studio Code"

# Show storage breakdown
brewstanza storage

# Export configuration
brewstanza export json
brewstanza export markdown
brewstanza export brewfile

# Sync to GitHub
brewstanza sync --repo yourusername/my-mac-setup
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
| `brew list` | List all installed packages (formulae + casks) |
| `brew list --formula` | List only formulae |
| `brew list --cask` | List only casks |
| `brew info <package>` | Show package details |
| `brew outdated` | List outdated packages |

### `brewstanza apps`

Scan and manage installed applications.

| Command | Description |
|---------|-------------|
| `apps list` | List all installed applications |
| `apps list --category` | List apps grouped by category |
| `apps info <app>` | Show app details with removal instructions |

### `brewstanza storage`

Display storage analytics.

| Command | Description |
|---------|-------------|
| `storage` | Show complete storage breakdown |
| `storage --top N` | Show top N storage consumers |
| `storage --category` | Show breakdown by category only |

### `brewstanza export`

Export configuration to files.

| Command | Description |
|---------|-------------|
| `export json` | Export to JSON format |
| `export markdown` | Export to Markdown format |
| `export brewfile` | Export to Brewfile format |
| `export --output <path>` | Specify output directory |

### `brewstanza sync`

Sync configuration to GitHub.

| Option | Description |
|--------|-------------|
| `--repo <repo>` | Target repository (format: owner/repo) |
| `--token <token>` | GitHub personal access token (or set `GITHUB_TOKEN` env) |
| `--message <msg>` | Custom commit message |

## 📁 Application Categories

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

BrewStanza uses a TOML configuration file at `~/.config/brewstanza/config.toml`:

```toml
[general]
default_format = "json"
color_output = true

[github]
token_file = "~/.config/brewstanza/github_token"
default_repo = "yourusername/my-mac-setup"

[scan]
app_directories = [
    "/Applications",
    "~/Applications"
]
exclude_patterns = [
    ".*\\.app/.*"  # Skip app bundle internals
]

[categories]
# Custom category mappings
"com.microsoft.VSCode" = "Development"
"com.spotify.client" = "Media"
```

## 🛠️ Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/brewstanza.git
cd brewstanza

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=brewstanza
```

### Project Structure

```
brewstanza/
├── src/
│   └── brewstanza/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entry point
│       ├── scanner/
│       │   ├── __init__.py
│       │   ├── homebrew.py     # Homebrew package scanner
│       │   └── apps.py         # Application scanner
│       ├── analyzer/
│       │   ├── __init__.py
│       │   └── storage.py      # Storage calculation
│       ├── exporter/
│       │   ├── __init__.py
│       │   ├── json_export.py
│       │   ├── markdown.py
│       │   └── github.py
│       └── ui/
│           ├── __init__.py
│           └── renderer.py     # Rich terminal output
├── tests/
│   ├── __init__.py
│   ├── test_homebrew.py
│   ├── test_apps.py
│   └── test_storage.py
├── pyproject.toml
├── README.md
├── TODO.md
├── LICENSE
└── CHANGELOG.md
```

### Running Locally

```bash
# Install in development mode
pip install -e .

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
