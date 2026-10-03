import os
import secrets
from pathlib import Path

from rich.console import Console

from brewstanza.backups.results import BackupResult
from brewstanza.backups.safety import ensure_safe

console = Console()
ALLOWED_FILES = (Path("settings.json"),)

def _open_directory(path: Path, create: bool = False) -> int:
    absolute = path.absolute()
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in absolute.parts[1:]:
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            try:
                next_descriptor = os.open(component, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, dir_fd=descriptor)
                next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _read_settings(source_dir: Path) -> bytes:
    source_descriptor = _open_directory(source_dir)
    try:
        file_descriptor = os.open(
            "settings.json", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=source_descriptor
        )
        try:
            chunks = []
            while chunk := os.read(file_descriptor, 1024 * 1024):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(file_descriptor)
    finally:
        os.close(source_descriptor)


def _open_child_directory(parent_descriptor: int, name: str, create: bool = False) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        return os.open(name, flags, dir_fd=parent_descriptor)
    except FileNotFoundError:
        if not create:
            raise
        os.mkdir(name, dir_fd=parent_descriptor)
        return os.open(name, flags, dir_fd=parent_descriptor)


def _create_temp_file(directory_descriptor: int) -> tuple[int, str]:
    for _ in range(10):
        name = f".settings-{secrets.token_hex(16)}.tmp"
        try:
            descriptor = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
                dir_fd=directory_descriptor,
            )
            return descriptor, name
        except FileExistsError:
            continue
    raise FileExistsError("Unable to create a unique temporary backup file")


def backup(backup_dir: Path, *, dry_run: bool = False) -> BackupResult:
    source_dir = Path.home() / ".claude"
    source_file = source_dir / ALLOWED_FILES[0]
    if not source_file.is_file():
        console.print(
            f"[yellow]Skipped:[/yellow] No supported Claude settings file found in {source_dir}."
        )
        return BackupResult.skipped("Claude", "No supported Claude settings file found.")

    try:
        ensure_safe(backup_dir, source_dir)
    except ValueError as e:
        console.print(f"[red]Refusing to back up:[/red] {e}")
        return BackupResult.failed("Claude", str(e))

    dest_file = backup_dir / ".claude" / ALLOWED_FILES[0]
    if dry_run:
        console.print(f"[cyan]Would back up:[/cyan] {source_file} to {dest_file}")
        return BackupResult.success("Claude", f"Would back up {source_file}.", 1)

    try:
        content = _read_settings(source_dir)
        destination_descriptor = _open_directory(backup_dir, create=True)
        claude_descriptor = -1
        temp_name = ""
        try:
            claude_descriptor = _open_child_directory(
                destination_descriptor, ".claude", create=True
            )
            try:
                temp_descriptor, temp_name = _create_temp_file(claude_descriptor)
                try:
                    written = 0
                    while written < len(content):
                        written += os.write(temp_descriptor, content[written:])
                    os.fsync(temp_descriptor)
                finally:
                    os.close(temp_descriptor)
                os.replace(
                    temp_name,
                    "settings.json",
                    src_dir_fd=claude_descriptor,
                    dst_dir_fd=claude_descriptor,
                )
            except BaseException:
                try:
                    os.unlink(temp_name, dir_fd=claude_descriptor)
                except FileNotFoundError:
                    pass
                raise
            finally:
                os.close(claude_descriptor)
        except BaseException:
            raise
        finally:
            os.close(destination_descriptor)
        console.print(f"[green]Success:[/green] Backed up {source_file} to {dest_file}")
        return BackupResult.success("Claude", f"Backed up {source_file} to {dest_file}", 1)
    except OSError as e:
        console.print(f"[red]Error backing up Claude settings:[/red] {e}")
        return BackupResult.failed("Claude", str(e))
