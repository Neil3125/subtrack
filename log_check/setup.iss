[Setup]
AppName=Log Check App
AppVersion=4.1
DefaultDirName={pf}\Log Check App
DefaultGroupName=Log Check App
OutputDir=installer
OutputBaseFilename=LogCheckApp_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=icon.ico

[Tasks]
; Temporarily removed to bypass error

[Files]
Source: "dist\log_check.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "customers.json"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "categories.json"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "qb_coordinates.json"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "log_check.exe.manifest"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\Log Check App"; Filename: "{app}\log_check.exe"; IconFilename: "{app}\icon.ico"
; Desktop shortcut (now always created)
Name: "{autodesktop}\Log Check App"; Filename: "{app}\log_check.exe"; IconFilename: "{app}\icon.ico"

[Run]
; No tasks or commands to run after installation

[Registry]
; Add manifest information to ensure app always runs as administrator
Root: HKLM; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: string; ValueName: "{app}\log_check.exe"; ValueData: "RUNASADMIN"; Flags: createvalueifdoesntexist