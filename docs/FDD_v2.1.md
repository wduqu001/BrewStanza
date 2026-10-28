# BrewStanza — Feature Design Document
**Version:** 2.1 (Versioned Backup Packages)
**Stack:** Python 3.11+, Click, Rich
**Target OS:** macOS, Linux (including WSL)

---

## 1. System Architecture

BrewStanza uses a Click CLI with `init` and `backup` commands. Backup modules write selected artifacts into a staging directory; the package layer publishes a timestamped snapshot under the configured destination root (default `~/BrewStanza-Backup/`).

```
src/brewstanza/
├── cli.py               ← Click entry point, command routing / menu
└── backups/
    ├── __init__.py
    ├── package.py       ← Package initialization, manifests, checksums, Git commits
    ├── results.py       ← Structured module results
    ├── safety.py        ← Destination and source-overlap validation
    ├── transaction.py   ← Safe artifact replacement
    ├── claude.py        ← Allowlisted Claude settings
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
| **CLI (cli.py)** | Provides `init` and `backup`; backup auto-initializes new/empty destinations and adopts an existing package or Git repository. |
| **Package layer** | Publishes timestamped directories containing `data/` and a versioned `manifest.json`; initialization selects Git-backed local commits or SHA-256 checksums. Never pushes. |
| **Claude Backup** | Copies only `~/.claude/settings.json`; other files are excluded. |
| **Zsh Backup** | Copies `~/.zsh` directory and `~/.zshrc`. |
| **Homebrew Backup** | Generates `data/Brewfile` in the staged package. Skips gracefully when Homebrew is missing. The Brewfile is reference data, not a restore target. |
| **Fonts Backup** | Copies `~/Library/Fonts`. Skips on non-macOS systems. |
| **Git Config Backup** | Copies `~/.gitconfig`. |
| **SSH Backup** | Copies `~/.ssh/config`. Explicitly ignores `id_rsa`, `id_ed25519`, and other private/public keys. |
| **Apps Backup** | Enumerates `.app` bundles in `/Applications` and `~/Applications`, writing `apps_manifest.json` and legacy `apps_list.txt`. Skips on non-macOS systems. |

---

## 2. Cross-Platform Handling

- Modules that interact with macOS-specific paths (`~/Library/Fonts`, `/Applications`) will check `sys.platform == 'darwin'`. If not, they log a "Skipped" message and return gracefully.
- Homebrew relies on the `brew` command being in the PATH. If missing (common on WSL), it skips gracefully.

## 3. Data Model

All modules expose a standard function signature:
```python
def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
    """Return success, skipped, or failed status with a diagnostic message."""
    pass
```

`BackupResult` also records the component name and number of backup artifacts
created. A directory copy counts as one artifact rather than counting every
file inside the directory.
