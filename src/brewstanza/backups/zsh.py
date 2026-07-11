import shutil
from pathlib import Path

from rich.console import Console

console = Console()

def backup(backup_dir: Path) -> bool:
    zsh_dir = Path.home() / ".zsh"
    zshrc_file = Path.home() / ".zshrc"
    
    success = False
    
    if zsh_dir.exists():
        dest_zsh_dir = backup_dir / ".zsh"
        try:
            if dest_zsh_dir.exists():
                shutil.rmtree(dest_zsh_dir)
            shutil.copytree(zsh_dir, dest_zsh_dir, dirs_exist_ok=True)
            console.print(f"[green]Success:[/green] Backed up {zsh_dir} to {dest_zsh_dir}")
            success = True
        except Exception as e:
            console.print(f"[red]Error backing up {zsh_dir}:[/red] {e}")
    else:
        console.print(f"[yellow]Skipped:[/yellow] {zsh_dir} does not exist.")

    if zshrc_file.exists():
        dest_zshrc_file = backup_dir / ".zshrc"
        try:
            shutil.copy2(zshrc_file, dest_zshrc_file)
            console.print(f"[green]Success:[/green] Backed up {zshrc_file} to {dest_zshrc_file}")
            success = True
        except Exception as e:
            console.print(f"[red]Error backing up {zshrc_file}:[/red] {e}")
    else:
        console.print(f"[yellow]Skipped:[/yellow] {zshrc_file} does not exist.")
        
    return success
