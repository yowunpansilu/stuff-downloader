import subprocess
import shutil
from pathlib import Path
import sys

import tomllib

ROOT = Path(__file__).resolve().parents[2]

def run(cmd, **kwargs):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True, **kwargs)

def main():
    # 1. Fetch macOS tools
    run([sys.executable, "packaging/fetch_tools.py", "--platform", "macos_arm64", "--dest", "tools", "fetch"])

    # 2. Convert PNG to ICNS
    app_png = ROOT / "src" / "stuff_downloader" / "resources" / "app.png"
    app_icns = ROOT / "src" / "stuff_downloader" / "resources" / "app.icns"
    run(["sips", "-s", "format", "icns", str(app_png), "--out", str(app_icns)])

    # 3. Build .app with PyInstaller
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "packaging/StuffDownloader_mac.spec"])

    # 4. Ad-hoc sign
    app_path = ROOT / "dist" / "StuffDownloader.app"
    run(["find", str(app_path), "-name", "._*", "-delete"])
    run(["find", str(app_path), "-name", ".DS_Store", "-delete"])
    subprocess.run(["xattr", "-rsd", "com.apple.FinderInfo", str(app_path)], cwd=ROOT)
    subprocess.run(["xattr", "-rsd", "com.apple.ResourceFork", str(app_path)], cwd=ROOT)
    run(["codesign", "--force", "--deep", "--no-strict", "-s", "-", str(app_path)])

    # 5. Create DMG
    with (ROOT / "pyproject.toml").open("rb") as f:
        pyproject_data = tomllib.load(f)
    version = pyproject_data.get("project", {}).get("version", "1.2.0")
    
    dmg_name = f"StuffDownloader-{version}-macos-arm64.dmg"
    dmg_path = ROOT / "dist" / dmg_name
    
    if dmg_path.exists():
        dmg_path.unlink()

    run([
        "hdiutil", "create", "-volname", "Stuff Downloader",
        "-srcfolder", str(app_path),
        "-ov", "-format", "UDZO",
        str(dmg_path)
    ])

    import hashlib
    digest = hashlib.sha256()
    with dmg_path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            digest.update(chunk)
    
    print(f"DMG Created: {dmg_path}")
    print(f"SHA-256: {digest.hexdigest()}")

if __name__ == "__main__":
    main()
