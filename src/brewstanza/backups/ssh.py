from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe
from brewstanza.backups.transaction import replace_file

console = Console()

def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
    ssh_dir = Path.home() / ".ssh"
    config_file = ssh_dir / "config"
    
    if not config_file.exists():
        console.print(f"[yellow]Skipped:[/yellow] {config_file} does not exist.")
        return BackupResult.skipped("SSH", f"{config_file} does not exist.")

    try:
        ensure_safe(backup_dir, config_file)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return BackupResult.failed("SSH", str(e))

    dest_config_file = backup_dir / ".ssh" / "config"
    if dry_run:
        console.print(f"[cyan]Would back up:[/cyan] {config_file} to {dest_config_file}")
        return BackupResult.success("SSH", f"Would back up {config_file}.", 1)

    try:
        dest_ssh_dir = backup_dir / ".ssh"
        dest_ssh_dir.mkdir(parents=True, exist_ok=True)
        replace_file(config_file, dest_config_file)
        console.print(f"[green]Success:[/green] Backed up {config_file} to {dest_config_file}")
        return BackupResult.success("SSH", f"Backed up {config_file} to {dest_config_file}.", 1)
    except OSError as e:
        console.print(f"[red]Error backing up {config_file}:[/red] {e}")
        return BackupResult.failed("SSH", str(e))
