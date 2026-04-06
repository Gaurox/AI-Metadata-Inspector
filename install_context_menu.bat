@echo off
setlocal

set "BASE_DIR=%~dp0"

:: =========================
:: PNG
:: =========================

reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt" /ve /d "AI - Copy positive prompt" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt" /v "Icon" /d "%BASE_DIR%icons\positive.ico" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt\command" /ve /d "\"wscript.exe\" \"%BASE_DIR%run_prompt_tool.vbs\" \"%%1\" positive" /f

reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt" /ve /d "AI - Copy negative prompt" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt" /v "Icon" /d "%BASE_DIR%icons\negative.ico" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt\command" /ve /d "\"wscript.exe\" \"%BASE_DIR%run_prompt_tool.vbs\" \"%%1\" negative" /f

reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo" /ve /d "AI - Metadata Info" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo" /v "Icon" /d "%BASE_DIR%icons\info.ico" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo\command" /ve /d "\"wscript.exe\" \"%BASE_DIR%run_prompt_tool.vbs\" \"%%1\" info" /f

:: =========================
:: MP4
:: =========================

reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt" /ve /d "AI - Copy positive prompt" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt" /v "Icon" /d "%BASE_DIR%icons\positive.ico" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt\command" /ve /d "\"wscript.exe\" \"%BASE_DIR%run_prompt_tool.vbs\" \"%%1\" positive" /f

reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt" /ve /d "AI - Copy negative prompt" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt" /v "Icon" /d "%BASE_DIR%icons\negative.ico" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt\command" /ve /d "\"wscript.exe\" \"%BASE_DIR%run_prompt_tool.vbs\" \"%%1\" negative" /f

reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo" /ve /d "AI - Metadata Info" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo" /v "Icon" /d "%BASE_DIR%icons\info.ico" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo\command" /ve /d "\"wscript.exe\" \"%BASE_DIR%run_prompt_tool.vbs\" \"%%1\" info" /f

echo.
echo Installation completed!
pause
