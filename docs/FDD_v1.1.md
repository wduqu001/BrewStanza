# BrewStanza — Feature Design Document
**Version:** 1.1 (March 2026)
**Stack:** Python 3.11+, asyncio, Click, Rich, TOML
**Target OS:** macOS Tahoe — Apple Silicon M1/M2/M3/M4

---

## 1. Scope Changes from v1.0

The following changes were made to keep the product focused on its core value proposition: **reproducible Mac migration for developers**.

| Feature | Decision | Rationale |
| :--- | :--- | :--- |
| `~/Library` leftover scanning | **Removed** | Sandboxing/permission friction on modern macOS; duplicates AppCleaner and CleanMyMac; not required for migration story |
| Markdown export | **Removed** | Redundant — Rich terminal output is already human-readable; keep JSON (scriptable) and Brewfile (migration) |
| `apps info <app>` command | **Removed** | Primary value (leftover paths) is gone; useful fields folded into `apps list` table output |
| Auto-categorise via `Info.plist` | **Deferred to v2.0** | Cosmetic grouping that adds `plistlib` complexity with no migration benefit |
| Async concurrent disk scanner | **Added** | Replaces sequential `du` calls; fans out subprocesses under `asyncio.Semaphore`; live Rich progress bar |

---

## 2. System Architecture

BrewStanza follows a modular architecture with clear separation of concerns. The CLI layer routes commands to domain modules; each module is independently testable with no cross-dependencies.

```
brewstanza/
├── cli.py               ← Click entry point, command routing
├── scanner/
│   ├── homebrew.py      ← HomebrewScanner
│   ├── apps.py          ← AppScanner
│   └── disk.py          ← DiskScanner  (async)
├── analyzer/
│   └── storage.py       ← StorageAnalyzer
├── exporter/
│   └── export.py        ← ExportManager
└── ui/
    └── renderer.py      ← UI Renderer (Rich)
```

### 2.1 Module Responsibilities

| Module | Responsibility |
| :--- | :--- |
| **HomebrewScanner** | Interfaces with Homebrew CLI (`brew list`, `brew info --json`) to extract package names and cellar paths |
| **AppScanner** | Enumerates `.app` bundles in `/Applications` and `~/Applications`; returns paths for downstream scanning |
| **DiskScanner** | Async concurrent `du -sk` runner — fans out N subprocesses under `asyncio.Semaphore(8)`; returns `ScanSummary` |
| **StorageAnalyzer** | Consumes `ScanSummary`; aggregates totals, computes percentage share, ranks top-N consumers |
| **ExportManager** | Serialises state to JSON or Brewfile; handles GitHub PAT auth and timestamped `git commit` via subprocess |
| **UI Renderer** | Formats all output using Rich — tables, progress bars, panels; no business logic |

---

## 3. Functional Specifications

### 3.1 Homebrew Management

- **Inventory:** Lists all installed formulae and casks via `brew list --formula` and `brew list --cask`
- **Metadata:** Displays package description and version via `brew info --json`
- **Disk usage:** Resolved from Homebrew cellar paths passed to `DiskScanner`
- **Actionable output:** Detects outdated packages via `brew outdated`; generates ready-to-run `brew upgrade` and `brew uninstall` strings

### 3.2 Application Scanning

- **Discovery:** Scans `/Applications` and `~/Applications` for `.app` bundles
- **Output:** `apps list` table shows name, primary path, and on-disk size (calculated on demand by `DiskScanner`)
- **Removed:** Per-app detail command (`apps info`) and `~/Library` leftover scanning are out of scope

### 3.3 Storage Analytics

- **Aggregates:** Total disk usage for Homebrew packages and standalone applications, shown side by side
- **Top consumers:** Lists the top 10 largest packages/applications by size
- **Distribution:** Percentage share per item as an inline bar (Rich markup)

### 3.4 Export

Two formats are supported:

| Format | Use case |
| :--- | :--- |
| **JSON** | Structured machine-readable snapshot of the full inventory |
| **Brewfile** | Standard `brew bundle` format for one-command environment restore |

### 3.5 GitHub Sync

Users maintain a version-controlled record of their developer environment:

- Exports current inventory to the configured output format
- Commits to a designated GitHub repository using a Personal Access Token (PAT) stored in `~/.config/brewstanza/config.toml`
- Commit messages include an automatic timestamp (`BrewStanza sync — 2026-03-14T10:32:00`)
- Supports private repositories

