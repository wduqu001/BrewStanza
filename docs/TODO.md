# BrewStanza — Development Checklist

> Work top-to-bottom. Each section unblocks the next.

---

## Week 1 — Foundation

### Project scaffold
- [x] `pyproject.toml` with `[project]`, `[project.scripts]`, `[tool.pytest.ini_options]`
- [x] `src/brewstanza/` package layout (not flat — required for Homebrew formula)
- [x] Test files collocated with source files inside `src/brewstanza/`
- [x] `ruff` configured in `pyproject.toml` (line length 100, select E/W/F/I)
- [x] `mypy` configured in `pyproject.toml` (strict mode)
- [x] `.github/workflows/ci.yml` — runs `pytest`, `ruff check`, `mypy` on push + PR
- [x] CI badge added to README
- [x] `~/.config/brewstanza/config.toml` schema defined and documented

### HomebrewScanner (`scanner/homebrew.py`)
- [x] `list_formulae() -> list[str]` — `brew list --formula`
- [x] `list_casks() -> list[str]` — `brew list --cask`
- [x] `get_info(name: str) -> dict` — `brew info --json=v2`
- [x] `get_outdated() -> list[str]` — `brew outdated --quiet`
- [x] `get_cellar_path(name: str) -> Path | None` — from info JSON
- [x] Unit tests with mocked subprocess (no real `brew` dependency in CI)

### AppScanner (`scanner/apps.py`)
- [x] `collect_app_paths() -> list[Path]` — glob `/Applications` and `~/Applications`
- [x] Handles missing directories gracefully (no crash if `~/Applications` doesn't exist)
- [x] Unit tests with a temporary fake directory tree

### DiskScanner (`scanner/disk.py`)
- [x] `ScanResult` dataclass — `path`, `size_bytes`, `error`, `size_human` property
- [x] `ScanSummary` dataclass — `results`, `failed_paths`, `total_bytes`, `total_human`, `top(n)`
- [x] `_du(path, semaphore) -> ScanResult` — async, never raises, captures timeout
- [x] `scan_paths_async(paths, label, concurrency, console) -> ScanSummary`
- [x] `scan_paths(paths, ...) -> ScanSummary` — sync wrapper via `asyncio.run()`
- [x] Rich progress bar with `transient=True`
- [x] Semaphore default of 8, configurable via `config.toml`
- [x] Per-path timeout of 30s, configurable via `config.toml`
- [x] Unit tests: mock `asyncio.create_subprocess_exec` for happy path, error path, timeout path

---

## Week 2 — Core features

### StorageAnalyzer (`analyzer/storage.py`)
- [x] `aggregate(summary: ScanSummary) -> StorageReport`
- [x] `StorageReport` — homebrew total, apps total, combined total, top-N list, per-item percentage
- [x] Unit tests with fixed `ScanSummary` fixtures

### CLI commands (`cli.py`)
- [ ] `brewstanza brew list` — table: name | version | size | outdated flag
- [ ] `brewstanza brew info <pkg>` — panel: description, version, size, cellar path, uninstall command
- [ ] `brewstanza apps list` — table: name | path | size
- [ ] `brewstanza storage` — two-section table (Homebrew / Apps) + top-10 consumer list with inline bars
- [ ] `--json` flag on all list/storage commands for scriptable output
- [ ] `--no-color` flag respected globally

### UI Renderer (`ui/renderer.py`)
- [ ] `render_brew_list(packages)` → Rich Table
- [ ] `render_apps_list(apps)` → Rich Table
- [ ] `render_storage_report(report)` → Rich layout with panels
- [ ] `render_summary_table(summary, top_n)` → Rich Table (reused from DiskScanner)
- [ ] Consistent column widths and colour scheme across all tables

### Integration
- [ ] Run full scan against real machine; verify output is correct and fast (< 5s)
- [ ] Verify `--json` output is valid JSON and parseable by `jq`

---

## Week 3 — Export, sync, polish

### ExportManager (`exporter/export.py`)
- [ ] `to_json(report) -> str` — full inventory snapshot with timestamp
- [ ] `to_brewfile(packages) -> str` — standard `brew bundle` format
- [ ] `write_file(content, path: Path)` — with overwrite confirmation prompt
- [ ] Unit tests for both format serialisers

### GitHub sync
- [ ] Read PAT and repo from `~/.config/brewstanza/config.toml`
- [ ] `sync(content, format)` — export → write temp file → `git add` → `git commit` → `git push`
- [ ] Commit message format: `BrewStanza sync — <ISO 8601 timestamp>`
- [ ] Graceful error if PAT is missing or expired (link to GitHub token settings)

### CLI commands
- [ ] `brewstanza export json` — write `brewstanza-snapshot.json`
- [ ] `brewstanza export brewfile` — write `Brewfile`
- [ ] `brewstanza sync` — export + commit in one step

### First-run experience
- [ ] Detect missing `config.toml` on any command that needs it
- [ ] Wizard: prompt for GitHub PAT, repo name, branch; write config file
- [ ] `brewstanza sync --dry-run` shows what would be committed without pushing

### Distribution
- [ ] `pyproject.toml` entry point: `brewstanza = "brewstanza.cli:main"`
- [ ] `pip install brewstanza` works from a clean venv
- [ ] Homebrew tap formula (`Formula/brewstanza.rb`) — installs from PyPI
- [ ] `brew install <user>/tap/brewstanza` works end-to-end

---

## Quality gates (must pass before calling it done)

- [ ] `pytest --cov=brewstanza --cov-fail-under=80` passes
- [ ] `ruff check src/ tests/` — zero warnings
- [ ] `mypy src/` — zero errors
- [ ] CI badge is green on `main`
- [ ] `brewstanza --help` and all sub-command `--help` are accurate and complete

---

## README / portfolio checklist

- [ ] One-line description that leads with the migration workflow story
- [ ] Install instructions (`brew install` and `pip install` variants)
- [ ] Animated demo GIF showing a full scan → storage → export → sync run
- [ ] `--demo` flag (or fixture data mode) so reviewers can run it without Homebrew installed
- [ ] Architecture section with module diagram
- [ ] Link to PRD and FDD in `docs/`
- [ ] `CONTRIBUTING.md` with setup instructions and test commands
- [ ] License file (MIT)
