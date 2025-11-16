[Setup]
AppName=Weather App
AppVersion=1.0
DefaultDirName={pf}\WeatherApp
DefaultGroupName=Weather App
OutputDir=.
OutputBaseFilename=WeatherAppInstaller
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico
LicenseFile=LICENSE.txt
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\weather_processor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Icons]
Name: "{group}\Weather App"; Filename: "{app}\weather_processor.exe"
Name: "{commondesktop}\Weather App"; Filename: "{app}\weather_processor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\weather_processor.exe"; Description: "Launch Weather App"; Flags: nowait postinstall

