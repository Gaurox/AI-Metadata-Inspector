Option Explicit

Dim shell, fso, appDir, pythonExe, mainPy, args, mode, cmd, exitCode, logPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

appDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = appDir
pythonExe = appDir & "\python_embeded\pythonw.exe"
mainPy = appDir & "\main.py"

If WScript.Arguments.Count < 1 Then
    MsgBox "AI Metadata Inspector: missing target file argument.", vbCritical, "AI Metadata Inspector"
    WScript.Quit 1
End If

If Not fso.FileExists(pythonExe) Then
    MsgBox "AI Metadata Inspector: embedded Python was not found:" & vbCrLf & pythonExe, vbCritical, "AI Metadata Inspector"
    WScript.Quit 2
End If

If Not fso.FileExists(mainPy) Then
    MsgBox "AI Metadata Inspector: main.py was not found:" & vbCrLf & mainPy, vbCritical, "AI Metadata Inspector"
    WScript.Quit 3
End If

mode = "positive"
If WScript.Arguments.Count >= 2 Then
    mode = WScript.Arguments(1)
End If

cmd = Quote(pythonExe) & " " & Quote(mainPy) & " " & Quote(WScript.Arguments(0)) & " " & Quote(mode)
exitCode = shell.Run(cmd, 0, True)

If LCase(mode) = "info" And exitCode <> 0 Then
    logPath = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\AI Metadata Inspector\logs\ai_info_error.log"
    MsgBox "AI Info failed to open." & vbCrLf & vbCrLf & _
           "Exit code: " & CStr(exitCode) & vbCrLf & _
           "Log file: " & logPath & vbCrLf & vbCrLf & _
           "If no log exists, the failure is before Python starts.", _
           vbCritical, "AI Metadata Inspector"
End If

WScript.Quit exitCode

Function Quote(ByVal value)
    Quote = Chr(34) & Replace(CStr(value), Chr(34), Chr(34) & Chr(34)) & Chr(34)
End Function
