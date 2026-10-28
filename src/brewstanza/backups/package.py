import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from brewstanza.backups.results import BackupResult

PACKAGE_MARKER = ".brewstanza.json"
PACKAGE_FORMAT_VERSION = 1


def _git_executable() -> str | None:
    return shutil.which("git")


def _existing_git_root(destination: Path, git_executable: str) -> Path | None:
    probe_path = destination
    while not probe_path.exists():
        if probe_path.parent == probe_path:
            return None
        probe_path = probe_path.parent
    result = subprocess.run(
        [git_executable, "-C", str(probe_path), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def initialize_package(destination: Path) -> bool:
    """Initialize a package root and return whether Git manages its integrity."""
    destination = destination.expanduser().resolve()
    marker_path = destination / PACKAGE_MARKER

    if marker_path.is_file():
        try:
            marker: Any = json.loads(marker_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Invalid BrewStanza package marker at {marker_path}.") from error
        if (
            not isinstance(marker, dict)
            or marker.get("format_version") != PACKAGE_FORMAT_VERSION
            or marker.get("integrity") not in {"git", "sha256"}
        ):
            raise ValueError(f"Unsupported BrewStanza package marker at {marker_path}.")
        return marker.get("integrity") == "git"

    git_executable = _git_executable()
    git_root = _existing_git_root(destination, git_executable) if git_executable else None
    if destination.exists() and any(destination.iterdir()) and git_root is None:
        raise ValueError(f"Package destination {destination} is not empty and is not initialized.")

    destination.mkdir(parents=True, exist_ok=True)
    if git_executable is not None:
        if git_root is None:
            subprocess.run(
                [git_executable, "init", str(destination)],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        integrity = "git"
    else:
        integrity = "sha256"

    marker_path.write_text(
        json.dumps({"format_version": PACKAGE_FORMAT_VERSION, "integrity": integrity}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return integrity == "git"


def _restore_path(relative_path: Path) -> str | None:
    first = relative_path.parts[0] if relative_path.parts else ""
    roots = {
        ".claude": Path(".claude"),
        ".zsh": Path(".zsh"),
        ".zshrc": Path(".zshrc"),
        ".gitconfig": Path(".gitconfig"),
        ".ssh": Path(".ssh"),
        "Fonts": Path("Library") / "Fonts",
    }
    if first == "Brewfile" or first.startswith("apps_"):
        return None
    restore_root = roots.get(first)
    if restore_root is None:
        return None
    remainder = relative_path.parts[1:]
    restore_path = restore_root.joinpath(*remainder)
    return restore_path.as_posix()


def _file_entries(data_dir: Path, *, include_checksums: bool) -> list[dict[str, str | None]]:
    entries: list[dict[str, str | None]] = []
    for file_path in sorted(path for path in data_dir.rglob("*") if path.is_file()):
        relative = file_path.relative_to(data_dir)
        entry: dict[str, str | None] = {
            "path": (Path("data") / relative).as_posix(),
            "restore_path": _restore_path(relative),
        }
        if include_checksums:
            entry["sha256"] = sha256(file_path.read_bytes()).hexdigest()
        entries.append(entry)
    return entries


def create_snapshot(
    destination: Path,
    staged_data: Path,
    results: list[BackupResult],
    *,
    created_at: datetime | None = None,
) -> Path:
    """Publish staged module output as a timestamped, versioned package."""
    destination = destination.expanduser().resolve()
    marker_path = destination / PACKAGE_MARKER
    marker: Any = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("format_version") != PACKAGE_FORMAT_VERSION:
        raise ValueError(f"Unsupported BrewStanza package format in {destination}.")

    integrity = marker["integrity"]
    current_time = created_at or datetime.now(timezone.utc)
    timestamp = current_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_name = timestamp
    suffix = 1
    while (destination / snapshot_name).exists():
        suffix += 1
        snapshot_name = f"{timestamp}-{suffix}"

    package_temp = Path(tempfile.mkdtemp(prefix=".brewstanza-package-", dir=destination))
    snapshot_path = destination / snapshot_name
    try:
        shutil.copytree(staged_data, package_temp / "data", symlinks=True)
        has_failures = any(result.status == "failed" for result in results)
        modules = [
            {
                "name": result.component,
                "status": result.status,
                "artifacts_copied": result.artifacts_copied,
            }
            for result in results
        ]
        manifest: dict[str, Any] = {
            "format_version": PACKAGE_FORMAT_VERSION,
            "created_at": current_time.isoformat(),
            "status": "partial" if has_failures else "complete",
            "modules": modules,
            "files": _file_entries(package_temp / "data", include_checksums=integrity == "sha256"),
        }
        (package_temp / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(package_temp, snapshot_path)
    except BaseException:
        if package_temp.exists():
            shutil.rmtree(package_temp)
        raise

    if integrity == "git" and not has_failures:
        git_executable = _git_executable() or "git"
        subprocess.run(
            [git_executable, "add", "--", PACKAGE_MARKER, snapshot_name],
            cwd=destination,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        subprocess.run(
            [
                git_executable,
                "commit",
                "--only",
                "-m",
                f"BrewStanza backup {snapshot_name}",
                "--",
                PACKAGE_MARKER,
                snapshot_name,
            ],
            cwd=destination,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    return snapshot_path
