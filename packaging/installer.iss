; A versão é gerada por tools/build_windows.py a partir de pyproject.toml.
#include "..\build\windows-version.iss"
#define AppName "Tibia Enhanced"

[Setup]
AppId={{794F32CF-D26D-4E37-A80C-A499CE8A01C8}
AppName={#AppName}
AppVersion={#AppVersion}
VersionInfoVersion={#AppNumericVersion}
AppPublisher=Caio Mascarenhas
DefaultDirName={localappdata}\Programs\{#AppName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041
SetupIconFile=..\build\TibiaEnhanced.ico
UninstallDisplayIcon={app}\TibiaEnhanced.exe
OutputDir=..\dist
OutputBaseFilename=TibiaEnhanced-{#AppVersion}-windows-x64-setup
Compression=lzma2
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Files]
Source: "..\dist\TibiaEnhanced\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\TibiaEnhanced.exe"; IconFilename: "{app}\TibiaEnhanced.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\TibiaEnhanced.exe"; IconFilename: "{app}\TibiaEnhanced.exe"; Tasks: desktopicon
