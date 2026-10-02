; Preparado para Inno Setup. O primeiro artefato validado é o ZIP portátil.
#define AppName "Tibia Enhanced"
#define AppVersion "0.1.0"

[Setup]
AppId={{794F32CF-D26D-4E37-A80C-A499CE8A01C8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Caio Mascarenhas
DefaultDirName={localappdata}\Programs\{#AppName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041
SetupIconFile=..\build\TibiaEnhanced.ico
UninstallDisplayIcon={app}\TibiaEnhanced.exe
OutputDir=..\dist
OutputBaseFilename=TibiaEnhanced-setup-test
Compression=lzma2
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Files]
Source: "..\dist\TibiaEnhanced\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\TibiaEnhanced.exe"; IconFilename: "{app}\TibiaEnhanced.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\TibiaEnhanced.exe"; IconFilename: "{app}\TibiaEnhanced.exe"; Tasks: desktopicon
