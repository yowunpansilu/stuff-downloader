# PyInstaller spec: GUI-only onedir build of Stuff Downloader for macOS
import importlib.util
import sys
from pathlib import Path
import json

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from PyInstaller.utils.hooks import copy_metadata

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"

with (ROOT / "pyproject.toml").open("rb") as f:
    pyproject_data = tomllib.load(f)
APP_VERSION = pyproject_data.get("project", {}).get("version", "1.2.0")

ENTRY = Path(workpath) / "stuff_downloader_entry.py"
ENTRY.parent.mkdir(parents=True, exist_ok=True)
ENTRY.write_text(
    "import sys\nfrom stuff_downloader.__main__ import main\nsys.exit(main())\n", encoding="utf-8"
)

TOOLS_DIR = ROOT / "tools"
_fetch_spec = importlib.util.spec_from_file_location("fetch_tools", ROOT / "packaging" / "fetch_tools.py")
fetch_tools = importlib.util.module_from_spec(_fetch_spec)
sys.modules["fetch_tools"] = fetch_tools
_fetch_spec.loader.exec_module(fetch_tools)
try:
    # Use load_manifest directly for macos_arm64 to check tools
    SOURCES, STAGED, EXECUTABLES = fetch_tools.load_manifest("macos_arm64")
    # Instead of verify_staged which uses global, we just mock the verify since we know it's mac
    for relative, expected in STAGED.items():
        target = TOOLS_DIR / relative
        if not target.is_file():
            raise fetch_tools.ToolError(f"missing {relative}")
        if fetch_tools.sha256_file(target) != expected:
            raise fetch_tools.ToolError(f"SHA-256 mismatch for {relative}")
except fetch_tools.ToolError as exc:
    raise SystemExit(f"ERROR: {exc}") from None

TOOL_DATAS = [
    (str(TOOLS_DIR / relative), str(Path("tools", relative).parent))
    for relative in STAGED
]

RESOURCES = SRC / "stuff_downloader" / "resources"
ICON = RESOURCES / "app.icns"
APP_DATAS = [
    (str(path), "resources")
    for path in sorted({*RESOURCES.glob("app.*"), *RESOURCES.glob("*.png")})
    if path.is_file()
]
for name in ("LICENSE", "THIRD_PARTY_LICENSES.txt"):
    if not (ROOT / name).is_file():
        raise SystemExit(f"{name} is missing: a build must ship its licence texts")
    APP_DATAS.append((str(ROOT / name), "."))
APP_DATAS += copy_metadata("stuff-downloader")
REQ_INS = sorted((ROOT / "packaging" / "engine-requirements").glob("*.in"))
if not REQ_INS:
    raise SystemExit("packaging/engine-requirements/*.in is missing: the update check needs it")
APP_DATAS += [(str(path), "engine-requirements") for path in REQ_INS]
APP_DATAS.append((str(ROOT / "packaging" / "build_runtime.py"), "runtime-tools"))

ENGINE_EXCLUDES = [
    "stuff_downloader_worker",
    "yt_dlp",
    "yt_dlp_ejs",
    "curl_cffi",
    "gallery_dl",
    "spotdl",
    "ytmusicapi",
    "mutagen",
]

a = Analysis(
    [str(ENTRY)],
    pathex=[str(SRC)],
    binaries=[],
    datas=TOOL_DATAS + APP_DATAS,
    hiddenimports=["stuff_downloader.app"],
    hookspath=[],
    runtime_hooks=[],
    excludes=ENGINE_EXCLUDES + ["tkinter", "pytest", "pytestqt"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="StuffDownloader",
    console=False,
    debug=False,
    strip=False,
    upx=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="StuffDownloader",
)

app = BUNDLE(
    coll,
    name='StuffDownloader.app',
    icon=str(ICON),
    bundle_identifier='com.stuffdownloader.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '13.0',
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
    },
)
