import asyncio
import sys
import pytest
from unittest.mock import patch, AsyncMock

import gitingest.utils.git_utils as git_utils

@pytest.mark.asyncio
async def test_run_command_success():
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"ok", b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc
        out, err = await git_utils.run_command("echo", "ok")
        assert out == b"ok"
        assert err == b""

@pytest.mark.asyncio
async def test_run_command_failure():
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"fail")
        mock_proc.returncode = 1
        mock_exec.return_value = mock_proc
        with pytest.raises(RuntimeError, match="Command failed"):
            await git_utils.run_command("fail")

@pytest.mark.asyncio
async def test_ensure_git_installed_success():
    with patch.object(git_utils, "run_command", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = (b"git version 2.0", b"")
        await git_utils.ensure_git_installed()
        mock_run.assert_awaited_with("git", "--version")

@pytest.mark.asyncio
async def test_ensure_git_installed_failure():
    with patch.object(git_utils, "run_command", new_callable=AsyncMock) as mock_run:
        mock_run.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError, match="Git is not installed"):
            await git_utils.ensure_git_installed()

@pytest.mark.asyncio
@pytest.mark.parametrize("status,expected", [
    (b"HTTP/1.1 200 OK\n", True),
    (b"HTTP/1.1 301 Moved Permanently\n", True),
    (b"HTTP/1.1 302 Found\n", False),
    (b"HTTP/1.1 404 Not Found\n", False),
])
async def test_check_repo_exists_status(status, expected):
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (status, b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc
        result = await git_utils.check_repo_exists("https://repo")
        assert result is expected

@pytest.mark.asyncio
async def test_check_repo_exists_curl_error():
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"fail")
        mock_proc.returncode = 1
        mock_exec.return_value = mock_proc
        result = await git_utils.check_repo_exists("https://repo")
        assert result is False

@pytest.mark.asyncio
async def test_check_repo_exists_unexpected_status():
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"HTTP/1.1 500 Internal Server Error\n", b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc
        with pytest.raises(RuntimeError, match="Unexpected status line"):
            await git_utils.check_repo_exists("https://repo")

@pytest.mark.asyncio
async def test_fetch_remote_branch_list_success():
    with patch.object(git_utils, "ensure_git_installed", new_callable=AsyncMock) as mock_ensure:
        with patch.object(git_utils, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (b"abc123\trefs/heads/main\ndef456\trefs/heads/dev\n", b"")
            branches = await git_utils.fetch_remote_branch_list("https://repo")
            assert set(branches) == {"main", "dev"}

@pytest.mark.asyncio
async def test_fetch_remote_branch_list_empty():
    with patch.object(git_utils, "ensure_git_installed", new_callable=AsyncMock) as mock_ensure:
        with patch.object(git_utils, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (b"", b"")
            branches = await git_utils.fetch_remote_branch_list("https://repo")
            assert branches == []

@pytest.mark.asyncio
async def test_fetch_remote_branch_list_error():
    with patch.object(git_utils, "ensure_git_installed", new_callable=AsyncMock) as mock_ensure:
        with patch.object(git_utils, "run_command", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = RuntimeError("fail")
            with pytest.raises(RuntimeError):
                await git_utils.fetch_remote_branch_list("https://repo") 