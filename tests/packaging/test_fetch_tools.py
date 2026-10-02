import json
import tempfile
from pathlib import Path

import pytest

import importlib.util
import sys
from pathlib import Path

# Load fetch_tools dynamically since 'packaging' conflicts with pip package
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fetch_tools", ROOT / "packaging" / "fetch_tools.py")
fetch_tools = importlib.util.module_from_spec(spec)
sys.modules["fetch_tools"] = fetch_tools
spec.loader.exec_module(fetch_tools)

from fetch_tools import Source, ToolError, load_manifest, _stage_path, sha256_file

def test_load_manifest_valid():
    sources, staged, executables = load_manifest("macos_arm64")
    assert len(sources) > 0
    assert len(staged) > 0
    assert "ffmpeg" in executables or "ffmpeg.exe" in executables

def test_load_manifest_invalid_platform():
    with pytest.raises(ToolError, match="Unknown platform: invalid"):
        load_manifest("invalid")

def test_stage_path():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = _stage_path(root, "sub/dir/file.txt")
        assert target.is_relative_to(root.resolve())
        
        with pytest.raises(ToolError, match="escapes"):
            _stage_path(root, "../outside.txt")

def test_sha256_file():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "test.txt"
        p.write_bytes(b"hello world")
        # echo -n "hello world" | shasum -a 256
        assert sha256_file(p) == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
