# BrewStanza — Product Requirements Document
**Version:** 2.0 (Pivoted to Backup Scripts)
**Status:** MVP in development

---

## 1. Executive Summary

BrewStanza is a modular Python CLI tool that provides developers with an actionable way to backup and restore their critical "dotfiles" and application configurations. It replaces the old disk-scanning approach with targeted backup scripts that gather configurations for tools like Claude, Zsh, Homebrew, SSH, Git, Fonts, and macOS installed applications. 
It supports macOS primarily but gracefully skips macOS-specific tasks on Windows WSL environments.

---

## 2. Project Identity

| Attribute | Value |
| :--- | :--- |
| **Project name** | BrewStanza |
| **Tech stack** | Python 3.11+, Click, Rich |
| **Target OS** | macOS, Windows WSL |
| **Distribution** | PyPI |
| **Repository** | `github.com/<user>/brewstanza` |

---

## 3. Problem Statement

Developers need an easy, actionable way to back up specific configurations and dotfiles so that restoring an environment on a new machine is trivial. Instead of a monolithic disk scanner, the tool should be broken down into testable, specific backup scripts that export configurations to a single directory (`~/BrewStanza-Backup/`).

---

## 4. Goals

- Provide a single CLI menu to trigger individual modular backup scripts.
- Support targeted backups for: `.claude`, `.zsh`, Homebrew (Brewfile), macOS Fonts, `.gitconfig`, `.ssh/config` (ignoring keys), and a list of installed macOS apps.
- Store backups centrally in `~/BrewStanza-Backup/`.
- Ensure cross-platform compatibility (macOS and WSL) by skipping macOS-specific scripts gracefully.

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
├── cli.py               ← CLI menu and orchestrator
└── backups/
    ├── claude.py        ← Copies ~/.claude
    ├── zsh.py           ← Copies ~/.zsh and ~/.zshrc
    ├── homebrew.py      ← Generates Brewfile via brew bundle dump
    ├── fonts.py         ← Copies ~/Library/Fonts
    ├── git.py           ← Copies ~/.gitconfig
    ├── ssh.py           ← Copies ~/.ssh/config (ignores keys)
    └── apps.py          ← Lists /Applications to apps_list.txt
```
