Set objShell = CreateObject("WScript.Shell")
Set objEnv = objShell.Environment("Process")

' Get the script directory
strPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' Change to the parle directory
objShell.CurrentDirectory = strPath

' Run the tray app silently
objShell.Run "cmd /c uv run parle-tray", 0, False