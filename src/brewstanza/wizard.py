"""
First-run configuration wizard for BrewStanza.

Invoked automatically when a command that needs GitHub config finds the
``~/.config/brewstanza/config.toml`` file missing or lacking a token.
Can also be triggered manually.
"""

import tomllib
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

_DEFAULT_CONFIG_PATH = Path.home() / ".config" / "brewstanza" / "config.toml"


def _write_config(token: str, repository: str, branch: str, path: Path) -> None:
    """Write a minimal config.toml to *path*, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "[github]\n"
        f'token      = "{token}"\n'
        f'repository = "{repository}"\n'
        f'branch     = "{branch}"\n'
        "\n"
        "[scanner]\n"
        "concurrency = 8\n"
        "timeout     = 30\n"
    )
    path.write_text(content, encoding="utf-8")


def needs_wizard(config_path: Path | None = None) -> bool:
    """
    Return True if the wizard should be offered to the user.

    The wizard is needed when either:
    - The config file does not exist, or
    - The ``[github]`` section has no ``token`` set.

    Args:
        config_path: Path to ``config.toml``.  Defaults to the standard
            ``~/.config/brewstanza/config.toml``.

    Returns:
        True if the wizard should run before the command proceeds.
    """
    path = config_path or _DEFAULT_CONFIG_PATH
    if not path.exists():
        return True
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        return not data.get("github", {}).get("token", "")
    except Exception:
        return True


def run_wizard(
    console: Console | None = None,
    config_path: Path | None = None,
) -> bool:
    """
    Interactively prompt the user for GitHub credentials and write config.toml.

    Args:
        console: Rich :class:`~rich.console.Console` to use for output.
            A default console is created if not provided.
        config_path: Destination path for the config file.  Defaults to
            ``~/.config/brewstanza/config.toml``.

    Returns:
        True if the wizard completed successfully and config was written,
        False if the user cancelled.
    """
    console = console or Console()
    config_path = config_path or _DEFAULT_CONFIG_PATH

    console.print(
        Panel(
            "[bold cyan]BrewStanza — First-run Setup[/bold cyan]\n\n"
            "A GitHub Personal Access Token (PAT) with [bold]repo[/bold] scope is required "
            "to sync your environment snapshot.\n\n"
            "Generate one at: [link=https://github.com/settings/tokens]"
            "https://github.com/settings/tokens[/link]",
            expand=False,
        )
    )

    token = Prompt.ask(
        "\n[bold]GitHub PAT[/bold] (ghp_...)",
        password=True,
    ).strip()

    if not token:
        console.print("[red]✗[/red] No token provided. Skipping setup.")
        return False

    repository = Prompt.ask(
        "[bold]Repository[/bold] (e.g. wduqu001/dotfiles)",
    ).strip()

    if not repository or "/" not in repository:
        console.print(
            "[red]✗[/red] Invalid repository format. Expected [cyan]owner/repo[/cyan]."
        )
        return False

    branch = Prompt.ask(
        "[bold]Branch[/bold]",
        default="main",
    ).strip()

    _write_config(token, repository, branch, config_path)
    console.print(
        f"\n[green]✓[/green] Configuration written to [cyan]{config_path}[/cyan]\n"
        "Run [bold]brewstanza sync[/bold] to push your first snapshot."
    )
    return True
