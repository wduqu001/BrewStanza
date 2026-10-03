import sys
from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe
from brewstanza.backups.transaction import replace_text

console = Console()

def backup(backup_dir: Path) -> BackupResult:
    if sys.platform != "darwin":
        console.print("[yellow]Skipped:[/yellow] App listing is only supported on macOS.")
        return BackupResult.skipped("Apps", "App listing is only supported on macOS.")
        
    app_dirs = [
        Path("/Applications"),
        Path.home() / "Applications"
    ]
    try:
        ensure_safe(backup_dir, *app_dirs)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return BackupResult.failed("Apps", str(e))
    
    apps_found = []
    try:
        for app_dir in app_dirs:
            if app_dir.exists():
                for app_path in app_dir.glob("*.app"):
                    apps_found.append(app_path.name)
    except OSError as e:
        console.print(f"[red]Error scanning applications:[/red] {e}")
        return BackupResult.failed("Apps", str(e))
                
    if not apps_found:
        console.print("[yellow]Skipped:[/yellow] No .app bundles found.")
        return BackupResult.skipped("Apps", "No .app bundles found.")
        
    apps_found.sort()
    
    dest_file = backup_dir / "apps_list.txt"
    try:
        replace_text("".join(f"{app}\n" for app in apps_found), dest_file)
        console.print(f"[green]Success:[/green] Backed up list of {len(apps_found)} apps to {dest_file}")  # noqa: E501
        return BackupResult.success("Apps", f"Backed up {len(apps_found)} app names.", 1)
    except OSError as e:
        console.print(f"[red]Error writing apps list:[/red] {e}")
        return BackupResult.failed("Apps", str(e))
