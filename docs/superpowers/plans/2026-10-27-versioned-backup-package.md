# Implementation Plan: Versioned Backup Packages

**Status:** Implemented and verified (69 tests; Ruff; strict mypy).

## Files and responsibilities

- `src/brewstanza/backups/package.py`: initialize package roots; stage timestamped snapshots; create versioned manifests, checksums, and local Git commits.
- `src/brewstanza/cli.py`: add `init`; route backup module output into package staging; initialize new/empty destinations and adopt existing BrewStanza packages or Git repositories.
- `tests/test_package.py`: package validation, path mapping, checksum, Git, and failure behavior.
- `tests/test_cli.py`: init and backup command lifecycle, including preservation of existing backup invocation behavior.
- `tests/test_integration.py`: assert timestamped package layout and manifest against a complete fake-machine backup.
- `docs/TODO.md`: check off the package-format task after implementation and verification.

## Tasks

1. **Package initialization (RED → GREEN)**
   - Test absent and empty destinations, already initialized package acceptance, refusal of unrelated non-empty destinations, and adoption of an existing Git repository.
   - Test Git detection and initialization when available, and checksum mode when unavailable.
   - Implement initialization without touching unrelated destination contents or creating nested Git repositories.

2. **Versioned snapshot content (RED → GREEN)**
   - Test timestamped snapshot directories, manifest version/status/module records, home-relative restore targets, and `null` restore targets for reference artifacts.
   - Test SHA-256 entries in checksum mode and absence of checksums in Git mode.
   - Implement a per-run staging directory and publish a snapshot only after its manifest is written.

3. **Git commit and partial runs (RED → GREEN)**
   - Test one local commit per complete snapshot, no push, and no commit for a partial snapshot.
   - Test partial status and retention of successful module output when any selected module fails; skipped modules alone remain complete.
   - Implement Git operations scoped to the new snapshot so unrelated and uncommitted files are not staged.

4. **CLI lifecycle (RED → GREEN)**
   - Test `brewstanza init --dest`, automatic initialization for absent/empty backup destinations, adoption of existing Git repositories, and refusal of unrecognized non-empty non-Git destinations.
   - Update CLI orchestration to run existing modules against the staging layout and present the final timestamped destination.
   - Preserve dry-run behavior: no package initialization, snapshot, manifest, checksum, or Git mutation.

5. **Integration and documentation**
   - Update integration expectations for package contents and validate manifest paths against actual files.
   - Run targeted tests, then the full pytest suite, Ruff, and strict mypy checks.
   - Update README, PRD/FDD, and `docs/TODO.md` to describe the package format and current CLI; leave subsequent restore features unchecked.

## Acceptance criteria

- Every normal backup produces a timestamped, self-contained directory with a versioned JSON manifest.
- Restore paths are home-relative; non-restorable references have `restore_path: null`.
- Initialization selects the integrity mode: Git-backed destinations commit complete snapshots locally; destinations initialized without Git record SHA-256 checksums.
- No remote push occurs in either mode.
- Failed runs are retained and marked partial but are not committed; skipped modules alone do not make a run partial.
- Unrecognized non-empty non-Git destinations and dry runs are not modified; existing Git repositories are adopted with scoped commits.
