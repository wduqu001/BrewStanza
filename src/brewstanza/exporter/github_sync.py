"""
GitHub Sync Module — commit and push export files to a GitHub repository.

Uses subprocess git over HTTPS with a PAT-embedded remote URL.
Requires git to be installed on the host machine and the target
repository to exist on GitHub (it does NOT need to be cloned locally;
a fresh clone is performed into a temporary directory on each run).
"""

import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from brewstanza.config import Config


class GitHubSyncError(Exception):
    """Raised when a sync operation cannot be completed."""


class GitHubSync:
    """
    Commits one or more export files to a GitHub repository via local git.

    The caller is responsible for loading a :class:`~brewstanza.config.Config`
    and passing it here.  A :class:`GitHubSyncError` is raised for any
    recoverable configuration or git error; unrecoverable OS errors are
    allowed to propagate.
    """

    GITHUB_TOKEN_SETTINGS = "https://github.com/settings/tokens"

    def __init__(self, config: Config) -> None:
        self._config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync(
        self,
        files: dict[str, str],
        dry_run: bool = False,
    ) -> str:
        """
        Export one or more files to the configured GitHub repository.

        Each key in *files* is the destination filename inside the repo
        (e.g. ``"Brewfile"`` or ``"brewstanza-snapshot.json"``); the value
        is the file contents as a string.

        Args:
            files: Mapping of ``{filename: content}`` to commit.
            dry_run: If True, print what would happen without executing
                any git commands.

        Returns:
            A human-readable summary of what was committed (or would be).

        Raises:
            GitHubSyncError: If config is invalid or a git command fails.
        """
        self._validate_config()

        commit_msg = f"BrewStanza sync — {datetime.now().isoformat(timespec='seconds')}"
        repo = self._config.github.repository
        branch = self._config.github.branch
        token = self._config.github.token

        filenames = ", ".join(files.keys())
        summary = (
            f"Commit: {commit_msg!r}\n"
            f"Repo:   {repo}  (branch: {branch})\n"
            f"Files:  {filenames}"
        )

        if dry_run:
            return f"[DRY RUN] Would push the following:\n{summary}"

        remote_url = f"https://{token}@github.com/{repo}.git"

        with tempfile.TemporaryDirectory(prefix="brewstanza_sync_") as tmpdir:
            work_dir = Path(tmpdir)
            self._git(["clone", "--depth=1", "--branch", branch, remote_url, str(work_dir)])

            for filename, content in files.items():
                dest = work_dir / filename
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
                self._git(["add", filename], cwd=work_dir)

            self._git(
                ["commit", "--allow-empty", "-m", commit_msg],
                cwd=work_dir,
            )
            self._git(["push", "origin", branch], cwd=work_dir)

        return f"✓ Synced to {repo}:{branch}\n{summary}"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_config(self) -> None:
        """Raise GitHubSyncError if the GitHub config is incomplete."""
        gh = self._config.github
        if not gh.token:
            raise GitHubSyncError(
                "GitHub Personal Access Token (PAT) is not set.\n"
                f"Add it to ~/.config/brewstanza/config.toml or visit:\n"
                f"  {self.GITHUB_TOKEN_SETTINGS}"
            )
        if not gh.repository:
            raise GitHubSyncError(
                "GitHub repository is not configured.\n"
                "Add [github] repository = \"owner/repo\" to "
                "~/.config/brewstanza/config.toml"
            )

    def _git(self, args: list[str], cwd: Path | None = None) -> str:
        """
        Run a git sub-command and return stdout.

        Args:
            args: git arguments (without the leading ``"git"``).
            cwd: Working directory.  Defaults to the current directory.

        Returns:
            stdout as a stripped string.

        Raises:
            GitHubSyncError: If git exits with a non-zero status.
        """
        cmd = ["git", *args]
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                cwd=cwd,
            )
            return result.stdout.strip()
        except FileNotFoundError as exc:
            raise GitHubSyncError(
                "git is not installed or not on PATH.\n"
                "Install it with: brew install git"
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip()
            # Surface a friendlier message for auth failures
            if "authentication" in stderr.lower() or "403" in stderr or "401" in stderr:
                raise GitHubSyncError(
                    "GitHub authentication failed. Your PAT may be expired or lack "
                    "'repo' scope.\n"
                    f"Generate a new token at: {self.GITHUB_TOKEN_SETTINGS}\n"
                    f"git said: {stderr}"
                ) from exc
            raise GitHubSyncError(
                f"git {' '.join(args)} failed:\n{stderr}"
            ) from exc
