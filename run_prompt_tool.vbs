If WScript.Arguments.Count < 2 Then
    WScript.Quit 1
End If

Dim filePath, mode
filePath = WScript.Arguments(0)
mode     = WScript.Arguments(1)

If Len(Trim(filePath)) = 0 Or Len(Trim(mode)) = 0 Then
    WScript.Quit 1
End If

Dim fso, scriptDir
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

Dim pythonExe, mainScript
pythonExe  = scriptDir & "\python_embeded\python.exe"
mainScript = scriptDir & "\main.py"

If Not fso.FileExists(pythonExe) Then
    WScript.Quit 2
End If

If Not fso.FileExists(mainScript) Then
    WScript.Quit 3
End If

Dim cmd
cmd = """" & pythonExe & """ """ & mainScript & """ """ & filePath & """ """ & mode & """"

Dim objShell
Set objShell = CreateObject("Wscript.Shell")

' 0 = invisible window, False = do not wait
objShell.Run cmd, 0, False
