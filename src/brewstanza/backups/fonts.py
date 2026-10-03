import sys
from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe
from brewstanza.backups.transaction import replace_directory

console = Console()

def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
    if sys.platform != "darwin":
        console.print("[yellow]Skipped:[/yellow] Fonts backup is only supported on macOS.")
        return BackupResult.skipped("Fonts", "Font backup is only supported on macOS.")

    source_dir = Path.home() / "Library" / "Fonts"
    if not source_dir.exists():
        console.print(f"[yellow]Skipped:[/yellow] {source_dir} does not exist.")
        return BackupResult.skipped("Fonts", f"{source_dir} does not exist.")

    try:
        ensure_safe(backup_dir, source_dir)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return BackupResult.failed("Fonts", str(e))

    dest_dir = backup_dir / "Fonts"
    if dry_run:
        console.print(f"[cyan]Would back up:[/cyan] {source_dir} to {dest_dir}")
        return BackupResult.success("Fonts", f"Would back up {source_dir}.", 1)

    try:
        replace_directory(source_dir, dest_dir)
        console.print(f"[green]Success:[/green] Backed up {source_dir} to {dest_dir}")
        return BackupResult.success(
            "Fonts", f"Backed up {source_dir} to {dest_dir}.", 1
        )
    except OSError as e:
        console.print(f"[red]Error backing up Fonts:[/red] {e}")
        return BackupResult.failed("Fonts", str(e))
