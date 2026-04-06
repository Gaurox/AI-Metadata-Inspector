#define MyAppName "AI Metadata Inspector"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Gaurox"
#define MyAppURL "https://github.com/Gaurox/AI-Metadata-Inspector"

[Setup]
AppId={{8C19D0A4-0E77-4A76-9D4B-7B7F0F23B123}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf}\AI Metadata Inspector
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

OutputDir=Output
OutputBaseFilename=AI_Metadata_Inspector_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=admin

UninstallDisplayIcon={app}\icons\info.ico
SetupIconFile=icons\info.ico

AllowNoIcons=yes
UsePreviousAppDir=yes

VersionInfoVersion=1.0.0.0
VersionInfoTextVersion=1.0.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\Context_Menu_Tools"
Name: "{app}\ps"

[Files]
; --- Core
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "exif_reader.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "prompt_extractors.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "workflow_parser.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "workflow_utils.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "workflow_resolver.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "workflow_extractors.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "workflow_seed.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "info_builder.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "info_window.py"; DestDir: "{app}"; Flags: ignoreversion

; --- PowerShell GUI
Source: "ps\info_window_helpers.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion
Source: "ps\info_window_layout.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion

; --- Launcher
Source: "run_prompt_tool.vbs"; DestDir: "{app}"; Flags: ignoreversion

; --- Context menu tools
Source: "install_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion

; --- ExifTool
Source: "exiftool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "exiftool_files\*"; DestDir: "{app}\exiftool_files"; Flags: ignoreversion recursesubdirs createallsubdirs

; --- Python portable
Source: "python_embeded\*"; DestDir: "{app}\python_embeded"; Flags: ignoreversion recursesubdirs createallsubdirs

; --- Icons
Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

; --- Docs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; --- Context menu reg tools
Source: "enable_old_context_menu.reg"; DestDir: "{app}\Context_Menu_Tools"; Flags: ignoreversion
Source: "disable_old_context_menu.reg"; DestDir: "{app}\Context_Menu_Tools"; Flags: ignoreversion

[Icons]
Name: "{group}\README"; Filename: "{app}\README.md"
Name: "{group}\LICENSE"; Filename: "{app}\LICENSE"
Name: "{group}\Context Menu Tools"; Filename: "{app}\Context_Menu_Tools"
Name: "{group}\Enable old context menu"; Filename: "{app}\Context_Menu_Tools\enable_old_context_menu.reg"
Name: "{group}\Disable old context menu"; Filename: "{app}\Context_Menu_Tools\disable_old_context_menu.reg"
Name: "{group}\Uninstall AI Metadata Inspector"; Filename: "{uninstallexe}"

[Registry]

; ================= PNG =================

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueData: "AI - Copy positive prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\positive.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" positive"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueData: "AI - Copy negative prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\negative.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" negative"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueData: "AI - Metadata Info"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\info.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" info"; Flags: uninsdeletekey

; ================= MP4 =================

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueData: "AI - Copy positive prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\positive.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" positive"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueData: "AI - Copy negative prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\negative.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" negative"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueData: "AI - Metadata Info"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\info.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" info"; Flags: uninsdeletekey

[Run]
Filename: "{app}\README.md"; Description: "Open README"; Flags: postinstall shellexec skipifsilent