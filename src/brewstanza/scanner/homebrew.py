"""
Homebrew Scanner Module - Scan and analyze Homebrew packages.
"""

import json
import subprocess
from pathlib import Path
from typing import Any


class HomebrewScanner:
    """Scanner for Homebrew packages (formulae and casks)."""

    def __init__(self) -> None:
        self._cellar_base: Path | None = None

    def _run_brew_command(self, args: list[str]) -> str:
        """
        Execute a brew command and return output.

        Args:
            args: List of brew command arguments

        Returns:
            Command stdout as string

        Raises:
            RuntimeError: If command fails
        """
        try:
            result = subprocess.run(
                ["brew", *args],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Homebrew command failed: brew {' '.join(args)}\n{e.stderr}") from e

    def list_formulae(self) -> list[str]:
        """
        List all installed formulae.

        Returns:
            List of formula names
        """
        output = self._run_brew_command(["list", "--formula"])
        if not output:
            return []
        return output.splitlines()

    def list_casks(self) -> list[str]:
        """
        List all installed casks.

        Returns:
            List of cask names
        """
        output = self._run_brew_command(["list", "--cask"])
        if not output:
            return []
        return output.splitlines()

    def get_info(self, name: str) -> dict[str, Any]:
        """
        Get detailed information about a package.

        Args:
            name: Package name (formula or cask)

        Returns:
            Dictionary with parsed JSON info from brew info --json=v2
        """
        output = self._run_brew_command(["info", "--json=v2", name])
        return json.loads(output)  # type: ignore

    def get_outdated(self) -> list[str]:
        """
        List outdated packages.

        Returns:
            List of outdated package names
        """
        output = self._run_brew_command(["outdated", "--quiet"])
        if not output:
            return []
        return output.splitlines()

    def get_cellar_path(self, name: str) -> Path | None:
        """
        Get the cellar path for a given formula.

        Args:
            name: Formula name

        Returns:
            Path to cellar or None if not found/not applicable
        """
        try:
            info = self.get_info(name)
        except RuntimeError:
            return None

        formulae = info.get("formulae", [])
        if not formulae:
            return None

        f = formulae[0]
        installed = f.get("installed", [])
        if not installed:
            return None

        version_raw = f.get("linked_keg") or installed[0].get("version")
        if not version_raw:
            return None
            
        version = str(version_raw)

        if self._cellar_base is None:
            self._cellar_base = Path(self._run_brew_command(["--cellar"]))

        return self._cellar_base / name / version
