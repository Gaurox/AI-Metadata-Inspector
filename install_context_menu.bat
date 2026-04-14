@echo off

set APP_DIR=%~dp0

echo Installing AI Metadata Inspector context menu...

:: ================= PNG =================

reg add "HKCR\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt" /ve /d "AI - Copy positive prompt" /f
reg add "HKCR\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt" /v "Icon" /d "%APP_DIR%icons\positive.ico" /f
reg add "HKCR\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" positive" /f

reg add "HKCR\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt" /ve /d "AI - Copy negative prompt" /f
reg add "HKCR\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt" /v "Icon" /d "%APP_DIR%icons\negative.ico" /f
reg add "HKCR\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" negative" /f

reg add "HKCR\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo" /ve /d "AI - Metadata Info" /f
reg add "HKCR\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo" /v "Icon" /d "%APP_DIR%icons\info.ico" /f
reg add "HKCR\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" info" /f

:: ================= MP4 =================

reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt" /ve /d "AI - Copy positive prompt" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt" /v "Icon" /d "%APP_DIR%icons\positive.ico" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" positive" /f

reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt" /ve /d "AI - Copy negative prompt" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt" /v "Icon" /d "%APP_DIR%icons\negative.ico" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" negative" /f

reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo" /ve /d "AI - Metadata Info" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo" /v "Icon" /d "%APP_DIR%icons\info.ico" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" info" /f

:: 🔥 NEW FEATURE
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames" /ve /d "AI - Extract Frames" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames" /v "Icon" /d "%APP_DIR%icons\extract.ico" /f
reg add "HKCR\SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames\command" /ve /d "wscript.exe \"%APP_DIR%run_prompt_tool.vbs\" \"%1\" extract_frames" /f

echo Done.
pause