#define MyAppName "AI Metadata Inspector"
#define MyAppVersion "1.3.3"
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

UninstallDisplayIcon={app}\icons\app.ico
SetupIconFile=icons\app.ico

AllowNoIcons=yes
UsePreviousAppDir=yes

VersionInfoVersion=1.3.3.0
VersionInfoTextVersion=1.3.3

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\Context_Menu_Tools"
Name: "{app}\ps"
Name: "{localappdata}\AI Metadata Inspector"

[Files]
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
Source: "info_window_py.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "windows_runtime.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "frame_extractor.py"; DestDir: "{app}"; Flags: ignoreversion

Source: "ps\info_window_helpers.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion
Source: "ps\info_window_layout.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion
Source: "ps\info_window_launcher.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion
Source: "ps\frame_extract_window.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion

Source: "run_prompt_tool.vbs"; DestDir: "{app}"; Flags: ignoreversion

Source: "install_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion

Source: "exiftool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "exiftool_files\*"; DestDir: "{app}\exiftool_files"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "python_embeded\*"; DestDir: "{app}\python_embeded"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "screenshots\*"; DestDir: "{app}\screenshots"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "SECURITY.md"; DestDir: "{app}"; Flags: ignoreversion

Source: "enable_old_context_menu.reg"; DestDir: "{app}\Context_Menu_Tools"; Flags: ignoreversion
Source: "disable_old_context_menu.reg"; DestDir: "{app}\Context_Menu_Tools"; Flags: ignoreversion

[Icons]
Name: "{group}\README"; Filename: "{app}\README.md"
Name: "{group}\LICENSE"; Filename: "{app}\LICENSE"
Name: "{group}\Context Menu Tools"; Filename: "{app}\Context_Menu_Tools"
Name: "{group}\Enable old context menu"; Filename: "{app}\Context_Menu_Tools\enable_old_context_menu.reg"
Name: "{group}\Disable old context menu"; Filename: "{app}\Context_Menu_Tools\disable_old_context_menu.reg"
Name: "{group}\Uninstall AI Metadata Inspector"; Filename: "{uninstallexe}"

[UninstallDelete]
Type: files; Name: "{localappdata}\AI Metadata Inspector\config.json"
Type: files; Name: "{localappdata}\AI Metadata Inspector\logs\prompt_tool_debug.log"
Type: files; Name: "{localappdata}\AI Metadata Inspector\logs\prompt_tool_debug.log.1"
Type: files; Name: "{localappdata}\AI Metadata Inspector\logs\ai_info_error.log"
Type: files; Name: "{localappdata}\AI Metadata Inspector\temp\*"
Type: dirifempty; Name: "{localappdata}\AI Metadata Inspector\logs"
Type: dirifempty; Name: "{localappdata}\AI Metadata Inspector\temp"
Type: dirifempty; Name: "{localappdata}\AI Metadata Inspector"

[Registry]
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueData: "AI - Copy positive prompt"; Flags: uninsdeletekey; Check: ShouldInstallPositivePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\positive.ico"; Flags: uninsdeletevalue; Check: ShouldInstallPositivePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" positive"; Flags: uninsdeletekey; Check: ShouldInstallPositivePrompt

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueData: "AI - Copy negative prompt"; Flags: uninsdeletekey; Check: ShouldInstallNegativePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\negative.ico"; Flags: uninsdeletevalue; Check: ShouldInstallNegativePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" negative"; Flags: uninsdeletekey; Check: ShouldInstallNegativePrompt

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueData: "AI - Ai Info"; Flags: uninsdeletekey; Check: ShouldInstallAIInfo
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\app.ico"; Flags: uninsdeletevalue; Check: ShouldInstallAIInfo
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" info"; Flags: uninsdeletekey; Check: ShouldInstallAIInfo

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueData: "AI - Copy positive prompt"; Flags: uninsdeletekey; Check: ShouldInstallPositivePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\positive.ico"; Flags: uninsdeletevalue; Check: ShouldInstallPositivePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" positive"; Flags: uninsdeletekey; Check: ShouldInstallPositivePrompt

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueData: "AI - Copy negative prompt"; Flags: uninsdeletekey; Check: ShouldInstallNegativePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\negative.ico"; Flags: uninsdeletevalue; Check: ShouldInstallNegativePrompt
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" negative"; Flags: uninsdeletekey; Check: ShouldInstallNegativePrompt

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueData: "AI - Ai Info"; Flags: uninsdeletekey; Check: ShouldInstallAIInfo
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\app.ico"; Flags: uninsdeletevalue; Check: ShouldInstallAIInfo
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" info"; Flags: uninsdeletekey; Check: ShouldInstallAIInfo

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames"; ValueType: string; ValueData: "AI - Extract Frames"; Flags: uninsdeletekey; Check: ShouldInstallExtractFrames
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\extract.ico"; Flags: uninsdeletevalue; Check: ShouldInstallExtractFrames
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames\command"; ValueType: string; ValueData: """{sys}\wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" extract_frames"; Flags: uninsdeletekey; Check: ShouldInstallExtractFrames

