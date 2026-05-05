"""Unit tests for GitHubSync."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from brewstanza.config import Config, GitHubConfig, ScannerConfig
from brewstanza.exporter.github_sync import GitHubSync, GitHubSyncError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(token: str = "ghp_test", repo: str = "user/dotfiles") -> Config:
    return Config(
        github=GitHubConfig(token=token, repository=repo, branch="main"),
        scanner=ScannerConfig(),
    )


def _make_sync(token: str = "ghp_test", repo: str = "user/dotfiles") -> GitHubSync:
    return GitHubSync(_make_config(token=token, repo=repo))


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestConfigValidation:
    """Tests for _validate_config() — called inside sync()."""

    def test_raises_when_token_missing(self) -> None:
        syncer = _make_sync(token="")
        with pytest.raises(GitHubSyncError, match="Personal Access Token"):
            syncer.sync({"Brewfile": "brew \"git\""})

    def test_raises_when_repo_missing(self) -> None:
        syncer = _make_sync(repo="")
        with pytest.raises(GitHubSyncError, match="repository is not configured"):
            syncer.sync({"Brewfile": "brew \"git\""})

    def test_error_includes_token_settings_url(self) -> None:
        syncer = _make_sync(token="")
        with pytest.raises(GitHubSyncError) as exc_info:
            syncer.sync({"Brewfile": ""})
        assert "github.com/settings/tokens" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


class TestDryRun:
    """sync(dry_run=True) should not execute any git commands."""

    def test_dry_run_returns_string_with_dry_run_prefix(self) -> None:
        syncer = _make_sync()
        result = syncer.sync({"Brewfile": "brew \"git\""}, dry_run=True)
        assert result.startswith("[DRY RUN]")

    def test_dry_run_mentions_commit_message(self) -> None:
        syncer = _make_sync()
        result = syncer.sync({"Brewfile": "content"}, dry_run=True)
        assert "BrewStanza sync" in result

    def test_dry_run_mentions_all_filenames(self) -> None:
        syncer = _make_sync()
        result = syncer.sync({"Brewfile": "", "snap.json": ""}, dry_run=True)
        assert "Brewfile" in result
        assert "snap.json" in result

    def test_dry_run_does_not_call_subprocess(self) -> None:
        syncer = _make_sync()
        with patch("subprocess.run") as mock_run:
            syncer.sync({"Brewfile": ""}, dry_run=True)
            mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# Happy path (mocked subprocess)
# ---------------------------------------------------------------------------


class TestSyncHappyPath:
    """sync() with valid config and mocked git calls succeeds."""

    def _mock_run(self, *args: object, **kwargs: object) -> MagicMock:
        """Return a fake CompletedProcess for every git call."""
        mock = MagicMock()
        mock.stdout = ""
        mock.returncode = 0
        return mock

    def test_sync_calls_git_clone(self) -> None:
        syncer = _make_sync()
        with patch("subprocess.run", side_effect=self._mock_run) as mock_run:
            syncer.sync({"Brewfile": "brew \"git\""})
        first_call_args = mock_run.call_args_list[0][0][0]
        assert first_call_args[0] == "git"
        assert first_call_args[1] == "clone"

    def test_sync_calls_git_commit(self) -> None:
        syncer = _make_sync()
        with patch("subprocess.run", side_effect=self._mock_run) as mock_run:
            syncer.sync({"Brewfile": "content"})
        all_subcmds = [c[0][0][1] for c in mock_run.call_args_list]
        assert "commit" in all_subcmds

    def test_sync_calls_git_push(self) -> None:
        syncer = _make_sync()
        with patch("subprocess.run", side_effect=self._mock_run) as mock_run:
            syncer.sync({"Brewfile": "content"})
        all_subcmds = [c[0][0][1] for c in mock_run.call_args_list]
        assert "push" in all_subcmds

    def test_sync_returns_success_message(self) -> None:
        syncer = _make_sync()
        with patch("subprocess.run", side_effect=self._mock_run):
            result = syncer.sync({"Brewfile": "brew \"git\""})
        assert "user/dotfiles" in result

    def test_commit_message_includes_timestamp(self) -> None:
        """The git commit call must include 'BrewStanza sync — <timestamp>'."""
        syncer = _make_sync()
        commit_msgs: list[str] = []

        def capturing_run(cmd: list[str], **kwargs: object) -> MagicMock:
            if "commit" in cmd:
                # The commit message follows '-m'
                idx = cmd.index("-m")
                commit_msgs.append(cmd[idx + 1])
            mock = MagicMock()
            mock.stdout = ""
            mock.returncode = 0
            return mock

        with patch("subprocess.run", side_effect=capturing_run):
            syncer.sync({"Brewfile": ""})

        assert commit_msgs, "No commit was made"
        assert commit_msgs[0].startswith("BrewStanza sync — ")


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestSyncErrors:
    """Git subprocess failures are surfaced as GitHubSyncError."""

    def test_git_not_installed_raises_friendly_error(self) -> None:
        syncer = _make_sync()
        with patch("subprocess.run", side_effect=FileNotFoundError("git not found")):
            with pytest.raises(GitHubSyncError, match="git is not installed"):
                syncer.sync({"Brewfile": ""})

    def test_auth_failure_raises_friendly_error(self) -> None:
        syncer = _make_sync()

        def fail_with_403(cmd: list[str], **kwargs: object) -> None:
            raise subprocess.CalledProcessError(
                returncode=128, cmd=cmd, stderr="error: 403 Forbidden"
            )

        with patch("subprocess.run", side_effect=fail_with_403):
            with pytest.raises(GitHubSyncError, match="authentication failed"):
                syncer.sync({"Brewfile": ""})

    def test_generic_git_error_raises_with_stderr(self) -> None:
        syncer = _make_sync()

        def fail_generic(cmd: list[str], **kwargs: object) -> None:
            raise subprocess.CalledProcessError(
                returncode=1, cmd=cmd, stderr="fatal: repository not found"
            )

        with patch("subprocess.run", side_effect=fail_generic):
            with pytest.raises(GitHubSyncError, match="repository not found"):
                syncer.sync({"Brewfile": ""})
