import shutil
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()

def backup(backup_dir: Path) -> bool:
    if shutil.which("brew") is None:
        console.print("[yellow]Skipped:[/yellow] 'brew' command not found in PATH.")
        return False
        
    brewfile_dest = backup_dir / "Brewfile"
    
    console.print(f"[cyan]Running:[/cyan] brew bundle dump to {brewfile_dest}...")
    try:
        # Run brew bundle dump. Using --force to overwrite if it exists.
        result = subprocess.run(
            ["brew", "bundle", "dump", f"--file={brewfile_dest}", "--force"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print(f"[green]Success:[/green] Backed up Homebrew inventory to {brewfile_dest}")  # noqa: E501
            return True
        else:
            console.print(f"[red]Error running brew bundle dump:[/red]\n{result.stderr}")
            return False
    except Exception as e:
        console.print(f"[red]Error backing up Homebrew:[/red] {e}")
        return False