[Code]
const
  CurrentAppVersion = '{#MyAppVersion}';
  UninstallRegistryKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8C19D0A4-0E77-4A76-9D4B-7B7F0F23B123}_is1';

var
  MaintenancePage: TWizardPage;
  RadioMaintenanceUpdate: TRadioButton;
  RadioMaintenanceModify: TRadioButton;
  RadioMaintenanceUninstall: TRadioButton;

  ContextMenuPage: TWizardPage;
  CheckPositivePrompt: TNewCheckBox;
  CheckNegativePrompt: TNewCheckBox;
  CheckAIInfo: TNewCheckBox;
  CheckExtractFrames: TNewCheckBox;

  FrameExtractionPage: TWizardPage;
  RadioNextToVideo: TRadioButton;
  RadioFixedFolder: TRadioButton;
  FixedFolderLabel: TNewStaticText;
  FixedFolderEdit: TNewEdit;
  FixedFolderBrowseButton: TNewButton;
  FixedFolderBehaviorLabel: TNewStaticText;
  FixedFolderBehaviorPanel: TPanel;
  RadioFixedFolderSubfolder: TRadioButton;
  RadioFixedFolderShared: TRadioButton;

  InstalledVersion: string;
  InstalledUninstallString: string;
  InstalledAppDir: string;
  HasInstalledVersion: Boolean;
  InstalledVersionIsOlder: Boolean;
  SkipSetupExitConfirmation: Boolean;

function EscapeJson(const S: string): string;
var
  T: string;
