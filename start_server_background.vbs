' 魏征像素服务器 - 后台启动脚本（无窗口）
' 使用 VBScript 隐藏命令行窗口

Set WshShell = CreateObject("WScript.Shell")

' 获取当前目录
currentDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' 构建命令（使用 pythonw.exe 无窗口运行）
cmd = "pythonw.exe -m src.server --port 7788"

' 在后台运行
WshShell.Run cmd, 0, False

' 显示提示
MsgBox "魏征像素服务器已在后台启动！" & vbCrLf & vbCrLf & "端口: 7788" & vbCrLf & "API: http://localhost:7788", vbInformation, "魏征 Agent"
