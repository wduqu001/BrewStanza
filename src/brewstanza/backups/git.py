import shutil
from pathlib import Path

from rich.console import Console

console = Console()

def backup(backup_dir: Path) -> bool:
    gitconfig_file = Path.home() / ".gitconfig"
    
    if not gitconfig_file.exists():
        console.print(f"[yellow]Skipped:[/yellow] {gitconfig_file} does not exist.")
        return False
        
    dest_gitconfig_file = backup_dir / ".gitconfig"
    try:
        shutil.copy2(gitconfig_file, dest_gitconfig_file)
        console.print(f"[green]Success:[/green] Backed up {gitconfig_file} to {dest_gitconfig_file}")  # noqa: E501
        return True
    except Exception as e:
        console.print(f"[red]Error backing up {gitconfig_file}:[/red] {e}")
        return False