begin
  T := S;
  StringChangeEx(T, '\', '\\', True);
  StringChangeEx(T, '"', '\"', True);
  Result := T;
end;

function ContextMenuKeyExists(const Extension, KeyName: string): Boolean;
begin
  Result := RegKeyExists(HKCR, 'SystemFileAssociations\' + Extension + '\shell\' + KeyName);
end;

function GetVersionPart(const Version: string; const PartIndex: Integer): Integer;
var
  I: Integer;
  CurrentPart: Integer;
  CurrentText: string;
  Ch: string;
begin
  Result := 0;
  CurrentPart := 0;
  CurrentText := '';

  for I := 1 to Length(Version) do
  begin
    Ch := Copy(Version, I, 1);
    if Ch = '.' then
    begin
      if CurrentPart = PartIndex then
      begin
        Result := StrToIntDef(CurrentText, 0);
        exit;
      end;

      CurrentPart := CurrentPart + 1;
      CurrentText := '';
    end
    else
      CurrentText := CurrentText + Ch;
  end;

  if CurrentPart = PartIndex then
    Result := StrToIntDef(CurrentText, 0);
end;

function CompareVersions(const LeftVersion, RightVersion: string): Integer;
var
  I: Integer;
  LeftPart: Integer;
  RightPart: Integer;
begin
  Result := 0;

  for I := 0 to 3 do
  begin
    LeftPart := GetVersionPart(LeftVersion, I);
    RightPart := GetVersionPart(RightVersion, I);

    if LeftPart < RightPart then
    begin
      Result := -1;
      exit;
    end;

    if LeftPart > RightPart then
    begin
      Result := 1;
      exit;
    end;
  end;
end;

function IsOurDisplayName(const DisplayName: string): Boolean;
var
  AppNameWithSpace: string;
begin
  AppNameWithSpace := '{#MyAppName} ';
  Result := (DisplayName = '{#MyAppName}') or
    (Copy(DisplayName, 1, Length(AppNameWithSpace)) = AppNameWithSpace);
end;

function ExtractVersionFromDisplayName(const DisplayName: string): string;
var
  AppNameWithSpace: string;
begin
  AppNameWithSpace := '{#MyAppName} ';
  Result := '';

  if Copy(DisplayName, 1, Length(AppNameWithSpace)) = AppNameWithSpace then
    Result := Copy(DisplayName, Length(AppNameWithSpace) + 1, Length(DisplayName));
end;

function TryReadInstallFromKey(const RootKey: Integer; const Subkey: string): Boolean;
var
  DisplayName: string;
begin
  Result := False;

  if RegQueryStringValue(RootKey, Subkey, 'DisplayName', DisplayName) then
  begin
    if IsOurDisplayName(DisplayName) then
    begin
      HasInstalledVersion := True;

      if not RegQueryStringValue(RootKey, Subkey, 'DisplayVersion', InstalledVersion) then
        InstalledVersion := ExtractVersionFromDisplayName(DisplayName);

      RegQueryStringValue(RootKey, Subkey, 'UninstallString', InstalledUninstallString);
      RegQueryStringValue(RootKey, Subkey, 'InstallLocation', InstalledAppDir);
      Result := True;
    end;
  end;
end;

function FindInstalledByDisplayName(const RootKey: Integer): Boolean;
var
  Subkeys: TArrayOfString;
  I: Integer;
  BaseKey: string;
begin
  Result := False;
  BaseKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall';

  if RegGetSubkeyNames(RootKey, BaseKey, Subkeys) then
  begin
    for I := 0 to GetArrayLength(Subkeys) - 1 do
    begin
      if TryReadInstallFromKey(RootKey, BaseKey + '\' + Subkeys[I]) then
      begin
        Result := True;
        exit;
      end;
    end;
  end;
end;

procedure DetectInstalledVersion();
begin
  HasInstalledVersion := False;
  InstalledVersion := '';
  InstalledUninstallString := '';
  InstalledAppDir := '';
  InstalledVersionIsOlder := False;
  SkipSetupExitConfirmation := False;

  TryReadInstallFromKey(HKLM32, UninstallRegistryKey);

  if not HasInstalledVersion then
    TryReadInstallFromKey(HKLM, UninstallRegistryKey);

  if not HasInstalledVersion then
    FindInstalledByDisplayName(HKLM32);

  if not HasInstalledVersion then
    FindInstalledByDisplayName(HKLM);

  if HasInstalledVersion then
  begin
    if InstalledVersion = '' then
      InstalledVersion := '0.0.0';

    InstalledVersionIsOlder := CompareVersions(InstalledVersion, CurrentAppVersion) < 0;
  end;
end;

procedure DeleteOwnedContextMenuKey(const Subkey: string);
var
  CommandValue: string;
begin
  if RegQueryStringValue(HKCR, Subkey + '\command', '', CommandValue) then
  begin
    if Pos('run_prompt_tool.vbs', Lowercase(CommandValue)) > 0 then
      RegDeleteKeyIncludingSubkeys(HKCR, Subkey);
  end
  else if RegKeyExists(HKCR, Subkey) then
    RegDeleteKeyIncludingSubkeys(HKCR, Subkey);
end;

procedure RemoveContextMenuEntries();
begin
  DeleteOwnedContextMenuKey('SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt');
  DeleteOwnedContextMenuKey('SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt');
  DeleteOwnedContextMenuKey('SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo');

  DeleteOwnedContextMenuKey('SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt');
  DeleteOwnedContextMenuKey('SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt');
  DeleteOwnedContextMenuKey('SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo');
  DeleteOwnedContextMenuKey('SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames');
end;

function LaunchExistingUninstaller(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := False;

  if InstalledUninstallString = '' then
  begin
    MsgBox('The installed uninstaller could not be found.', mbError, MB_OK);
    exit;
  end;

  Result := ShellExec('', RemoveQuotes(InstalledUninstallString), '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);

  if not Result then
    MsgBox('Unable to launch the installed uninstaller. Error code: ' + IntToStr(ErrorCode), mbError, MB_OK);
end;

function ShouldInstallPositivePrompt(): Boolean;
begin
  Result := Assigned(CheckPositivePrompt) and CheckPositivePrompt.Checked;
end;

function ShouldInstallNegativePrompt(): Boolean;
begin
  Result := Assigned(CheckNegativePrompt) and CheckNegativePrompt.Checked;
end;

function ShouldInstallAIInfo(): Boolean;
begin
  Result := Assigned(CheckAIInfo) and CheckAIInfo.Checked;
end;

function ShouldInstallExtractFrames(): Boolean;
begin
  Result := Assigned(CheckExtractFrames) and CheckExtractFrames.Checked;
end;

procedure UpdateFrameExtractionControls();
var
  FixedMode: Boolean;
begin
  FixedMode := RadioFixedFolder.Checked;

  FixedFolderLabel.Enabled := FixedMode;
  FixedFolderEdit.Enabled := FixedMode;
  FixedFolderBrowseButton.Enabled := FixedMode;
  FixedFolderBehaviorLabel.Enabled := FixedMode;
  FixedFolderBehaviorPanel.Enabled := FixedMode;
  RadioFixedFolderSubfolder.Enabled := FixedMode;
  RadioFixedFolderShared.Enabled := FixedMode;
end;

procedure FrameExtractionOptionChanged(Sender: TObject);
begin
  UpdateFrameExtractionControls();
end;

procedure BrowseFixedFolder(Sender: TObject);
var
  SelectedDir: string;
begin
  SelectedDir := FixedFolderEdit.Text;
  if BrowseForFolder('Select the folder where extracted frames should always be stored', SelectedDir, False) then
    FixedFolderEdit.Text := SelectedDir;
end;

procedure InitializeWizard();
var
  MaintenanceInfoLabel: TNewStaticText;
  ContextInfoLabel: TNewStaticText;
begin
  DetectInstalledVersion();

  if HasInstalledVersion and (InstalledAppDir <> '') then
    WizardForm.DirEdit.Text := InstalledAppDir;

  MaintenancePage := CreateCustomPage(
    wpWelcome,
    'Existing Installation',
    'Choose what you want to do with AI Metadata Inspector'
  );

  MaintenanceInfoLabel := TNewStaticText.Create(MaintenancePage);
  MaintenanceInfoLabel.Parent := MaintenancePage.Surface;
  MaintenanceInfoLabel.Left := ScaleX(0);
  MaintenanceInfoLabel.Top := ScaleY(8);
  MaintenanceInfoLabel.Width := MaintenancePage.SurfaceWidth;
  MaintenanceInfoLabel.Height := ScaleY(42);

  if HasInstalledVersion and InstalledVersionIsOlder then
    MaintenanceInfoLabel.Caption := 'AI Metadata Inspector ' + InstalledVersion + ' is already installed. This setup contains version ' + CurrentAppVersion + '.'
  else
    MaintenanceInfoLabel.Caption := 'AI Metadata Inspector ' + CurrentAppVersion + ' is already installed.';

  RadioMaintenanceUpdate := TRadioButton.Create(MaintenancePage);
  RadioMaintenanceUpdate.Parent := MaintenancePage.Surface;
  RadioMaintenanceUpdate.Left := ScaleX(0);
  RadioMaintenanceUpdate.Top := MaintenanceInfoLabel.Top + ScaleY(48);
  RadioMaintenanceUpdate.Width := MaintenancePage.SurfaceWidth;
  RadioMaintenanceUpdate.Caption := 'Update to version ' + CurrentAppVersion + ' and keep the selected modules';
  RadioMaintenanceUpdate.Checked := InstalledVersionIsOlder;
  RadioMaintenanceUpdate.Enabled := InstalledVersionIsOlder;

  RadioMaintenanceModify := TRadioButton.Create(MaintenancePage);
  RadioMaintenanceModify.Parent := MaintenancePage.Surface;
  RadioMaintenanceModify.Left := ScaleX(0);
  RadioMaintenanceModify.Top := RadioMaintenanceUpdate.Top + ScaleY(28);
  RadioMaintenanceModify.Width := MaintenancePage.SurfaceWidth;
  RadioMaintenanceModify.Caption := 'Modify installed right-click modules';
  RadioMaintenanceModify.Checked := not InstalledVersionIsOlder;

  RadioMaintenanceUninstall := TRadioButton.Create(MaintenancePage);
  RadioMaintenanceUninstall.Parent := MaintenancePage.Surface;
  RadioMaintenanceUninstall.Left := ScaleX(0);
  RadioMaintenanceUninstall.Top := RadioMaintenanceModify.Top + ScaleY(28);
  RadioMaintenanceUninstall.Width := MaintenancePage.SurfaceWidth;
  RadioMaintenanceUninstall.Caption := 'Uninstall AI Metadata Inspector';

  ContextMenuPage := CreateCustomPage(
    wpSelectDir,
    'Context Menu Options',
    'Choose which right-click entries should be installed'
  );

  ContextInfoLabel := TNewStaticText.Create(ContextMenuPage);
  ContextInfoLabel.Parent := ContextMenuPage.Surface;
  ContextInfoLabel.Left := ScaleX(0);
  ContextInfoLabel.Top := ScaleY(8);
  ContextInfoLabel.Width := ContextMenuPage.SurfaceWidth;
  ContextInfoLabel.Height := ScaleY(24);
  ContextInfoLabel.Caption := 'All options are enabled by default.';

  CheckPositivePrompt := TNewCheckBox.Create(ContextMenuPage);
  CheckPositivePrompt.Parent := ContextMenuPage.Surface;
  CheckPositivePrompt.Left := ScaleX(0);
  CheckPositivePrompt.Top := ContextInfoLabel.Top + ScaleY(30);
  CheckPositivePrompt.Width := ContextMenuPage.SurfaceWidth;
  CheckPositivePrompt.Caption := 'AI - Copy positive prompt';
  CheckPositivePrompt.Checked := (not HasInstalledVersion) or ContextMenuKeyExists('.png', 'AI.1_CopyPositivePrompt') or ContextMenuKeyExists('.mp4', 'AI.1_CopyPositivePrompt');

  CheckNegativePrompt := TNewCheckBox.Create(ContextMenuPage);
  CheckNegativePrompt.Parent := ContextMenuPage.Surface;
  CheckNegativePrompt.Left := ScaleX(0);
  CheckNegativePrompt.Top := CheckPositivePrompt.Top + ScaleY(24);
  CheckNegativePrompt.Width := ContextMenuPage.SurfaceWidth;
  CheckNegativePrompt.Caption := 'AI - Copy negative prompt';
  CheckNegativePrompt.Checked := (not HasInstalledVersion) or ContextMenuKeyExists('.png', 'AI.2_CopyNegativePrompt') or ContextMenuKeyExists('.mp4', 'AI.2_CopyNegativePrompt');

  CheckAIInfo := TNewCheckBox.Create(ContextMenuPage);
  CheckAIInfo.Parent := ContextMenuPage.Surface;
  CheckAIInfo.Left := ScaleX(0);
  CheckAIInfo.Top := CheckNegativePrompt.Top + ScaleY(24);
  CheckAIInfo.Width := ContextMenuPage.SurfaceWidth;
  CheckAIInfo.Caption := 'AI - Ai Info';
  CheckAIInfo.Checked := (not HasInstalledVersion) or ContextMenuKeyExists('.png', 'AI.3_ShowMetadataInfo') or ContextMenuKeyExists('.mp4', 'AI.3_ShowMetadataInfo');

  CheckExtractFrames := TNewCheckBox.Create(ContextMenuPage);
  CheckExtractFrames.Parent := ContextMenuPage.Surface;
  CheckExtractFrames.Left := ScaleX(0);
  CheckExtractFrames.Top := CheckAIInfo.Top + ScaleY(24);
  CheckExtractFrames.Width := ContextMenuPage.SurfaceWidth;
  CheckExtractFrames.Caption := 'AI - Extract Frames (MP4 only)';
  CheckExtractFrames.Checked := (not HasInstalledVersion) or ContextMenuKeyExists('.mp4', 'AI.4_ExtractFrames');

  FrameExtractionPage := CreateCustomPage(
    ContextMenuPage.ID,
    'Frame Extraction Settings',
    'Choose where MP4 frame extractions should be written'
  );

  RadioNextToVideo := TRadioButton.Create(FrameExtractionPage);
  RadioNextToVideo.Parent := FrameExtractionPage.Surface;
  RadioNextToVideo.Left := ScaleX(0);
  RadioNextToVideo.Top := ScaleY(8);
  RadioNextToVideo.Width := FrameExtractionPage.SurfaceWidth;
  RadioNextToVideo.Caption := 'Extract frames next to the video file into a folder named "video-name-frames"';
  RadioNextToVideo.Checked := True;
  RadioNextToVideo.OnClick := @FrameExtractionOptionChanged;

  RadioFixedFolder := TRadioButton.Create(FrameExtractionPage);
  RadioFixedFolder.Parent := FrameExtractionPage.Surface;
  RadioFixedFolder.Left := ScaleX(0);
  RadioFixedFolder.Top := RadioNextToVideo.Top + ScaleY(34);
  RadioFixedFolder.Width := FrameExtractionPage.SurfaceWidth;
  RadioFixedFolder.Caption := 'Always extract frames into a fixed folder';
  RadioFixedFolder.OnClick := @FrameExtractionOptionChanged;

  FixedFolderLabel := TNewStaticText.Create(FrameExtractionPage);
  FixedFolderLabel.Parent := FrameExtractionPage.Surface;
  FixedFolderLabel.Left := ScaleX(20);
  FixedFolderLabel.Top := RadioFixedFolder.Top + ScaleY(30);
  FixedFolderLabel.Caption := 'Fixed folder:';

  FixedFolderEdit := TNewEdit.Create(FrameExtractionPage);
  FixedFolderEdit.Parent := FrameExtractionPage.Surface;
  FixedFolderEdit.Left := ScaleX(20);
  FixedFolderEdit.Top := FixedFolderLabel.Top + ScaleY(18);
  FixedFolderEdit.Width := FrameExtractionPage.SurfaceWidth - ScaleX(110);
  FixedFolderEdit.Text := ExpandConstant('{userdocs}\Frames');

  FixedFolderBrowseButton := TNewButton.Create(FrameExtractionPage);
  FixedFolderBrowseButton.Parent := FrameExtractionPage.Surface;
  FixedFolderBrowseButton.Left := FixedFolderEdit.Left + FixedFolderEdit.Width + ScaleX(6);
  FixedFolderBrowseButton.Top := FixedFolderEdit.Top - ScaleY(1);
  FixedFolderBrowseButton.Width := ScaleX(75);
  FixedFolderBrowseButton.Height := FixedFolderEdit.Height + ScaleY(2);
  FixedFolderBrowseButton.Caption := 'Browse...';
  FixedFolderBrowseButton.OnClick := @BrowseFixedFolder;

  FixedFolderBehaviorLabel := TNewStaticText.Create(FrameExtractionPage);
  FixedFolderBehaviorLabel.Parent := FrameExtractionPage.Surface;
  FixedFolderBehaviorLabel.Left := ScaleX(20);
  FixedFolderBehaviorLabel.Top := FixedFolderEdit.Top + ScaleY(36);
  FixedFolderBehaviorLabel.Caption := 'When using a fixed folder:';

  FixedFolderBehaviorPanel := TPanel.Create(FrameExtractionPage);
  FixedFolderBehaviorPanel.Parent := FrameExtractionPage.Surface;
  FixedFolderBehaviorPanel.Left := ScaleX(20);
  FixedFolderBehaviorPanel.Top := FixedFolderBehaviorLabel.Top + ScaleY(18);
  FixedFolderBehaviorPanel.Width := FrameExtractionPage.SurfaceWidth - ScaleX(20);
  FixedFolderBehaviorPanel.Height := ScaleY(56);
  FixedFolderBehaviorPanel.BevelOuter := bvNone;
  FixedFolderBehaviorPanel.TabStop := False;

  RadioFixedFolderSubfolder := TRadioButton.Create(FrameExtractionPage);
  RadioFixedFolderSubfolder.Parent := FixedFolderBehaviorPanel;
  RadioFixedFolderSubfolder.Left := ScaleX(20);
  RadioFixedFolderSubfolder.Top := ScaleY(2);
  RadioFixedFolderSubfolder.Width := FixedFolderBehaviorPanel.Width - ScaleX(20);
  RadioFixedFolderSubfolder.Caption := 'Use a subfolder for each video';
  RadioFixedFolderSubfolder.Checked := True;

  RadioFixedFolderShared := TRadioButton.Create(FrameExtractionPage);
  RadioFixedFolderShared.Parent := FixedFolderBehaviorPanel;
  RadioFixedFolderShared.Left := ScaleX(20);
  RadioFixedFolderShared.Top := RadioFixedFolderSubfolder.Top + ScaleY(24);
  RadioFixedFolderShared.Width := FixedFolderBehaviorPanel.Width - ScaleX(20);
  RadioFixedFolderShared.Caption := 'Use one app-managed shared subfolder inside the fixed folder';

  UpdateFrameExtractionControls();
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;

  if PageID = MaintenancePage.ID then
  begin
    Result := not HasInstalledVersion;
    exit;
  end;

  if HasInstalledVersion and (PageID = wpSelectDir) then
  begin
    Result := True;
    exit;
  end;

  if PageID = FrameExtractionPage.ID then
    Result := not ShouldInstallExtractFrames();
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = MaintenancePage.ID then
  begin
    if RadioMaintenanceUninstall.Checked then
    begin
      if LaunchExistingUninstaller() then
      begin
        SkipSetupExitConfirmation := True;
        WizardForm.Close();
      end;

      Result := False;
      exit;
    end;
  end;

  if CurPageID = FrameExtractionPage.ID then
  begin
    if RadioFixedFolder.Checked and (Trim(FixedFolderEdit.Text) = '') then
    begin
      MsgBox('Please choose a fixed folder for frame extraction.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  if SkipSetupExitConfirmation then
    Confirm := False;
end;

function PrepareToInstall(var NeedsRestart: Boolean): string;
begin
  RemoveContextMenuEntries();
  Result := '';
end;

procedure SaveFrameExtractionConfig();
var
  ConfigPath: string;
  ConfigContent: string;
  ModeValue: string;
  FolderValue: string;
  BehaviorValue: string;
begin
  if not ShouldInstallExtractFrames() then
    exit;

  if RadioFixedFolder.Checked then
  begin
    ModeValue := 'fixed_folder';
    FolderValue := Trim(FixedFolderEdit.Text);

    if RadioFixedFolderShared.Checked then
      BehaviorValue := 'single_shared_folder'
    else
      BehaviorValue := 'subfolder_per_video';
  end
  else
  begin
    ModeValue := 'next_to_video';
    FolderValue := '';
    BehaviorValue := 'subfolder_per_video';
  end;

  ConfigPath := ExpandConstant('{localappdata}\AI Metadata Inspector\config.json');

  ConfigContent :=
    '{'#13#10 +
    '  "frame_extraction": {'#13#10 +
    '    "mode": "' + ModeValue + '",'#13#10 +
    '    "fixed_folder": "' + EscapeJson(FolderValue) + '",'#13#10 +
    '    "fixed_folder_behavior": "' + BehaviorValue + '"'#13#10 +
    '  }'#13#10 +
    '}'#13#10;

  SaveStringToFile(ConfigPath, ConfigContent, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveFrameExtractionConfig();
  end;
end;
