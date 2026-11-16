# Migration Inventory Files Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish clear font and Zsh-directory reference inventories with every applicable BrewStanza snapshot, outside its manifest.

**Architecture:** Collection belongs in `package.py`, where the complete staged `data/` tree is available. Two helpers derive deterministic text content; `create_snapshot` writes the optional files before generating the data-only manifest. Backup-module interfaces stay unchanged.

**Tech Stack:** Python 3.11+, `pathlib`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-11-16-migration-inventories-design.md`

## Global Constraints

- `fonts_list.txt` and `zsh_plugins.txt` are snapshot-root, human-readable reference files.
- Manifest `files` entries enumerate only files below `data/`; reference inventories never appear there.
- Font entries are sorted relative paths below `data/Fonts`, one per line.
- Zsh entries are sorted top-level directory names below `data/.zsh`, one per line.
- Inventories must state they are setup checklists, not installation or restore scripts.
- Do not infer font installation sources or classify Zsh directories as plugins.
- Missing component data produces no corresponding inventory.

## Review Focus

- An empty `data/Fonts` directory creates a header-only inventory because the Fonts module succeeded.
- Nested font directories preserve their relative paths to avoid filename ambiguity.
- Files directly below `data/.zsh` are excluded; only directories qualify.
- A failed or unavailable module produces no inventory.
- Reference files do not change existing Git or checksum/manifest integrity behavior.

---

### Task 1: Generate data-derived inventory content

**Files:**
- Modify: `src/brewstanza/backups/package.py:104-115`
- Test: `tests/test_package.py`

**Interfaces:**
- Produces: `_font_inventory(data_dir: Path) -> str | None`
- Produces: `_zsh_plugin_inventory(data_dir: Path) -> str | None`

- [ ] **Step 1: Write failing helper tests**

Add `test_font_inventory_lists_sorted_relative_font_paths`, creating `Fonts/Zed.otf` and `Fonts/family/Alpha.ttf`, and assert the returned inventory contains `family/Alpha.ttf\nZed.otf\n`. Add `test_zsh_plugin_inventory_lists_only_sorted_top_level_directories`, creating `.zsh/custom`, `.zsh/zinit`, and `.zsh/aliases.zsh`; assert it contains `custom\nzinit\n` but not `aliases.zsh`.

- [ ] **Step 2: Run the focused tests to verify failure**

Run: `python -m pytest tests/test_package.py -k inventory -v`

Expected: FAIL because both helpers are undefined.

- [ ] **Step 3: Implement the two helpers in `src/brewstanza/backups/package.py`**

Return `None` if the relevant data directory is absent. Otherwise render a fixed comment header, sorted newline-separated entries, and a trailing newline. Recursively list files relative to `Fonts`; list direct child directories only for `.zsh`.

- [ ] **Step 4: Run focused helper tests**

Run: `python -m pytest tests/test_package.py -k inventory -v`

Expected: PASS.

- [ ] **Step 5: Commit the helpers and tests**

Run: `git add src/brewstanza/backups/package.py tests/test_package.py && git commit -m "feat: generate migration inventory content"`

### Task 2: Publish inventories without changing manifest entries

**Files:**
- Modify: `src/brewstanza/backups/package.py:141-164`
- Test: `tests/test_package.py`

**Interfaces:**
- Consumes: `_font_inventory(data_dir: Path) -> str | None`; `_zsh_plugin_inventory(data_dir: Path) -> str | None`
- Produces: `fonts_list.txt` and `zsh_plugins.txt` through `create_snapshot(...) -> Path`

- [ ] **Step 1: Write failing snapshot tests**

Create staged `Fonts/Inter.ttf` and `.zsh/zinit`, call `create_snapshot`, then assert the two inventory files exist at snapshot root and no manifest `files` entry ends in `_list.txt` or `zsh_plugins.txt`. Add an absence test for staged data without `Fonts` or `.zsh`.

- [ ] **Step 2: Run focused snapshot tests to verify failure**

Run: `python -m pytest tests/test_package.py -k "snapshot and inventor" -v`

Expected: FAIL because publication does not write inventory files.

- [ ] **Step 3: Write optional inventory strings during `create_snapshot`**

After copying staged data, call both Task 1 helpers with `package_temp / "data"`. Write returned content as UTF-8 to root-level `fonts_list.txt` and `zsh_plugins.txt` before `manifest.json`. Leave `_file_entries(package_temp / "data", ...)` unchanged.

- [ ] **Step 4: Run package tests**

Run: `python -m pytest tests/test_package.py -v`

Expected: PASS.

- [ ] **Step 5: Commit snapshot publication**

Run: `git add src/brewstanza/backups/package.py tests/test_package.py && git commit -m "feat: add snapshot migration inventories"`

### Task 3: Document new-machine reference files

**Files:**
- Modify: `README.md:94-110`
- Test: `tests/test_integration.py`

**Interfaces:**
- Consumes: root-level inventory files from Task 2.
- Produces: README guidance and end-to-end assertions.

- [ ] **Step 1: Add failing integration assertions**

In the complete macOS-style backup test, assert `fonts_list.txt` contains `Arial.ttf`. Add a top-level fake `.zsh` directory and assert `zsh_plugins.txt` names it; retain `custom.zsh` as a file and assert it is excluded.

- [ ] **Step 2: Run integration test to verify failure**

Run: `python -m pytest tests/test_integration.py -v`

Expected: FAIL because the inventory behavior is not asserted by the existing fixture.

- [ ] **Step 3: Update the README Backup policy**

Add a “New-machine checklist” paragraph: snapshots may contain `fonts_list.txt` and `zsh_plugins.txt`, respectively listing backed-up fonts and top-level `.zsh` directories. Say they guide manual installation/configuration and do not restore or install anything.

- [ ] **Step 4: Run complete verification**

Run: `python -m pytest`

Run: `python -m ruff check src/ tests/`

Run: `python -m mypy src/`

Expected: all commands exit 0.

- [ ] **Step 5: Commit documentation and end-to-end coverage**

Run: `git add README.md tests/test_integration.py && git commit -m "docs: explain migration inventory files"`

## Self-review

- **Spec coverage:** Tasks 1–2 provide deterministic optional inventories, correct scope and location, and manifest exclusion. Task 3 explains their new-machine purpose.
- **Step scan:** Every step is a concrete test, command, implementation, or commit.
- **Type consistency:** Both helper signatures match across Tasks 1 and 2.
- **Review focus:** Helper tests cover empty/missing data, nesting, sorting, and direct-file exclusion. Task 2 covers absence and manifest boundaries; existing package integrity tests run in full with Task 2.
- **Proportion:** The plan defines interfaces, values, and checks without transcribing the implementation.
