from pathlib import Path

import pytest

from brewstanza.backups.transaction import replace_directory, replace_file


def test_replace_file_preserves_existing_on_copy_failure(tmp_path, mocker):
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("new")
    destination.write_text("old")
    mocker.patch("brewstanza.backups.transaction.shutil.copy2", side_effect=PermissionError())

    with pytest.raises(PermissionError):
        replace_file(source, destination)

    assert destination.read_text() == "old"


def test_replace_directory_preserves_existing_on_copy_failure(tmp_path, mocker):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "config").write_text("new")
    (destination / "config").write_text("old")
    mocker.patch(
        "brewstanza.backups.transaction.shutil.copytree",
        side_effect=PermissionError(),
    )

    with pytest.raises(PermissionError):
        replace_directory(source, destination)

    assert (destination / "config").read_text() == "old"


def test_replace_directory_preserves_source_symlinks(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "external").symlink_to("/etc/hosts")

    replace_directory(source, destination)

    assert (destination / "external").is_symlink()
    assert (destination / "external").readlink() == Path("/etc/hosts")


def test_replace_directory_cleans_up_existing_destination_symlink(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    destination.symlink_to(target, target_is_directory=True)

    replace_directory(source, destination)

    assert destination.is_dir()
    assert not destination.is_symlink()
    assert list(tmp_path.glob(".destination.old-*")) == []


def test_replace_directory_cleans_up_existing_destination_file(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.write_text("stale")

    replace_directory(source, destination)

    assert destination.is_dir()
    assert list(tmp_path.glob(".destination.old-*")) == []
