# BrewStanza development checklist

The current product is the backup orchestrator described in
[PRD_v1.1.md](PRD_v1.1.md). Inventory scanning, storage analytics, JSON export,
GitHub synchronization, and automated restore are future work and are not
implemented CLI commands.

## Current implementation

- [x] Click CLI with `--version` and `backup` command
- [x] Interactive component selection and `--all` execution
- [x] Configurable backup destination
- [x] Claude, Zsh, Homebrew, Fonts, Git, SSH, and Apps modules
- [x] Homebrew availability and macOS-only module checks
- [x] Destination overlap protection
- [x] Unit and integration tests
- [x] Ruff and strict mypy checks

## Next implementation phases

### Safety and reliability

- [x] Replace whole-directory Claude backup with an explicit safe-file allowlist
- [x] Exclude tokens, credentials, history, caches, logs, and local state
- [x] Document exactly which files each module copies
- [x] Return structured success, skipped, and failed results
- [x] Preserve existing backups when a replacement copy fails
- [x] Replace broad exception handlers with specific expected exceptions
- [x] Add Homebrew subprocess timeout and diagnostics
- [x] Validate destination type, permissions, and symlink resolution

### Tests and CI

- [x] Test partial copy failures and permission errors
- [x] Test sensitive-file exclusion
- [x] Test Homebrew timeout and nonzero exit status
- [x] Test CLI exit status for failed modules
- [x] Test supported Python versions in CI
- [x] Build and smoke-test the installed wheel in CI
- [x] Test graceful behavior on non-macOS platforms

### Future features

- [ ] Add dry-run support
- [ ] Write a structured application manifest
- [ ] Define and implement a versioned restore format
- [ ] Add automated restore only after backup policy is stable
- [ ] Add app categorization and an interactive TUI
