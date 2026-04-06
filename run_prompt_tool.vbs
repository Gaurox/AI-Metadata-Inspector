Set objShell = CreateObject("Wscript.Shell")

scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

pythonExe = scriptDir & "\python_embeded\python.exe"
mainScript = scriptDir & "\main.py"

filePath = WScript.Arguments(0)
mode = WScript.Arguments(1)

cmd = """" & pythonExe & """ """ & mainScript & """ """ & filePath & """ """ & mode & """"

' 0 = invisible, False = no wait
objShell.Run cmd, 0, False