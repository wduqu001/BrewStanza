import shutil
import sys
from pathlib import Path
from rich.console import Console

console = Console()

def backup(backup_dir: Path) -> bool:
    if sys.platform != "darwin":
        console.print("[yellow]Skipped:[/yellow] Fonts backup is only supported on macOS.")
        return False
        
    source_dir = Path.home() / "Library" / "Fonts"
    if not source_dir.exists():
        console.print(f"[yellow]Skipped:[/yellow] {source_dir} does not exist.")
        return False
        
    dest_dir = backup_dir / "Fonts"
    try:
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        console.print(f"[green]Success:[/green] Backed up {source_dir} to {dest_dir}")
        return True
    except Exception as e:
        console.print(f"[red]Error backing up Fonts:[/red] {e}")
        return False
