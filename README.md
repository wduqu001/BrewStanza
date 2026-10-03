# BrewStanza

> Back up the developer configuration that matters — in one CLI.

[![CI](https://github.com/wduqu001/brewstanza/actions/workflows/ci.yml/badge.svg)](https://github.com/wduqu001/brewstanza/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://img.shields.io/badge/macOS-Tahoe+-silver.svg)](https://www.apple.com/macos/)

BrewStanza creates a portable backup directory for the configuration and
environment files developers commonly need when moving to another machine.
It works on macOS and Linux/WSL, skipping macOS-only modules when they are
not available. It focuses on targeted backups rather than copying an entire
home directory.

## Why people use BrewStanza

- **Migrate faster:** collect important configuration files without guesswork.
- **Avoid unnecessary exposure:** SSH keys are never copied, while the
  sensitive-file policy for other configuration directories is being tightened.
- **Stay lightweight:** no background agent or full-screen UI is required.

## Current scope

The current release provides one command, `brewstanza backup`, with modules for:

- Claude configuration
- Zsh configuration
- Homebrew packages (`Brewfile`)
- User fonts on macOS
- Global Git configuration
- SSH client configuration (never private keys)
- Installed macOS application names

The project does not currently provide storage analytics, JSON inventory
exports, GitHub synchronization, or automated restore. Those are future
features, not supported commands.

See [docs/PRD_v1.1.md](docs/PRD_v1.1.md) and
[docs/FDD_v1.1.md](docs/FDD_v1.1.md) for the current backup design.

## Installation

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

# Back up every supported component
brewstanza backup --all

# Back up selected components interactively
brewstanza backup

# Use a custom destination
brewstanza backup --dest "$HOME/BrewStanza-Backup"
```

## Command guide

| Area | Command | What it does |
|---|---|---|
| Backup | `brewstanza backup --all` | Runs every available backup module |
| Backup | `brewstanza backup` | Prompts for individual components |
| Destination | `brewstanza backup --dest PATH` | Writes backups to a custom directory |

Global flags:

- `--help` shows usage
- `--version` shows installed version

## Backup policy

The default destination is `~/BrewStanza-Backup/`. The CLI rejects the home
directory as a destination, and modules reject destinations that overlap their
sources. Review the destination before running a full backup.

The Claude module copies only `~/.claude/settings.json`; credentials, history,
caches, logs, and unknown files are excluded. The SSH module copies only
`~/.ssh/config`; private and public keys are not copied. Each module reports
when its source is unavailable and skips it rather than failing the whole
command.

## Architecture (at a glance)

```text
brewstanza/
├── cli.py
└── backups/
    ├── apps.py
    ├── claude.py
    ├── fonts.py
    ├── git.py
    ├── homebrew.py
    ├── safety.py
    ├── ssh.py
    └── zsh.py
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python -m pytest
python -m ruff check src/ tests/
python -m mypy src/
```

## Roadmap

- Explicit allowlists for sensitive configuration directories
- Transactional backups that preserve the previous backup on failure
- Dry-run support
- Richer application manifest output
- Automated restore after the backup format is stable
- App auto-categorization
- Interactive TUI experience

## Contributing

Pull requests are welcome. For larger changes, open an issue first so we can align scope and design. See [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup.

## License

MIT — see `LICENSE`.
