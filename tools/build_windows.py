"""Build Windows x64 em pasta, com ícone multirresolução e manifesto local."""

import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import platform
import subprocess
import struct
import sys
import zipfile

from PIL import Image
import pefile

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if sys.platform != "win32" or platform.machine().upper() not in ("AMD64", "X86_64"):
        raise SystemExit("Execute o build no Windows x64.")
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    with Image.open(ROOT / "src" / "tibiaenhanced" / "imgs" / "iconapp_no_bg.png") as image:
        image.save(build / "TibiaEnhanced.ico", format="ICO",
                   sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(ROOT / "dist"), "--workpath", str(build / "pyinstaller"),
                    str(ROOT / "packaging" / "TibiaEnhanced.spec")], cwd=ROOT, check=True)
    bundle = ROOT / "dist" / "TibiaEnhanced"
    exe = bundle / "TibiaEnhanced.exe"
    pe = pefile.PE(str(exe))
    assert pe.FILE_HEADER.Machine == 0x8664, "O executável não é x64"
    assert pe.OPTIONAL_HEADER.Subsystem == 2, "O executável abriu com console"
    resource_types = {entry.id for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries}
    assert 3 in resource_types and 14 in resource_types, "Ícone ausente no executável"
    icon_resources = next(entry for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries if entry.id == 3)
    embedded_icons = set()
    for entry in icon_resources.directory.entries:
        resource = entry.directory.entries[0].data.struct
        embedded_icons.add(pe.get_data(resource.OffsetToData, resource.Size))
    ico = (build / "TibiaEnhanced.ico").read_bytes()
    count = struct.unpack_from("<H", ico, 4)[0]
    source_icons = set()
    icon_sizes = []
    for index in range(count):
        width, height, _, _, _, _, size, offset = struct.unpack_from("<BBBBHHII", ico, 6 + 16 * index)
        source_icons.add(ico[offset:offset + size])
        icon_sizes.append([width or 256, height or 256])
    assert embedded_icons == source_icons, "O ícone do executável não corresponde ao ícone do app"
    pe.close()
    packages = {name: version(name) for name in
                ("PyInstaller", "pyinstaller-hooks-contrib", "PySide6", "mss", "Pillow", "pefile")}
    files = [path for path in bundle.rglob("*") if path.is_file()]
    forbidden = {".git", ".venv", ".venv-build", ".vscode", "tests", "tools"}
    assert not any(forbidden.intersection(path.relative_to(bundle).parts) for path in files)
    assert not any(path.name == "profiles.json" or path.name.startswith(".env") for path in files)
    manifest = {
        "python": platform.python_version(), "architecture": platform.machine(),
        "packages": packages, "icon_sizes": icon_sizes, "files": len(files),
        "bytes": sum(path.stat().st_size for path in files),
        "sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_dirty": bool(subprocess.check_output(["git", "diff", "HEAD", "--name-only"],
                                                           cwd=ROOT, text=True).strip()),
    }
    (build / "windows-build.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    archive = ROOT / "dist" / "TibiaEnhanced-windows-x64-test.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for path in files:
            zip_file.write(path, path.relative_to(bundle.parent))
    print(json.dumps({"executable": str(exe), "zip": str(archive), **manifest}, indent=2))


if __name__ == "__main__":
    main()
