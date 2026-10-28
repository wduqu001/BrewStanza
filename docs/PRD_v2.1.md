# BrewStanza — Product Requirements Document
**Version:** 2.1 (Versioned Backup Packages)
**Status:** Backup CLI implemented; restore remains future work

---

## 1. Executive Summary

BrewStanza is a modular Python CLI tool for creating targeted backups of developer configuration and application references. It supports Claude, Zsh, Homebrew, SSH, Git, Fonts, and macOS application listings. Runs create timestamped, versioned packages under a configurable destination. Initialization selects the integrity mode: Git-backed destinations receive local commits, while destinations initialized without Git use SHA-256 checksums. Restore is planned but is not implemented.

---

## 2. Project Identity

| Attribute | Value |
| :--- | :--- |
| **Project name** | BrewStanza |
| **Tech stack** | Python 3.11+, Click, Rich |
| **Target OS** | macOS, Linux (including WSL) |
| **Distribution** | PyPI |
| **Repository** | `github.com/wduqu001/BrewStanza` |

---

## 3. Problem Statement

Developers need an easy, actionable way to back up specific configurations and dotfiles for migration to another machine. BrewStanza uses targeted, testable backup modules and writes each run as a timestamped package under one destination root (default `~/BrewStanza-Backup/`).

---

## 4. Goals

- Provide `init` and `backup` CLI commands, with interactive component selection and `--all` execution.
- Support targeted backups for: `.claude`, `.zsh`, Homebrew (Brewfile), macOS Fonts, `.gitconfig`, `.ssh/config` (ignoring keys), and a list of installed macOS apps.
- Store timestamped packages under a configurable destination (default `~/BrewStanza-Backup/`) with a versioned JSON manifest and home-relative restore targets.
- Use the integrity mode selected at initialization: local Git commits for Git-backed destinations or SHA-256 checksums otherwise. Never push automatically.
- Ensure cross-platform compatibility by gracefully skipping macOS-specific modules when unsupported.

---

## 5. Non-Goals

- Disk usage scanning and storage analytics.
- Automated restoration (v1 handles backup/export only).
- Backing up sensitive SSH private keys.
- Backing up actual `.app` bundles (only their names are listed).

---

## 6. Technical Architecture

### 6.1 Tech Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| Language | Python 3.11+ | Cross-platform (macOS/WSL), robust CLI ecosystem |
| CLI framework | Click | Subcommand and menu support |
| TUI library | Rich | Professional CLI styling |
| Testing | pytest | Standard Python testing |

### 6.2 Project Structure

```
src/brewstanza/
├── cli.py               ← init/backup commands and orchestration
└── backups/
    ├── package.py       ← Package initialization, manifests, checksums, Git commits
    ├── results.py       ← Structured success/skipped/failed results
    ├── safety.py        ← Destination and source-overlap validation
    ├── transaction.py   ← Safe replacement of backup artifacts
    ├── claude.py        ← Copies ~/.claude/settings.json only
    ├── zsh.py           ← Copies ~/.zsh and ~/.zshrc
    ├── homebrew.py      ← Generates a Brewfile
    ├── fonts.py         ← Copies ~/Library/Fonts
    ├── git.py           ← Copies ~/.gitconfig
    ├── ssh.py           ← Copies ~/.ssh/config only
    └── apps.py          ← Writes apps_manifest.json and apps_list.txt
```
