import platform
from pathlib import Path
import pytest

from gitingest.utils.file_utils import get_preferred_encodings, is_text_file

def test_get_preferred_encodings_contains_utf8():
    encodings = get_preferred_encodings()
    assert "utf-8" in encodings
    assert isinstance(encodings, list)
    assert all(isinstance(e, str) for e in encodings)

def test_get_preferred_encodings_windows(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    encodings = get_preferred_encodings()
    assert "cp1252" in encodings
    assert "iso-8859-1" in encodings

def test_is_text_file_with_text(tmp_path):
    file = tmp_path / "text.txt"
    file.write_text("Ceci est un fichier texte.")
    assert is_text_file(file) is True

def test_is_text_file_with_binary(tmp_path):
    file = tmp_path / "bin.bin"
    file.write_bytes(b"\x00\x01\x02\xff")
    assert is_text_file(file) is False

def test_is_text_file_empty(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_bytes(b"")
    assert is_text_file(file) is True

def test_is_text_file_oserror(tmp_path, monkeypatch):
    file = tmp_path / "fail.txt"
    file.write_text("fail")
    def raise_oserror(*a, **kw):
        raise OSError("fail")
    monkeypatch.setattr(Path, "open", raise_oserror)
    assert is_text_file(file) is False

def test_is_text_file_weird_encoding(tmp_path):
    file = tmp_path / "latin.txt"
    # Texte en latin-1 avec caractères accentués
    file.write_bytes("café crème".encode("latin-1"))
    # Doit être détecté comme texte
    assert is_text_file(file) is True 