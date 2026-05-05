# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-05

### Added
- **ExportManager**: Support for exporting inventory snapshots to JSON and Brewfile formats.
- **GitHub Sync**: Automatic synchronization of inventory snapshots to a GitHub repository with timestamped commits.
- **Setup Wizard**: Interactive first-run configuration for GitHub integration.
- **Extended Storage Analytics**: More detailed breakdown and improved concurrency in disk scanning.
- **Comprehensive Test Suite**: Increased test coverage to 95%.

### Changed
- Refactored CLI to use the new `ExportManager` and `GitHubSync` modules.
- Improved error handling for GitHub authentication and subprocess failures.
- Updated documentation and added development guidelines.

### Removed
- Markdown export (redundant with Rich terminal output).

## [1.0.0] - 2026-04-14

### Added
- Initial release of BrewStanza.
- Basic Homebrew and Application inventory scanning.
- Simple storage breakdown.
