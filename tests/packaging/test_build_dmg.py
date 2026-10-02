import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Load build_dmg dynamically since 'packaging' conflicts with pip package
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "build_dmg", ROOT / "packaging" / "macos" / "build_dmg.py"
)
build_dmg = importlib.util.module_from_spec(spec)
sys.modules["build_dmg"] = build_dmg
spec.loader.exec_module(build_dmg)


def test_dmg_version_parsing(tmp_path, monkeypatch):
    # Mock ROOT to a tmp dir
    monkeypatch.setattr(build_dmg, "ROOT", tmp_path)

    # Create mock pyproject.toml
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "9.9.9"\n')

    # Mock run and subprocess.run and shutil.copytree
    mock_run = MagicMock()
    monkeypatch.setattr(build_dmg, "run", mock_run)
    monkeypatch.setattr(subprocess, "run", MagicMock())
    monkeypatch.setattr(build_dmg.shutil, "copytree", MagicMock())

    # Run main; fails at DMG hash because file doesn't exist
    with pytest.raises(FileNotFoundError):
        build_dmg.main()

    # Check that hdiutil create was called with the correct dmg name
    hdiutil_call = None
    for call in mock_run.call_args_list:
        cmd = call[0][0]
        if cmd[0] == "hdiutil":
            hdiutil_call = cmd
            break

    assert hdiutil_call is not None
    import platform
    arch = platform.machine()
    assert str(tmp_path / "dist" / f"StuffDownloader-9.9.9-macos-{arch}.dmg") in hdiutil_call
