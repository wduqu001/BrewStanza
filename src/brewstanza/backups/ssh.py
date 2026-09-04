import shutil
from pathlib import Path

from rich.console import Console

from brewstanza.backups.safety import ensure_safe

console = Console()

def backup(backup_dir: Path) -> bool:
    ssh_dir = Path.home() / ".ssh"
    config_file = ssh_dir / "config"
    
    if not config_file.exists():
        console.print(f"[yellow]Skipped:[/yellow] {config_file} does not exist.")
        return False

    try:
        ensure_safe(backup_dir, config_file)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return False

    dest_ssh_dir = backup_dir / ".ssh"
    dest_ssh_dir.mkdir(parents=True, exist_ok=True)
    
    dest_config_file = dest_ssh_dir / "config"
    try:
        shutil.copy2(config_file, dest_config_file)
        console.print(f"[green]Success:[/green] Backed up {config_file} to {dest_config_file}")
        return True
    except Exception as e:
        console.print(f"[red]Error backing up {config_file}:[/red] {e}")
        return False
