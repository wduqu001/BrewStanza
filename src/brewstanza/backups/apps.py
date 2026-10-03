import json
import sys
from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe
from brewstanza.backups.transaction import replace_texts

console = Console()
MANIFEST_VERSION = 1

def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
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
    
    apps_found: list[dict[str, str]] = []
    try:
        for app_dir in app_dirs:
            if app_dir.exists():
                for app_path in app_dir.glob("*.app"):
                    apps_found.append(
                        {
                            "name": app_path.name,
                            "path": str(app_path),
                            "source": str(app_dir),
                        }
                    )
    except OSError as e:
        console.print(f"[red]Error scanning applications:[/red] {e}")
        return BackupResult.failed("Apps", str(e))
                
    if not apps_found:
        console.print("[yellow]Skipped:[/yellow] No .app bundles found.")
        return BackupResult.skipped("Apps", "No .app bundles found.")
        
    apps_found.sort(key=lambda app: (app["name"], app["path"]))
    
    manifest_file = backup_dir / "apps_manifest.json"
    legacy_file = backup_dir / "apps_list.txt"
    manifest = {
        "schema_version": MANIFEST_VERSION,
        "applications": apps_found,
    }
    if dry_run:
        console.print(
            f"[cyan]Would back up:[/cyan] {len(apps_found)} apps to {manifest_file}"
        )
        return BackupResult.success("Apps", f"Would back up {len(apps_found)} apps.", 2)

    try:
        replace_texts(
            {
                manifest_file: json.dumps(manifest, indent=2) + "\n",
                legacy_file: "".join(f"{app['name']}\n" for app in apps_found),
            }
        )
        console.print(
            f"[green]Success:[/green] Backed up manifest of {len(apps_found)} apps "
            f"to {manifest_file}"
        )
        return BackupResult.success("Apps", f"Backed up {len(apps_found)} apps.", 2)
    except OSError as e:
        console.print(f"[red]Error writing apps list:[/red] {e}")
        return BackupResult.failed("Apps", str(e))
