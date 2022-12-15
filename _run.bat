echo off
chcp 65001

title RtMonitor_Dash

cd %~dp0
call "venv\Scripts\activate.bat"

cd %~dp0
python app_dash_LiveSignal.py

pause