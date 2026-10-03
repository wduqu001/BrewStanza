# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-05

### Added
- **Backup orchestrator**: Run all or selected configuration backups from one CLI.
- **Backup modules**: Added Claude, Zsh, Homebrew, Fonts, Git, SSH, and macOS
  application backup modules.
- **Destination safety checks**: Reject the home directory globally and reject
  source-overlapping destinations in filesystem-copy modules.
- **Comprehensive test suite**: Added unit and integration coverage for the
  backup modules and CLI.

### Changed
- Refactored the project around targeted backup scripts instead of inventory
  scanning and storage analytics.
- Added graceful skipping for unavailable macOS-only sources and Homebrew.
- Updated documentation and development guidelines for the backup workflow.

### Removed
- Inventory scanning, storage analytics, JSON export, and GitHub sync commands
  are not part of the current backup-oriented release.

## [1.0.0] - 2026-04-14

### Added
- Initial release of BrewStanza.
- Basic Homebrew and Application inventory scanning.
- Simple storage breakdown.
