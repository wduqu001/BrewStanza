# BrewStanza development checklist

The current product is the backup orchestrator described in
[PRD_v2.1.md](PRD_v2.1.md). Storage analytics, GitHub synchronization, and
automated restore are future work and are not implemented CLI commands.

## Current implementation

- [x] Click CLI with `--version`, `init`, and `backup` commands
- [x] Interactive component selection and `--all` execution
- [x] Configurable backup destination
- [x] Timestamped backup packages with a versioned JSON manifest
- [x] Local Git commits or SHA-256 integrity when Git is unavailable
- [x] Dry-run backup planning
- [x] Claude, Zsh, Homebrew, Fonts, Git, SSH, and Apps modules
- [x] Versioned application manifest with legacy app-list compatibility
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

- [x] Define the versioned backup/restore package format
- [ ] Add restore preview and path/overwrite safety validation
- [ ] Implement limited restore for configuration files and directories
- [ ] Add a separate Homebrew restore workflow
- [ ] Add app categorization to the structured application manifest
- [ ] Add an interactive TUI on top of the backup planning model
