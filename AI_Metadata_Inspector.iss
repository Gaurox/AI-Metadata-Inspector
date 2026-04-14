#define MyAppName "AI Metadata Inspector"
#define MyAppVersion "1.2.0"
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

VersionInfoVersion=1.2.0.0
VersionInfoTextVersion=1.2.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\Context_Menu_Tools"
Name: "{app}\ps"

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
Source: "app_config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "frame_extractor.py"; DestDir: "{app}"; Flags: ignoreversion

Source: "ps\info_window_helpers.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion
Source: "ps\info_window_layout.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion
Source: "ps\frame_extract_window.ps1"; DestDir: "{app}\ps"; Flags: ignoreversion

Source: "run_prompt_tool.vbs"; DestDir: "{app}"; Flags: ignoreversion

Source: "install_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion

Source: "exiftool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "exiftool_files\*"; DestDir: "{app}\exiftool_files"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "python_embeded\*"; DestDir: "{app}\python_embeded"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

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
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueData: "AI - Copy positive prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\positive.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" positive"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueData: "AI - Copy negative prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\negative.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" negative"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueData: "AI - Metadata Info"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\info.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" info"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueData: "AI - Copy positive prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\positive.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" positive"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueData: "AI - Copy negative prompt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\negative.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" negative"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueData: "AI - Metadata Info"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\info.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" info"; Flags: uninsdeletekey

Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames"; ValueType: string; ValueData: "AI - Extract Frames"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\icons\extract.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames\command"; ValueType: string; ValueData: """wscript.exe"" ""{app}\run_prompt_tool.vbs"" ""%1"" extract_frames"; Flags: uninsdeletekey

[Code]
var
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

function EscapeJson(const S: string): string;
var
  T: string;
begin
  T := S;
  StringChangeEx(T, '\', '\\', True);
  StringChangeEx(T, '"', '\"', True);
  Result := T;
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
begin
  FrameExtractionPage := CreateCustomPage(
    wpSelectDir,
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
  RadioFixedFolderShared.Caption := 'Use the fixed folder directly and replace previous extraction';

  UpdateFrameExtractionControls();
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = FrameExtractionPage.ID then
  begin
    if RadioFixedFolder.Checked and (Trim(FixedFolderEdit.Text) = '') then
    begin
      MsgBox('Please choose a fixed folder for frame extraction.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure SaveFrameExtractionConfig();
var
  ConfigPath: string;
  ConfigContent: string;
  ModeValue: string;
  FolderValue: string;
  BehaviorValue: string;
begin
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

  ConfigPath := ExpandConstant('{app}\config.json');

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