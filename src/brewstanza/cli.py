import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from brewstanza.backups import claude, zsh, homebrew, fonts, git, ssh, apps

console = Console()
DEFAULT_BACKUP_DIR = Path.home() / "BrewStanza-Backup"

MODULES = {
    "Claude": claude.backup,
    "Zsh": zsh.backup,
    "Homebrew": homebrew.backup,
    "Fonts": fonts.backup,
    "Git": git.backup,
    "SSH": ssh.backup,
    "Apps": apps.backup,
}

@click.group()
def main() -> None:
    """BrewStanza: Dotfile and App Backup Orchestrator."""
    pass

@main.command()
@click.option(
    "--dest", 
    type=click.Path(path_type=Path), 
    default=DEFAULT_BACKUP_DIR,
    help="Destination directory for backups."
)
@click.option(
    "--all", "backup_all",
    is_flag=True,
    help="Run all backup modules without prompting."
)
def backup(dest: Path, backup_all: bool) -> None:
    """Run the backup orchestration menu."""
    dest.mkdir(parents=True, exist_ok=True)
    console.print(Panel.fit(f"[bold blue]BrewStanza Backup Orchestrator[/bold blue]\nTarget: {dest}", border_style="blue"))
    
    if backup_all:
        choices = list(MODULES.keys())
    else:
        # Simple CLI menu
        console.print("Select which components to backup:")
        console.print("  [bold]all[/bold] - Run all backups")
        for i, name in enumerate(MODULES.keys(), 1):
            console.print(f"  [bold]{i}[/bold] - {name}")
            
        selection = click.prompt("Enter your choice (comma separated or 'all')", default="all")
        
        if selection.lower() == "all":
            choices = list(MODULES.keys())
        else:
            choices = []
            keys = list(MODULES.keys())
            for idx in selection.split(","):
                idx = idx.strip()
                if idx.isdigit() and 1 <= int(idx) <= len(keys):
                    choices.append(keys[int(idx) - 1])
                elif idx in keys:
                    choices.append(idx)
                    
            if not choices:
                console.print("[red]Invalid selection. Exiting.[/red]")
                return

    console.print(f"\n[bold]Starting backups for: {', '.join(choices)}[/bold]\n")
    
    success_count = 0
    for name in choices:
        console.print(f"[bold cyan]--- Backing up {name} ---[/bold cyan]")
        result = MODULES[name](dest)
        if result:
            success_count += 1
        console.print("")
        
    console.print(f"[bold green]Backup complete! {success_count}/{len(choices)} components processed successfully.[/bold green]")

if __name__ == "__main__":
    main()
