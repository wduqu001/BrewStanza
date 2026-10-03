from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe
from brewstanza.backups.transaction import replace_directory, replace_file

console = Console()

def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
    zsh_dir = Path.home() / ".zsh"
    zshrc_file = Path.home() / ".zshrc"

    try:
        ensure_safe(backup_dir, zsh_dir, zshrc_file)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return BackupResult.failed("Zsh", str(e))

    artifacts_copied = 0
    failed = False

    if dry_run:
        planned = 0
        if zsh_dir.exists():
            console.print(f"[cyan]Would back up:[/cyan] {zsh_dir} to {backup_dir / '.zsh'}")
            planned += 1
        else:
            console.print(f"[yellow]Skipped:[/yellow] {zsh_dir} does not exist.")
        if zshrc_file.exists():
            console.print(f"[cyan]Would back up:[/cyan] {zshrc_file} to {backup_dir / '.zshrc'}")
            planned += 1
        else:
            console.print(f"[yellow]Skipped:[/yellow] {zshrc_file} does not exist.")
        if planned:
            return BackupResult.success(
                "Zsh", "Would back up available Zsh configuration.", planned
            )
        return BackupResult.skipped("Zsh", "No Zsh configuration files found.")
    
    if zsh_dir.exists():
        dest_zsh_dir = backup_dir / ".zsh"
        try:
            replace_directory(zsh_dir, dest_zsh_dir)
            console.print(f"[green]Success:[/green] Backed up {zsh_dir} to {dest_zsh_dir}")
            artifacts_copied += 1
        except OSError as e:
            console.print(f"[red]Error backing up {zsh_dir}:[/red] {e}")
            failed = True
    else:
        console.print(f"[yellow]Skipped:[/yellow] {zsh_dir} does not exist.")

    if zshrc_file.exists():
        dest_zshrc_file = backup_dir / ".zshrc"
        try:
            replace_file(zshrc_file, dest_zshrc_file)
            console.print(f"[green]Success:[/green] Backed up {zshrc_file} to {dest_zshrc_file}")
            artifacts_copied += 1
        except OSError as e:
            console.print(f"[red]Error backing up {zshrc_file}:[/red] {e}")
            failed = True
    else:
        console.print(f"[yellow]Skipped:[/yellow] {zshrc_file} does not exist.")
        
    if failed:
        return BackupResult.failed(
            "Zsh", "One or more Zsh backup artifacts failed.", artifacts_copied
        )
    if artifacts_copied:
        return BackupResult.success(
            "Zsh", "Backed up available Zsh configuration.", artifacts_copied
        )
    return BackupResult.skipped("Zsh", "No Zsh configuration files found.")