---

## 4. Async Concurrent Disk Scanner

This is the most technically significant module. Sequential `du -sk` calls on a machine with 50+ packages can take 10–30 seconds. The async scanner reduces this to the latency of the single slowest path.

### 4.1 Design

```
collect paths
     │
     ▼
asyncio.gather(*[_du(path, semaphore) for path in paths])
     │                    │
     │          asyncio.Semaphore(8)
     │          caps concurrent du subprocesses
     │
     ▼
ScanSummary(results, failed_paths)
```

### 4.2 Key Design Decisions

| Decision | Rationale |
| :--- | :--- |
| `asyncio` over `ThreadPoolExecutor` | `du` is I/O-bound; async subprocesses avoid thread overhead and integrate cleanly with Click's sync surface via `asyncio.run()` |
| Semaphore cap of 8 | Matches APFS I/O thread sweet spot; above ~16 yields diminishing returns and risks `EMFILE` errors |
| `du -sk` (kilobytes) | `-s` summarises the full tree; `-k` gives consistent 1 KB blocks across macOS versions; multiply by 1024 for bytes |
| Per-call timeout of 30s | Prevents a hung `du` (e.g. network mount) from blocking the entire scan |
| Errors captured in result | `_du()` never raises; errors go into `ScanResult.error` so one bad path doesn't abort the batch |
| `transient=True` on progress bar | Rich erases the bar when done; the final summary table replaces it cleanly |

### 4.3 Public API

```python
# Sync wrapper — safe to call directly from Click commands
summary: ScanSummary = scan_paths(paths, label="Scanning apps")

# Async — use when already inside an event loop
summary: ScanSummary = await scan_paths_async(paths, label="Scanning apps")
```

### 4.4 Data Model

```python
@dataclass
class ScanResult:
    path:       Path
    size_bytes: int   = 0
    error:      str   = ""   # non-empty = this path failed

@dataclass
class ScanSummary:
    results:      list[ScanResult]  # successful scans
    failed_paths: list[Path]        # paths that errored or timed out

    def top(self, n: int = 10) -> list[ScanResult]: ...
    def total_bytes(self) -> int: ...
    def total_human(self) -> str: ...
```

### 4.5 Testing Strategy

Because `_du()` wraps a subprocess, it can be tested without touching the filesystem:

```python
# Mock asyncio.create_subprocess_exec to return controlled stdout
async def test_du_returns_correct_bytes(mocker):
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"1024\t/some/path\n", b"")
    mock_proc.returncode = 0
    mocker.patch("asyncio.create_subprocess_exec", return_value=mock_proc)

    result = await _du(Path("/some/path"), asyncio.Semaphore(1))

    assert result.size_bytes == 1024 * 1024
    assert result.error == ""
```

---

## 5. Command Reference

| Command | Description |
| :--- | :--- |
| `brewstanza brew list` | Lists all Homebrew packages with versions and disk sizes |
| `brewstanza brew info <pkg>` | Shows detailed metadata for a single package |
| `brewstanza apps list` | Lists all installed `.app` bundles with path and size |
| `brewstanza storage` | Displays aggregated storage breakdown and top 10 consumers |
| `brewstanza export [json\|brewfile]` | Exports current inventory to the specified format |
| `brewstanza sync` | Commits the latest export to the configured GitHub repository |

---

## 6. Configuration

Stored at `~/.config/brewstanza/config.toml`:

```toml
[github]
token      = "ghp_..."       # Personal Access Token (PAT)
repository = "user/dotfiles" # Target repo (can be private)
branch     = "main"

[scanner]
concurrency = 8              # Max concurrent du subprocesses
timeout     = 30             # Seconds before a single path is abandoned
```

---

## 7. Error Handling Policy

| Scenario | Behaviour |
| :--- | :--- |
| `brew` not installed | Exit with clear message and install instructions |
| No `.app` bundles found | Warn and continue; don't abort the full command |
| `du` timeout on a path | Record in `ScanSummary.failed_paths`; display warning in footer of output table |
| GitHub auth failure | Surface the PAT error directly; link to GitHub token settings |
| Missing config file | First-run wizard prompts for GitHub token and writes `config.toml` |
