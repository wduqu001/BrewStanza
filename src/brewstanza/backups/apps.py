import sys
from pathlib import Path

from rich.console import Console

console = Console()

def backup(backup_dir: Path) -> bool:
    if sys.platform != "darwin":
        console.print("[yellow]Skipped:[/yellow] App listing is only supported on macOS.")
        return False
        
    app_dirs = [
        Path("/Applications"),
        Path.home() / "Applications"
    ]
    
    apps_found = []
    
    for app_dir in app_dirs:
        if app_dir.exists():
            for app_path in app_dir.glob("*.app"):
                apps_found.append(app_path.name)
                
    if not apps_found:
        console.print("[yellow]Skipped:[/yellow] No .app bundles found.")
        return False
        
    apps_found.sort()
    
    dest_file = backup_dir / "apps_list.txt"
    try:
        with open(dest_file, "w", encoding="utf-8") as f:
            for app in apps_found:
                f.write(f"{app}\n")
        console.print(f"[green]Success:[/green] Backed up list of {len(apps_found)} apps to {dest_file}")  # noqa: E501
        return True
    except Exception as e:
        console.print(f"[red]Error writing apps list:[/red] {e}")
        return False
