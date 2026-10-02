from pathlib import Path
from importlib.metadata import distribution
import sys
import tomllib
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct, VSVersionInfo,
)

root = Path(SPECPATH).parent
assets = root / "src" / "tibiaenhanced"
app_version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
version_numbers = tuple(int(part) for part in app_version.split(".")) + (0,)
version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=version_numbers, prodvers=version_numbers, mask=0x3f,
                      flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
    kids=[StringFileInfo([StringTable("040904B0", [
        StringStruct("CompanyName", "Caio Mascarenhas"),
        StringStruct("FileDescription", "Tibia Enhanced"),
        StringStruct("FileVersion", app_version),
        StringStruct("InternalName", "TibiaEnhanced"),
        StringStruct("OriginalFilename", "TibiaEnhanced.exe"),
        StringStruct("ProductName", "Tibia Enhanced"),
        StringStruct("ProductVersion", app_version),
    ])]), VarFileInfo([VarStruct("Translation", [1033, 1200])])],
)
datas = []
for directory in ("audios", "imgs", "fonts", "icons"):
    for path in (assets / directory).rglob("*"):
        if path.is_file():
            datas.append((str(path), str(Path("tibiaenhanced") / path.parent.relative_to(assets))))
datas.append((str(root / "packaging" / "README-windows.txt"), "."))
for package in ("PySide6", "PySide6_Essentials", "PySide6_Addons", "shiboken6", "mss"):
    package_info = distribution(package)
    for file in package_info.files or []:
        if "licenses" in file.parts or file.name.startswith("LICENSE"):
            path = package_info.locate_file(file)
            if path.is_file():
                datas.append((str(path), str(Path("licenses") / package / file.parent)))
python_license = Path(sys.base_prefix) / "LICENSE.txt"
if python_license.is_file():
    datas.append((str(python_license), "licenses/Python"))

a = Analysis(
    [str(root / "packaging" / "windows_entry.py")],
    pathex=[str(root / "src")],
    binaries=[], datas=datas, hiddenimports=[], hookspath=[], runtime_hooks=[],
    excludes=["pytest", "unittest", "segno", "zxingcpp", "PIL", "pip"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="TibiaEnhanced", console=False, debug=False, strip=False, upx=False,
    icon=str(root / "build" / "TibiaEnhanced.ico"),
    version=version_info,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="TibiaEnhanced")
