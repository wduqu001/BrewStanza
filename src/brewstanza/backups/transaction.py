import os
import shutil
import tempfile
from pathlib import Path


def replace_directory(source: Path, destination: Path) -> None:
    """Copy a directory into a sibling staging directory and replace atomically."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.tmp-", dir=destination.parent))
    previous: Path | None = None
    try:
        shutil.copytree(source, staging, dirs_exist_ok=True, symlinks=True)
        if destination.exists():
            previous = Path(
                tempfile.mkdtemp(prefix=f".{destination.name}.old-", dir=destination.parent)
            )
            previous.rmdir()
            os.replace(destination, previous)
        os.replace(staging, destination)
    except BaseException:
        if previous is not None and not destination.exists():
            os.replace(previous, destination)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if previous is not None and previous.exists():
            if previous.is_symlink() or not previous.is_dir():
                previous.unlink()
            else:
                shutil.rmtree(previous)


def replace_file(source: Path, destination: Path) -> None:
    """Copy a file to a sibling temporary file and atomically replace the target."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.tmp-", dir=destination.parent)
    os.close(fd)
    temporary_path = Path(temporary)
    try:
        shutil.copy2(source, temporary_path)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def replace_text(content: str, destination: Path) -> None:
    """Write text to a sibling temporary file and atomically replace the target."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.tmp-", dir=destination.parent)
    os.close(fd)
    temporary_path = Path(temporary)
    try:
        temporary_path.write_text(content, encoding="utf-8")
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def replace_texts(contents: dict[Path, str]) -> None:
    """Replace several text files together, restoring prior files on failure."""
    temporary_paths: dict[Path, Path] = {}
    previous_paths: dict[Path, Path] = {}
    committed: list[Path] = []
    try:
        for destination, content in contents.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(
                prefix=f".{destination.name}.tmp-", dir=destination.parent
            )
            os.close(fd)
            temporary_path = Path(temporary)
            temporary_path.write_text(content, encoding="utf-8")
            temporary_paths[destination] = temporary_path

        for destination in contents:
            if os.path.lexists(destination):
                fd, previous = tempfile.mkstemp(
                    prefix=f".{destination.name}.old-", dir=destination.parent
                )
                os.close(fd)
                previous_path = Path(previous)
                previous_path.unlink()
                os.replace(destination, previous_path)
                previous_paths[destination] = previous_path

        for destination, temporary_path in temporary_paths.items():
            os.replace(temporary_path, destination)
            committed.append(destination)
    except BaseException:
        for destination in committed:
            destination.unlink(missing_ok=True)
        for destination, previous_path in previous_paths.items():
            if os.path.lexists(previous_path):
                os.replace(previous_path, destination)
        raise
    finally:
        for temporary_path in temporary_paths.values():
            temporary_path.unlink(missing_ok=True)
        for previous_path in previous_paths.values():
            previous_path.unlink(missing_ok=True)
