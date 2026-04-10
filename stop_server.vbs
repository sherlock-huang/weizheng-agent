' 魏征像素服务器 - 停止脚本

Set WshShell = CreateObject("WScript.Shell")

' 发送停止命令
cmd = "python.exe -m src.cli stop"
WshShell.Run cmd, 0, True

MsgBox "魏征像素服务器已停止！", vbInformation, "魏征 Agent"
