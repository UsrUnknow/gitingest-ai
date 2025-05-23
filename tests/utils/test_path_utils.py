import os
import platform
import tempfile
from pathlib import Path
import pytest

from gitingest.utils.path_utils import _is_safe_symlink

@pytest.mark.skipif(platform.system() == "Windows", reason="Symlink tests are not reliable on Windows CI")
def test_is_safe_symlink_valid(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    target = base / "target.txt"
    target.write_text("ok")
    symlink = base / "link"
    symlink.symlink_to(target)
    assert _is_safe_symlink(symlink, base) is True

@pytest.mark.skipif(platform.system() == "Windows", reason="Symlink tests are not reliable on Windows CI")
def test_is_safe_symlink_outside(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("nope")
    symlink = base / "link"
    symlink.symlink_to(outside)
    assert _is_safe_symlink(symlink, base) is False

@pytest.mark.skipif(platform.system() == "Windows", reason="Symlink tests are not reliable on Windows CI")
def test_is_safe_symlink_broken(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    broken = base / "doesnotexist.txt"
    symlink = base / "link"
    symlink.symlink_to(broken)
    assert _is_safe_symlink(symlink, base) is False

def test_is_safe_symlink_not_a_symlink(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    file = base / "file.txt"
    file.write_text("plain")
    # On Unix, _is_safe_symlink ne vérifie pas islink, donc il va resolve() le fichier
    # et vérifier qu'il est bien dans base
    assert _is_safe_symlink(file, base) is True

def test_is_safe_symlink_exception(monkeypatch, tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    file = base / "file.txt"
    file.write_text("plain")
    # Simule une exception sur resolve
    class DummyPath(Path):
        def resolve(self):
            raise OSError("fail")
    dummy = DummyPath(str(file))
    assert _is_safe_symlink(dummy, base) is False 