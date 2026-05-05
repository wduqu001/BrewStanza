"""
Tests for Config.load() and Config.from_dict() — covers lines 76-101.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brewstanza.config import Config, GitHubConfig, ScannerConfig


class TestConfigLoad:
    """Tests for Config.load() — file-based loading."""

    def test_load_returns_defaults_when_file_missing(self) -> None:
        cfg = Config.load(Path("/nonexistent/config.toml"))
        assert cfg.github.token == ""
        assert cfg.github.branch == "main"
        assert cfg.scanner.concurrency == 8
        assert cfg.scanner.timeout == 30

    def test_load_reads_github_section(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            path.write_text(
                '[github]\ntoken = "ghp_abc"\nrepository = "u/r"\nbranch = "dev"\n'
            )
            cfg = Config.load(path)
        assert cfg.github.token == "ghp_abc"
        assert cfg.github.repository == "u/r"
        assert cfg.github.branch == "dev"

    def test_load_reads_scanner_section(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            path.write_text("[scanner]\nconcurrency = 4\ntimeout = 60\n")
            cfg = Config.load(path)
        assert cfg.scanner.concurrency == 4
        assert cfg.scanner.timeout == 60

    def test_load_uses_default_path_when_none_passed(self) -> None:
        """Passing None falls through to the home-based default path — returns Config."""
        # We can't guarantee ~/.config/brewstanza/config.toml exists in CI,
        # so just assert the return type is correct and no exception is raised.
        cfg = Config.load(None)
        assert isinstance(cfg, Config)

    def test_load_handles_missing_sections_gracefully(self) -> None:
        """A config with neither [github] nor [scanner] should use defaults."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            path.write_text("# empty config\n")
            cfg = Config.load(path)
        assert cfg.github.token == ""
        assert cfg.scanner.concurrency == 8


class TestConfigFromDict:
    """Tests for Config.from_dict() — dictionary-based construction."""

    def test_from_dict_with_full_data(self) -> None:
        data = {
            "github": {"token": "tok", "repository": "owner/repo", "branch": "main"},
            "scanner": {"concurrency": 16, "timeout": 15},
        }
        cfg = Config.from_dict(data)
        assert cfg.github.token == "tok"
        assert cfg.github.repository == "owner/repo"
        assert cfg.scanner.concurrency == 16
        assert cfg.scanner.timeout == 15

    def test_from_dict_with_empty_dict_uses_defaults(self) -> None:
        cfg = Config.from_dict({})
        assert cfg.github.token == ""
        assert cfg.scanner.concurrency == 8

    def test_from_dict_github_only(self) -> None:
        cfg = Config.from_dict({"github": {"token": "xyz"}})
        assert cfg.github.token == "xyz"
        assert cfg.scanner.concurrency == 8

    def test_from_dict_scanner_only(self) -> None:
        cfg = Config.from_dict({"scanner": {"concurrency": 2}})
        assert cfg.scanner.concurrency == 2
        assert cfg.github.token == ""


class TestConfigDataclasses:
    """Sanity checks on the dataclass defaults."""

    def test_github_config_defaults(self) -> None:
        gh = GitHubConfig()
        assert gh.token == ""
        assert gh.repository == ""
        assert gh.branch == "main"

    def test_scanner_config_defaults(self) -> None:
        sc = ScannerConfig()
        assert sc.concurrency == 8
        assert sc.timeout == 30

    def test_config_default_factory(self) -> None:
        cfg = Config()
        assert isinstance(cfg.github, GitHubConfig)
        assert isinstance(cfg.scanner, ScannerConfig)
