# Versioned Backup Package Design

## Goal

Define portable, versioned backup snapshots that can be restored on another machine and stored in a private dotfiles Git repository.

## Package layout

The configured destination is the package repository root. Each backup run creates a timestamped child directory containing `manifest.json` and the files copied by selected backup modules. The manifest records a format version, creation time, completion status, included modules, and for each copied file its package-relative location and restore destination relative to the user's home directory. It must not store machine-specific absolute paths as restore destinations. Reference artifacts such as the app list and Brewfile use `restore_path: null`.

The package contains only files selected by existing backup modules and their existing safety rules. Git remotes and pushes are outside this design.

## Initialization and versioning

`brewstanza init` prepares the destination. It refuses to change an existing non-empty directory unless it is already a BrewStanza package or is inside an existing Git repository. Git operations are scoped to the BrewStanza marker and snapshot directory, leaving unrelated repository contents untouched. If Git is installed and no containing repository exists, it initializes Git when needed. If Git is unavailable, package manifests include SHA-256 checksums for copied files. `backup` automatically initializes only a new or empty destination; otherwise the user must initialize it explicitly or use an existing BrewStanza package or Git repository.

When the destination is a Git repository, each complete backup run is committed locally as one commit containing that timestamped package. BrewStanza does not push. A run with any failed module is retained as a partial package and is not committed. Skipped modules do not by themselves make a run partial.

## Safety and compatibility

The manifest format is explicitly versioned so later restore code can reject or handle unsupported versions. Package file paths are relative and must be validated against traversal before restore. Existing backup destination protections continue to apply. Package creation must preserve the last complete snapshot if copying fails.

## Out of scope

- Restore preview and restore execution, tracked by subsequent TODO items.
- Homebrew restore workflow.
- App categorization and the interactive TUI.
- Remote Git configuration, authentication, and pushing.
- SHA-256 generation when Git is managing the destination.

## Self-review

- No placeholders remain; paths, manifest fields, Git behavior, partial-run behavior, and exclusions are stated.
- “Complete” means no module failed; skipped modules are allowed, matching the current structured backup results.
- The format is designed to be portable without assuming a future restore implementation or a remote Git service.
