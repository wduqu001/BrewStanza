# Migration inventory files — design

## Goal

Make a BrewStanza snapshot easier to use when moving to a new workspace or
computer by separating install/configuration reference lists from the package
manifest.

## Snapshot layout

Each snapshot will include two optional, human-readable text files at its root:

```text
20261116T120000Z/
├── data/
├── fonts_list.txt
├── manifest.json
└── zsh_plugins.txt
```

`manifest.json` remains the package metadata and file-integrity/restore map. It
will not include entries for either inventory file. The inventories are
reference material and are intentionally not restore targets.

## Font inventory

When the Fonts module succeeds, BrewStanza writes `fonts_list.txt`. It lists the
font files available in the backed-up `data/Fonts` directory, one relative path
per line, sorted deterministically. A short comment header explains that the
file is a checklist for installing fonts on a new macOS machine.

The existing `data/Fonts` backup remains unchanged. The list does not claim an
installation source because local font files cannot reliably identify whether a
font originated from Homebrew, a vendor download, or another installer.

## Zsh plugin inventory

When the Zsh module succeeds, BrewStanza writes `zsh_plugins.txt`. It lists the
top-level directories in the backed-up `data/.zsh` directory, one per line,
sorted deterministically. A header explains that it is an inventory only and
that the user must install the matching plugin manager or source each plugin as
their `.zshrc` requires.

This deliberately avoids guessing which directories are plugins: a hand-rolled
Zsh configuration may keep custom functions, themes, completions, and plugins
in the same directory. Listing all top-level entries is complete, transparent,
and avoids false installation advice.

If `.zsh` is absent or the Zsh backup fails, no plugin inventory is produced.

## Generation point

Package creation owns inventory generation because it can inspect the staged
snapshot data after all selected modules finish. The individual backup modules
continue to copy only their source artifacts.

## Failure and integrity behavior

- Inventory generation failure aborts package publication, like manifest-writing
  failure; no incomplete published snapshot is produced.
- Inventory files are included in Git-backed snapshots. SHA-256 integrity
  coverage remains limited to the backed-up data files listed in the manifest.
- They are not included in `manifest.json`'s `files` array because that array
  enumerates backed-up data with restore paths.
- A partial snapshot may contain an inventory for any relevant module that
  succeeded.

## Documentation

The README will describe the two reference files and clarify that they are
new-machine setup checklists, not automated installation or restore scripts.

## Acceptance criteria

1. A snapshot with backed-up fonts has a deterministic `fonts_list.txt`.
2. A snapshot with `data/.zsh` has a deterministic `zsh_plugins.txt`.
3. Neither reference file appears in `manifest.json`'s file list.
4. The existing manifest file entries continue to describe only `data/` files.
5. Missing or failed component backups do not generate their reference file.
6. Tests cover file contents, absence behavior, and manifest exclusion.
