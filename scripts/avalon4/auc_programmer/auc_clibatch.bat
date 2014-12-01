@echo off
:startprog
echo %date%_%time%   烧写开始
C:\Keil_v5\UV4\UV4 -f auc_programmer.uvproj -j0 -O avalon-usb-converter.log
if %ERRORLEVEL% EQU 0 (
	echo 烧写完成，请更换下一个
) else (
	echo 烧写未成功，请检查！
)
::sleep for 2 seconds
ping 10.11.12.13 -n 2 -w 1000 > nul
goto :startprog