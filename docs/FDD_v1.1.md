# BrewStanza — Feature Design Document
**Version:** 2.0 (Backup Scripts)
**Stack:** Python 3.11+, Click, Rich
**Target OS:** macOS, Windows WSL

---

## 1. System Architecture

BrewStanza follows a modular architecture where a central CLI menu triggers individual backup modules. Each module is responsible for a specific domain (e.g., Zsh, SSH, Homebrew) and exports data to `~/BrewStanza-Backup/`.

```
src/brewstanza/
├── cli.py               ← Click entry point, command routing / menu
└── backups/
    ├── __init__.py
    ├── claude.py        ← Claude Desktop settings
    ├── zsh.py           ← Zsh configuration
    ├── homebrew.py      ← Homebrew packages (Brewfile)
    ├── fonts.py         ← macOS Fonts
    ├── git.py           ← Git global config
    ├── ssh.py           ← SSH config
    └── apps.py          ← macOS Installed Apps list
```

### 1.1 Module Responsibilities

| Module | Responsibility |
| :--- | :--- |
| **CLI (cli.py)** | Provides a menu to run all backups or select specific ones. Ensures the `~/BrewStanza-Backup/` directory exists. |
| **Claude Backup** | Copies `~/.claude` if it exists. |
| **Zsh Backup** | Copies `~/.zsh` directory and `~/.zshrc`. |
| **Homebrew Backup** | Executes `brew bundle dump --file=~/BrewStanza-Backup/Brewfile`. Skips gracefully on WSL if Homebrew is missing. |
| **Fonts Backup** | Copies `~/Library/Fonts`. Skips on WSL. |
| **Git Backup** | Copies `~/.gitconfig`. |
| **SSH Backup** | Copies `~/.ssh/config`. Explicitly ignores `id_rsa`, `id_ed25519`, and other private/public keys. |
| **Apps Backup** | Enumerates `.app` bundles in `/Applications` and `~/Applications` and writes their names to `apps_list.txt`. Skips on WSL. |

---

## 2. Cross-Platform Handling (WSL vs macOS)

- Modules that interact with macOS-specific paths (`~/Library/Fonts`, `/Applications`) will check `sys.platform == 'darwin'`. If not, they log a "Skipped" message and return gracefully.
- Homebrew relies on the `brew` command being in the PATH. If missing (common on WSL), it skips gracefully.

## 3. Data Model

All modules expose a standard function signature:
```python
def backup(backup_dir: Path) -> bool:
    """Performs the backup and returns True on success or False on skip/error."""
    pass
```
