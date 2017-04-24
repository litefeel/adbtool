@echo off
rem %cd% 工作目录/当前目录
rem %~dp0 bat文件所在目录

rem 启用延迟扩展，一行语句中延迟变量赋值
setlocal ENABLEDELAYEDEXPANSION

set rpstr=E:/work/zeus/GameEditors/UIEdit/res/
set xxx=/sdcard/hookzeus/
set localpath=%cd%/%1
set localpath=%localpath:\=/%

set remotepath=%localpath:E:/work/zeus/GameEditors/UIEdit/res/=!xxx!%
echo %localpath%
echo %remotepath%
adb push %localpath% %remotepath%
