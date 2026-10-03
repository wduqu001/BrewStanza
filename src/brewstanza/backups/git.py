from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe
from brewstanza.backups.transaction import replace_file

console = Console()

def backup(backup_dir: Path) -> BackupResult:
    gitconfig_file = Path.home() / ".gitconfig"
    
    if not gitconfig_file.exists():
        console.print(f"[yellow]Skipped:[/yellow] {gitconfig_file} does not exist.")
        return BackupResult.skipped("Git", f"{gitconfig_file} does not exist.")

    try:
        ensure_safe(backup_dir, gitconfig_file)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return BackupResult.failed("Git", str(e))

    dest_gitconfig_file = backup_dir / ".gitconfig"
    try:
        replace_file(gitconfig_file, dest_gitconfig_file)
        console.print(f"[green]Success:[/green] Backed up {gitconfig_file} to {dest_gitconfig_file}")  # noqa: E501
        return BackupResult.success(
            "Git", f"Backed up {gitconfig_file} to {dest_gitconfig_file}.", 1
        )
    except OSError as e:
        console.print(f"[red]Error backing up {gitconfig_file}:[/red] {e}")
        return BackupResult.failed("Git", str(e))
