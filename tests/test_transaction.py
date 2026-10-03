import os
from pathlib import Path

import pytest

from brewstanza.backups.transaction import replace_directory, replace_file, replace_texts


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


def test_replace_directory_cleans_staging_after_partial_copy_failure(tmp_path, mocker):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (destination / "config").write_text("old")

    def partial_copy(_source, staging, **_kwargs):
        Path(staging, "partial").write_text("incomplete")
        raise PermissionError("Access denied")

    mocker.patch(
        "brewstanza.backups.transaction.shutil.copytree",
        side_effect=partial_copy,
    )

    with pytest.raises(PermissionError, match="Access denied"):
        replace_directory(source, destination)

    assert (destination / "config").read_text() == "old"
    assert not (destination / "partial").exists()
    assert list(tmp_path.glob(".destination.tmp-*")) == []
    assert list(tmp_path.glob(".destination.old-*")) == []


def test_replace_file_propagates_destination_permission_error(tmp_path, mocker):
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("new")
    destination.write_text("old")
    mocker.patch(
        "brewstanza.backups.transaction.os.replace",
        side_effect=PermissionError("Access denied"),
    )

    with pytest.raises(PermissionError, match="Access denied"):
        replace_file(source, destination)

    assert destination.read_text() == "old"
    assert list(tmp_path.glob(".destination.txt.tmp-*")) == []


def test_replace_texts_restores_all_files_when_second_replace_fails(tmp_path, mocker):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("old first")
    second.write_text("old second")
    real_replace = os.replace
    calls = 0

    def fail_on_second_commit(source, destination, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 4:
            raise PermissionError("Access denied")
        return real_replace(source, destination, **kwargs)

    mocker.patch(
        "brewstanza.backups.transaction.os.replace",
        side_effect=fail_on_second_commit,
    )

    with pytest.raises(PermissionError, match="Access denied"):
        replace_texts({first: "new first", second: "new second"})

    assert first.read_text() == "old first"
    assert second.read_text() == "old second"


def test_replace_texts_restores_dangling_symlink_on_failure(tmp_path, mocker):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("old first")
    second.symlink_to(tmp_path / "missing-target")
    real_replace = os.replace
    calls = 0

    def fail_on_second_commit(source, destination, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 4:
            raise PermissionError("Access denied")
        return real_replace(source, destination, **kwargs)

    mocker.patch(
        "brewstanza.backups.transaction.os.replace",
        side_effect=fail_on_second_commit,
    )

    with pytest.raises(PermissionError, match="Access denied"):
        replace_texts({first: "new first", second: "new second"})

    assert first.read_text() == "old first"
    assert second.is_symlink()
    assert second.readlink() == tmp_path / "missing-target"


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
