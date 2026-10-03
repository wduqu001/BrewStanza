import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from brewstanza.backups import apps, claude, fonts, git, homebrew, ssh, zsh
from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_dest_not_home, ensure_safe

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

def _source_paths_for(name: str) -> tuple[Path, ...]:
    home = Path.home()
    sources = {
        "Claude": (home / ".claude",),
        "Zsh": (home / ".zsh", home / ".zshrc"),
        "Fonts": (home / "Library" / "Fonts",),
        "Git": (home / ".gitconfig",),
        "SSH": (home / ".ssh" / "config",),
        "Apps": (Path("/Applications"), home / "Applications"),
    }
    return sources.get(name, ())


def _validate_dest_for_choices(dest: Path, choices: list[str]) -> None:
    for name in choices:
        if name in {"Apps", "Fonts"} and sys.platform != "darwin":
            continue
        ensure_safe(dest, *_source_paths_for(name))


@click.group()
@click.version_option()
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
    try:
        ensure_dest_not_home(dest)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

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
            lower_keys = [k.lower() for k in keys]
            for idx in selection.split(","):
                idx = idx.strip()
                if idx.isdigit() and 1 <= int(idx) <= len(keys):
                    choice = keys[int(idx) - 1]
                    if choice not in choices:
                        choices.append(choice)
                elif idx.lower() in lower_keys:
                    choice = keys[lower_keys.index(idx.lower())]
                    if choice not in choices:
                        choices.append(choice)
                    
            if not choices:
                console.print("[red]Invalid selection. Exiting.[/red]")
                return

    try:
        _validate_dest_for_choices(dest, choices)
        dest.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as e:
        raise click.ClickException(f"Invalid backup destination {dest}: {e}") from e

    console.print(Panel.fit(f"[bold blue]BrewStanza Backup Orchestrator[/bold blue]\nTarget: {dest}", border_style="blue"))  # noqa: E501
    console.print(f"\n[bold]Starting backups for: {', '.join(choices)}[/bold]\n")
    
    results: list[BackupResult] = []
    for name in choices:
        console.print(f"[bold cyan]--- Backing up {name} ---[/bold cyan]")
        result = MODULES[name](dest)
        results.append(result)
        console.print("")

    successes = sum(result.status == "success" for result in results)
    skipped = sum(result.status == "skipped" for result in results)
    failed = sum(result.status == "failed" for result in results)
    console.print(
        f"[bold green]Backup complete! {successes} succeeded, "
        f"{skipped} skipped, {failed} failed.[/bold green]"
    )
    if failed:
        raise click.ClickException("One or more backup components failed.")

if __name__ == "__main__":
    main()
