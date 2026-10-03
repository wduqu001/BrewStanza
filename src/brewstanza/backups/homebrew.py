import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult

console = Console()

def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
    if shutil.which("brew") is None:
        console.print("[yellow]Skipped:[/yellow] 'brew' command not found in PATH.")
        return BackupResult.skipped("Homebrew", "'brew' command not found in PATH.")
        
    brewfile_dest = backup_dir / "Brewfile"
    temporary_path: Path | None = None

    if dry_run:
        console.print(f"[cyan]Would run:[/cyan] brew bundle dump to {brewfile_dest}")
        return BackupResult.success(
            "Homebrew", f"Would back up Homebrew inventory to {brewfile_dest}.", 1
        )
    
    console.print(f"[cyan]Running:[/cyan] brew bundle dump to {brewfile_dest}...")
    try:
        fd, temporary_name = tempfile.mkstemp(prefix=".Brewfile.tmp-", dir=backup_dir)
        os.close(fd)
        temporary_path = Path(temporary_name)
        # Run brew bundle dump. Using --force to overwrite if it exists.
        result = subprocess.run(
            ["brew", "bundle", "dump", f"--file={temporary_path}", "--force"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            console.print(f"[green]Success:[/green] Backed up Homebrew inventory to {brewfile_dest}")  # noqa: E501
            temporary_path.replace(brewfile_dest)
            return BackupResult.success(
                "Homebrew", f"Backed up Homebrew inventory to {brewfile_dest}.", 1
            )
        else:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            diagnostic = stderr or stdout
            message = (
                f"Homebrew command failed with exit code {result.returncode}: {diagnostic}"
                if diagnostic
                else f"Homebrew command failed with exit code {result.returncode}."
            )
            console.print(f"[red]Error running brew bundle dump:[/red]\n{message}")
            return BackupResult.failed("Homebrew", message)
    except subprocess.TimeoutExpired as e:
        stderr_value = e.stderr or ""
        stdout_value = e.stdout or ""
        stderr_text = (
            stderr_value.decode(errors="replace")
            if isinstance(stderr_value, bytes)
            else str(stderr_value)
        )
        stdout_text = (
            stdout_value.decode(errors="replace")
            if isinstance(stdout_value, bytes)
            else str(stdout_value)
        )
        output_text = stderr_text.strip() or stdout_text.strip()
        message = "Homebrew command timed out after 30 seconds."
        if output_text.strip():
            message = f"{message} Output: {output_text.strip()}"
        console.print(f"[red]Error backing up Homebrew:[/red] {message}")
        return BackupResult.failed("Homebrew", message)
    except (OSError, subprocess.SubprocessError) as e:
        console.print(f"[red]Error backing up Homebrew:[/red] {e}")
        return BackupResult.failed("Homebrew", str(e))
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
