from pathlib import Path


def ensure_dest_not_home(backup_dir: Path) -> None:
    """Reject the home directory as a backup destination.

    Several modules write fixed names into the destination (Brewfile,
    .gitconfig, .ssh/config). Pointing the destination at home would
    overwrite real user files, so refuse it up front.
    """
    if backup_dir.resolve() == Path.home().resolve():
        raise ValueError(f"Backup destination cannot be the home directory: {backup_dir}")


def ensure_safe(backup_dir: Path, *sources: Path) -> None:
    """Reject a destination that overlaps any backup source.

    A destination equal to a source, containing a source, or inside a
    source would overwrite or delete the originals during backup, so we
    refuse to continue.
    """
    ensure_dest_not_home(backup_dir)
    dest = backup_dir.resolve()
    for source in sources:
        src = source.resolve()
        if dest == src or src.is_relative_to(dest) or dest.is_relative_to(src):
            raise ValueError(f"Backup destination overlaps the backup source: {source}")
