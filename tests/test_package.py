import json
from datetime import datetime, timezone
from hashlib import sha256

import pytest

from brewstanza.backups.package import create_snapshot, initialize_package
from brewstanza.backups.results import BackupResult


def test_initialize_package_uses_checksums_without_git(mocker, tmp_path):
    destination = tmp_path / "backup"
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)

    uses_git = initialize_package(destination)

    assert uses_git is False
    marker = json.loads((destination / ".brewstanza.json").read_text())
    assert marker["format_version"] == 1
    assert marker["integrity"] == "sha256"


def test_initialize_package_creates_git_repository_when_available(mocker, tmp_path):
    destination = tmp_path / "backup"
    mocker.patch("brewstanza.backups.package._git_executable", return_value="/usr/bin/git")
    mocker.patch("brewstanza.backups.package._existing_git_root", return_value=None)
    run = mocker.patch("brewstanza.backups.package.subprocess.run")

    uses_git = initialize_package(destination)

    assert uses_git is True
    run.assert_called_once_with(
        ["/usr/bin/git", "init", str(destination)],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    marker = json.loads((destination / ".brewstanza.json").read_text())
    assert marker["integrity"] == "git"


def test_initialize_package_accepts_empty_destination(mocker, tmp_path):
    destination = tmp_path / "existing-empty"
    destination.mkdir()
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)

    initialize_package(destination)

    assert (destination / ".brewstanza.json").is_file()


def test_initialize_package_refuses_unrecognized_nonempty_destination(mocker, tmp_path):
    destination = tmp_path / "unrelated"
    destination.mkdir()
    unrelated = destination / "notes.txt"
    unrelated.write_text("keep me")
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)

    with pytest.raises(ValueError, match="not empty"):
        initialize_package(destination)

    assert unrelated.read_text() == "keep me"
    assert not (destination / ".brewstanza.json").exists()


def test_initialize_package_adopts_nonempty_existing_git_repository(mocker, tmp_path):
    repository = tmp_path / "dotfiles"
    repository.mkdir()
    (repository / "README.md").write_text("unrelated content")
    mocker.patch("brewstanza.backups.package._git_executable", return_value="/usr/bin/git")
    run = mocker.patch(
        "brewstanza.backups.package.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout=f"{repository}\n"),
    )

    uses_git = initialize_package(repository)

    assert uses_git is True
    assert (repository / "README.md").read_text() == "unrelated content"
    assert json.loads((repository / ".brewstanza.json").read_text())["integrity"] == "git"
    assert run.call_count == 1
    assert run.call_args.args[0][1:3] == ["-C", str(repository)]
    assert run.call_args.args[0][-2:] == ["rev-parse", "--show-toplevel"]


def test_initialize_package_is_idempotent_for_brewstanza_destination(mocker, tmp_path):
    destination = tmp_path / "backup"
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)
    initialize_package(destination)
    mocker.patch("brewstanza.backups.package._git_executable", return_value="/usr/bin/git")
    run = mocker.patch("brewstanza.backups.package.subprocess.run")

    uses_git = initialize_package(destination)

    assert uses_git is False
    run.assert_not_called()


def test_create_snapshot_writes_versioned_manifest_and_checksums(tmp_path):
    destination = tmp_path / "backup"
    destination.mkdir()
    (destination / ".brewstanza.json").write_text(
        json.dumps({"format_version": 1, "integrity": "sha256"})
    )
    staged_data = tmp_path / "staged-data"
    (staged_data / ".gitconfig").parent.mkdir(parents=True)
    config = staged_data / ".gitconfig"
    config.write_text("[user]\nname=Test\n")
    (staged_data / "Brewfile").write_text("brew 'python'\n")
    created_at = datetime(2026, 10, 27, 12, 30, tzinfo=timezone.utc)

    snapshot = create_snapshot(
        destination,
        staged_data,
        [BackupResult.success("Git", "copied", 1), BackupResult.success("Homebrew", "copied", 1)],
        created_at=created_at,
    )

    assert snapshot == destination / "20261027T123000Z"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["format_version"] == 1
    assert manifest["status"] == "complete"
    assert manifest["created_at"] == "2026-10-27T12:30:00+00:00"
    assert "message" not in manifest["modules"][0]
    entries = {entry["path"]: entry for entry in manifest["files"]}
    assert entries["data/.gitconfig"]["restore_path"] == ".gitconfig"
    assert entries["data/Brewfile"]["restore_path"] is None
    assert entries["data/.gitconfig"]["sha256"] == sha256(config.read_bytes()).hexdigest()
    assert (snapshot / "data" / ".gitconfig").read_text() == "[user]\nname=Test\n"


def test_create_partial_snapshot_is_retained_without_git_commit(mocker, tmp_path):
    destination = tmp_path / "backup"
    destination.mkdir()
    (destination / ".brewstanza.json").write_text(
        json.dumps({"format_version": 1, "integrity": "git"})
    )
    staged_data = tmp_path / "staged-data"
    staged_data.mkdir()
    (staged_data / ".zshrc").write_text("export FOO=bar\n")
    run = mocker.patch("brewstanza.backups.package.subprocess.run")
    created_at = datetime(2026, 10, 27, 12, 30, tzinfo=timezone.utc)

    snapshot = create_snapshot(
        destination,
        staged_data,
        [BackupResult.failed("Zsh", "one artifact failed", 1)],
        created_at=created_at,
    )

    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["status"] == "partial"
    assert manifest["modules"][0]["status"] == "failed"
    assert "sha256" not in manifest["files"][0]
    run.assert_not_called()


def test_create_complete_git_snapshot_adds_and_commits_only_snapshot(mocker, tmp_path):
    destination = tmp_path / "backup"
    destination.mkdir()
    (destination / ".brewstanza.json").write_text(
        json.dumps({"format_version": 1, "integrity": "git"})
    )
    staged_data = tmp_path / "staged-data"
    staged_data.mkdir()
    (staged_data / ".zshrc").write_text("export FOO=bar\n")
    run = mocker.patch("brewstanza.backups.package.subprocess.run")
    created_at = datetime(2026, 10, 27, 12, 30, tzinfo=timezone.utc)

    create_snapshot(
        destination,
        staged_data,
        [BackupResult.success("Zsh", "copied", 1)],
        created_at=created_at,
    )

    assert [call.args[0][1:] for call in run.call_args_list] == [
        ["add", "--", ".brewstanza.json", "20261027T123000Z"],
        [
            "commit",
            "--only",
            "-m",
            "BrewStanza backup 20261027T123000Z",
            "--",
            ".brewstanza.json",
            "20261027T123000Z",
        ],
    ]
    assert all(call.kwargs["cwd"] == destination for call in run.call_args_list)
    assert all("push" not in call.args[0] for call in run.call_args_list)
