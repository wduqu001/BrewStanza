"""
brewstanza/scanner/disk.py

Async concurrent disk-usage scanner.

Strategy
--------
`du -sk <path>` is the right primitive — it measures actual on-disk
blocks (not apparent size), is universally available on macOS, and
handles nested directories correctly. The problem is latency: calling
it once per package/app in a tight loop is sequential and slow.

Fix: fan out N calls concurrently using asyncio + asyncio.Semaphore
to cap parallelism, then report results incrementally through a Rich
Progress bar so the user sees movement immediately.

Concurrency tuning
------------------
macOS HFS+/APFS I/O threads: 8 concurrent `du` calls hits the sweet
spot — enough to stay off the critical path of the slowest call
without thrashing the I/O scheduler. Raise CONCURRENCY cautiously;
above ~16 you'll start seeing diminishing returns and occasional
EMFILE errors on machines with many open files.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path

from rich import box
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from brewstanza.config import Config

_config = Config.load()
CONCURRENCY = _config.scanner.concurrency
DU_TIMEOUT = float(_config.scanner.timeout)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ScanResult:
    path: Path
    size_bytes: int = 0
    error: str = ""

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024**2)

    @property
    def size_human(self) -> str:
        b: float = float(self.size_bytes)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"


@dataclass
class ScanSummary:
    results: list[ScanResult] = field(default_factory=list)
    failed_paths: list[Path] = field(default_factory=list)

    @property
    def total_bytes(self) -> int:
        return sum(r.size_bytes for r in self.results)

    @property
    def total_human(self) -> str:
        return ScanResult(path=Path(), size_bytes=self.total_bytes).size_human

    def top(self, n: int = 10) -> list[ScanResult]:
        return sorted(self.results, key=lambda r: r.size_bytes, reverse=True)[:n]


# ---------------------------------------------------------------------------
# Core async primitives
# ---------------------------------------------------------------------------


async def _du(path: Path, semaphore: asyncio.Semaphore) -> ScanResult:
    """
    Run `du -sk <path>` under the semaphore.

    -s   summarise (single total for the whole tree)
    -k   output in 1 KB blocks (consistent across macOS versions)

    Returns a ScanResult. Never raises — errors are captured in the
    result so the caller can keep scanning the rest of the batch.
    """
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                "du",
                "-sk",
                str(path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,  # suppress "permission denied" noise
            )
            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=DU_TIMEOUT)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return ScanResult(path=path, error="timeout")

            if proc.returncode != 0:
                return ScanResult(path=path, error=f"du exited {proc.returncode}")

            raw = stdout.decode().strip()
            if not raw:
                return ScanResult(path=path, error="empty output")

            kb = int(raw.split()[0])
            return ScanResult(path=path, size_bytes=kb * 1024)

        except FileNotFoundError:
            return ScanResult(path=path, error="path not found")
        except Exception as exc:  # noqa: BLE001
            return ScanResult(path=path, error=str(exc))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def scan_paths_async(
    paths: list[Path],
    *,
    label: str = "Scanning",
    concurrency: int = CONCURRENCY,
    console: Console | None = None,
) -> ScanSummary:
    """
    Scan every path in `paths` concurrently, showing a Rich progress bar.

    Parameters
    ----------
    paths       : list of directories/bundles to measure
    label       : description shown on the progress bar
    concurrency : how many `du` calls to run simultaneously
    console     : Rich Console to render into (creates one if None)

    Returns a ScanSummary with all results once every path is done.

    Usage
    -----
    >>> import asyncio
    >>> from pathlib import Path
    >>> summary = asyncio.run(scan_paths_async(
    ...     paths=[Path("/Applications/Firefox.app"), Path("/Applications/VSCode.app")],
    ...     label="Scanning apps",
    ... ))
    >>> print(summary.total_human)
    """
    if console is None:
        console = Console()

    semaphore = asyncio.Semaphore(concurrency)
    summary = ScanSummary()

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=32),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,  # erase the bar when done; final table replaces it
    )

    with progress:
        task_id = progress.add_task(label, total=len(paths))

        async def _scan_one(path: Path) -> None:
            result = await _du(path, semaphore)
            if result.error:
                summary.failed_paths.append(path)
            else:
                summary.results.append(result)
            progress.advance(task_id)

        await asyncio.gather(*(_scan_one(p) for p in paths))

    return summary


def scan_paths(
    paths: list[Path],
    *,
    label: str = "Scanning",
    concurrency: int = CONCURRENCY,
    console: Console | None = None,
) -> ScanSummary:
    """
    Synchronous wrapper — safe to call from Click commands.

    Click commands are synchronous; this lets the scanner be called
    without any asyncio boilerplate at the call site.

    >>> summary = scan_paths(app_paths, label="Scanning apps")
    """
    return asyncio.run(
        scan_paths_async(
            paths,
            label=label,
            concurrency=concurrency,
            console=console,
        )
    )


# ---------------------------------------------------------------------------
# Convenience: collect common path lists
# ---------------------------------------------------------------------------


def collect_app_paths() -> list[Path]:
    """Return all .app bundles from /Applications and ~/Applications."""
    roots = [
        Path("/Applications"),
        Path.home() / "Applications",
    ]
    paths: list[Path] = []
    for root in roots:
        if root.is_dir():
            paths.extend(p for p in root.iterdir() if p.suffix == ".app")
    return paths


async def _brew_list_paths() -> list[Path]:
    """
    Ask Homebrew for the cellar paths of installed formulae and casks.

    Returns empty list if brew is not installed.
    """
    paths: list[Path] = []

    for flag in ("--formula", "--cask"):
        proc = await asyncio.create_subprocess_exec(
            "brew",
            "list",
            flag,
            "--full-name",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            continue

        names = stdout.decode().splitlines()

        # Ask brew where each package is installed
        if names:
            info_proc = await asyncio.create_subprocess_exec(
                "brew",
                "--prefix",
                *names,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            info_out, _ = await info_proc.communicate()
            if info_proc.returncode == 0:
                for line in info_out.decode().splitlines():
                    p = Path(line.strip())
                    if p.exists():
                        paths.append(p)

    return paths


def collect_brew_paths() -> list[Path]:
    """Return installed Homebrew cellar paths (formulae + casks)."""
    return asyncio.run(_brew_list_paths())


# ---------------------------------------------------------------------------
# Rich display helper
# ---------------------------------------------------------------------------


def render_summary_table(
    summary: ScanSummary,
    *,
    title: str = "Storage breakdown",
    top_n: int = 10,
    console: Console | None = None,
) -> None:
    """Print a Rich table of the top N consumers to the console."""
    if console is None:
        console = Console()

    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        show_footer=True,
        min_width=60,
    )
    table.add_column("Package / App", style="bold", footer="Total")
    table.add_column("Size", justify="right", footer=f"[bold]{summary.total_human}[/bold]")
    table.add_column("Share", justify="right", footer="")

    total = summary.total_bytes or 1  # guard division by zero

    for result in summary.top(top_n):
        share = result.size_bytes / total * 100
        bar = "█" * int(share / 5)  # 20 chars = 100 %
        table.add_row(
            result.path.stem,
            result.size_human,
            f"[dim]{bar:<20}[/dim] {share:5.1f}%",
        )

    console.print(table)

    if summary.failed_paths:
        console.print(
            f"[yellow]⚠  {len(summary.failed_paths)} path(s) could not be scanned "
            f"(permission denied or timeout)[/yellow]"
        )


# ---------------------------------------------------------------------------
# Quick smoke-test  (python disk_scanner.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    console = Console()
    targets = collect_app_paths()

    if not targets:
        console.print("[red]No .app bundles found.[/red]")
        sys.exit(1)

    console.print(f"[dim]Found {len(targets)} app bundles — scanning...[/dim]")
    summary = scan_paths(targets, label="Scanning /Applications", console=console)
    render_summary_table(summary, title="App storage breakdown", console=console)
