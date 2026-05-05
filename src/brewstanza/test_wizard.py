"""Unit tests for the first-run configuration wizard."""

import tomllib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from brewstanza.wizard import needs_wizard, run_wizard

# ---------------------------------------------------------------------------
# needs_wizard()
# ---------------------------------------------------------------------------


class TestNeedsWizard:
    """Tests for needs_wizard() — detects missing or incomplete config."""

    def test_returns_true_when_config_file_missing(self) -> None:
        assert needs_wizard(Path("/nonexistent/path/config.toml")) is True

    def test_returns_true_when_token_is_empty(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            cfg.write_text('[github]\ntoken = ""\nrepository = "u/r"\nbranch = "main"\n')
            assert needs_wizard(cfg) is True

    def test_returns_false_when_token_is_set(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            cfg.write_text('[github]\ntoken = "ghp_abc"\nrepository = "u/r"\nbranch = "main"\n')
            assert needs_wizard(cfg) is False

    def test_returns_true_when_github_section_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            cfg.write_text("[scanner]\nconcurrency = 8\n")
            assert needs_wizard(cfg) is True


# ---------------------------------------------------------------------------
# run_wizard() — happy path
# ---------------------------------------------------------------------------


class TestRunWizardHappyPath:
    """run_wizard() completes and writes a valid config.toml."""

    def _run(self, config_path: Path, answers: list[str]) -> bool:
        """Patch Prompt.ask to return *answers* in sequence."""
        with patch("brewstanza.wizard.Prompt.ask", side_effect=answers):
            return run_wizard(config_path=config_path)

    def test_returns_true_on_success(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            result = self._run(cfg, ["ghp_mytoken", "user/dotfiles", "main"])
            assert result is True

    def test_writes_config_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            self._run(cfg, ["ghp_mytoken", "user/dotfiles", "main"])
            assert cfg.exists()

    def test_config_contains_token(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            self._run(cfg, ["ghp_mytoken", "user/dotfiles", "main"])
            data = tomllib.loads(cfg.read_text())
            assert data["github"]["token"] == "ghp_mytoken"

    def test_config_contains_repository(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            self._run(cfg, ["ghp_mytoken", "user/dotfiles", "main"])
            data = tomllib.loads(cfg.read_text())
            assert data["github"]["repository"] == "user/dotfiles"

    def test_config_contains_branch(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            self._run(cfg, ["ghp_mytoken", "user/dotfiles", "feature"])
            data = tomllib.loads(cfg.read_text())
            assert data["github"]["branch"] == "feature"

    def test_config_contains_scanner_defaults(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            self._run(cfg, ["ghp_mytoken", "user/dotfiles", "main"])
            data = tomllib.loads(cfg.read_text())
            assert data["scanner"]["concurrency"] == 8
            assert data["scanner"]["timeout"] == 30

    def test_creates_parent_directories(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "nested" / "path" / "config.toml"
            self._run(cfg, ["ghp_mytoken", "user/dotfiles", "main"])
            assert cfg.exists()


# ---------------------------------------------------------------------------
# run_wizard() — cancellation / invalid input
# ---------------------------------------------------------------------------


class TestRunWizardCancellation:
    """run_wizard() returns False on invalid or empty input."""

    def test_returns_false_when_token_is_empty(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            with patch("brewstanza.wizard.Prompt.ask", side_effect=["", "user/dotfiles", "main"]):
                result = run_wizard(config_path=cfg)
            assert result is False

    def test_returns_false_when_repo_has_no_slash(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            with patch(
                "brewstanza.wizard.Prompt.ask",
                side_effect=["ghp_token", "invalidepo", "main"],
            ):
                result = run_wizard(config_path=cfg)
            assert result is False

    def test_no_config_written_on_cancellation(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            with patch("brewstanza.wizard.Prompt.ask", side_effect=["", "u/r", "main"]):
                run_wizard(config_path=cfg)
            assert not cfg.exists()


# ---------------------------------------------------------------------------
# needs_wizard() — exception branch (lines 57-58)
# ---------------------------------------------------------------------------


class TestNeedsWizardEdgeCases:
    """Edge cases for needs_wizard()."""

    def test_returns_true_on_corrupt_toml(self) -> None:
        """A file that isn't valid TOML should trigger the except branch."""
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            cfg.write_bytes(b"\xff\xfe invalid utf-8 toml \x00")
            # Exception during tomllib.load → should return True
            assert needs_wizard(cfg) is True

    def test_returns_true_when_no_path_given_and_default_missing(self) -> None:
        """When the default config path doesn't exist, needs_wizard returns True."""
        with patch(
            "brewstanza.wizard._DEFAULT_CONFIG_PATH",
            Path("/nonexistent/brewstanza/config.toml"),
        ):
            assert needs_wizard() is True


# ---------------------------------------------------------------------------
# run_wizard() — default console path
# ---------------------------------------------------------------------------


class TestRunWizardDefaultConsole:
    """run_wizard() with no console argument creates its own Console."""

    def test_run_wizard_creates_console_when_none(self) -> None:
        """Calling without a console arg should not raise."""
        with TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.toml"
            with patch(
                "brewstanza.wizard.Prompt.ask",
                side_effect=["ghp_tok", "user/repo", "main"],
            ):
                result = run_wizard(console=None, config_path=cfg)
            assert result is True

