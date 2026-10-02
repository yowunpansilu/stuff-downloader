import subprocess
from unittest.mock import patch, MagicMock

import pytest

import importlib.util
import sys
from pathlib import Path

# Load build_dmg dynamically since 'packaging' conflicts with pip package
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_dmg", ROOT / "packaging" / "macos" / "build_dmg.py")
build_dmg = importlib.util.module_from_spec(spec)
sys.modules["build_dmg"] = build_dmg
spec.loader.exec_module(build_dmg)

def test_dmg_version_parsing(tmp_path, monkeypatch):
    # Mock ROOT to a tmp dir
    monkeypatch.setattr(build_dmg, "ROOT", tmp_path)
    
    # Create mock pyproject.toml
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "9.9.9"\n')
    
    # Mock run and subprocess.run
    mock_run = MagicMock()
    monkeypatch.setattr(build_dmg, "run", mock_run)
    monkeypatch.setattr(subprocess, "run", MagicMock())
    
    # Run main, it will fail at DMG hash because file doesn't exist, we just want to ensure it passes all steps before that
    with pytest.raises(FileNotFoundError):
        build_dmg.main()
        
    # Check that hdiutil create was called with correct dmg name
    hdiutil_call = None
    for call in mock_run.call_args_list:
        cmd = call[0][0]
        if cmd[0] == "hdiutil":
            hdiutil_call = cmd
            break
            
    assert hdiutil_call is not None
    assert str(tmp_path / "dist" / "StuffDownloader-9.9.9-macos-arm64.dmg") in hdiutil_call
