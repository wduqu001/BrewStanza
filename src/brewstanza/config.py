"""
Configuration module for BrewStanza.

This module defines the configuration schema used by BrewStanza, which is loaded
from a TOML file. The default location for the configuration file is
`~/.config/brewstanza/config.toml`.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class GitHubConfig:
    """
    GitHub synchronization configuration.

    Attributes:
        token (str): The Personal Access Token (PAT) used to authenticate with GitHub.
        repository (str): The target repository in the format 'owner/repo'.
        branch (str): The branch to push the snapshots to. Defaults to 'main'.
    """

    token: str = ""
    repository: str = ""
    branch: str = "main"


@dataclass
class ScannerConfig:
    """
    Disk scanning behaviour configuration.

    Attributes:
        concurrency (int): The number of concurrent disk scanning operations to perform.
            Defaults to 8.
        timeout (int): The maximum number of seconds to wait for a single directory
            scan before timing out. Defaults to 30.
    """

    concurrency: int = 8
    timeout: int = 30


@dataclass
class Config:
    """
    Root configuration object containing all settings for BrewStanza.

    Attributes:
        github (GitHubConfig): Settings related to GitHub synchronization.
        scanner (ScannerConfig): Settings related to the disk scanning behaviour.
    """

    github: GitHubConfig = field(default_factory=GitHubConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """
        Load the configuration from the given TOML file path.

        If no path is provided, it defaults to `~/.config/brewstanza/config.toml`.
        If the configuration file does not exist, an empty default configuration
        will be returned.

        Args:
            config_path (Path | None, optional): The path to the configuration file.
                Defaults to None.

        Returns:
            Config: The instantiated configuration object.
        """
        if config_path is None:
            config_path = Path.home() / ".config" / "brewstanza" / "config.toml"

        if not config_path.exists():
            return cls()

        with config_path.open("rb") as f:
            data = tomllib.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create a Config object from a parsed dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing configuration data.

        Returns:
            Config: The instantiated configuration object.
        """
        github_data = data.get("github", {})
        scanner_data = data.get("scanner", {})

        return cls(github=GitHubConfig(**github_data), scanner=ScannerConfig(**scanner_data))
