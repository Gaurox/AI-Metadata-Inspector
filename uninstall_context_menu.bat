@echo off

echo Removing AI Metadata Inspector context menu...

:: ================= PNG =================

reg delete "HKCR\SystemFileAssociations\.png\shell\AI.1_CopyPositivePrompt" /f >nul 2>&1
reg delete "HKCR\SystemFileAssociations\.png\shell\AI.2_CopyNegativePrompt" /f >nul 2>&1
reg delete "HKCR\SystemFileAssociations\.png\shell\AI.3_ShowMetadataInfo" /f >nul 2>&1

:: ================= MP4 =================

reg delete "HKCR\SystemFileAssociations\.mp4\shell\AI.1_CopyPositivePrompt" /f >nul 2>&1
reg delete "HKCR\SystemFileAssociations\.mp4\shell\AI.2_CopyNegativePrompt" /f >nul 2>&1
reg delete "HKCR\SystemFileAssociations\.mp4\shell\AI.3_ShowMetadataInfo" /f >nul 2>&1
reg delete "HKCR\SystemFileAssociations\.mp4\shell\AI.4_ExtractFrames" /f >nul 2>&1

echo Done.
pause