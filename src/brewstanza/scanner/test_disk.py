"""
Tests for BrewStanza disk scanner.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from brewstanza.scanner.disk import ScanResult, ScanSummary, _du, scan_paths, scan_paths_async


@pytest.fixture
def mock_semaphore() -> asyncio.Semaphore:
    return asyncio.Semaphore(1)


@patch("asyncio.create_subprocess_exec")
def test_du_happy_path(mock_create_subprocess_exec: AsyncMock) -> None:
    async def run_test() -> None:
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"1024\t/some/path\n", b"")
        mock_create_subprocess_exec.return_value = mock_proc

        path = Path("/some/path")
        result = await _du(path, asyncio.Semaphore(1))

        assert result.path == path
        assert result.size_bytes == 1024 * 1024  # kb to bytes
        assert result.error == ""

    asyncio.run(run_test())


@patch("asyncio.create_subprocess_exec")
def test_du_error_path(mock_create_subprocess_exec: AsyncMock) -> None:
    async def run_test() -> None:
        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate.return_value = (b"", b"permission denied")
        mock_create_subprocess_exec.return_value = mock_proc

        path = Path("/some/path")
        result = await _du(path, asyncio.Semaphore(1))

        assert result.path == path
        assert result.error == "du exited 1"

    asyncio.run(run_test())


@patch("asyncio.wait_for")
@patch("asyncio.create_subprocess_exec")
def test_du_timeout_path(
    mock_create_subprocess_exec: AsyncMock,
    mock_wait_for: MagicMock,
) -> None:
    async def run_test() -> None:
        def fake_wait_for(coro, timeout):
            coro.close()
            raise asyncio.TimeoutError()

        mock_wait_for.side_effect = fake_wait_for

        mock_proc = AsyncMock()
        mock_proc.kill = MagicMock()
        mock_create_subprocess_exec.return_value = mock_proc

        path = Path("/some/path")
        result = await _du(path, asyncio.Semaphore(1))

        assert result.path == path
        assert result.error == "timeout"
        mock_proc.kill.assert_called_once()

    asyncio.run(run_test())


@patch("brewstanza.scanner.disk._du")
def test_scan_paths_async(mock_du: AsyncMock) -> None:
    async def run_test() -> None:
        mock_du.side_effect = [
            ScanResult(path=Path("/app1"), size_bytes=100),
            ScanResult(path=Path("/app2"), error="failed"),
        ]

        summary = await scan_paths_async([Path("/app1"), Path("/app2")])
        assert len(summary.results) == 1
        assert len(summary.failed_paths) == 1
        assert summary.results[0].size_bytes == 100

    asyncio.run(run_test())


@patch("brewstanza.scanner.disk._du")
def test_scan_paths_sync(mock_du: AsyncMock) -> None:
    mock_du.side_effect = [
        ScanResult(path=Path("/app1"), size_bytes=100),
    ]

    summary = scan_paths([Path("/app1")])
    assert isinstance(summary, ScanSummary)
    assert len(summary.results) == 1
