@echo off
rem Starts the customised portfolio only. See dev\serve.py for the safety checks.
cd /d "%~dp0"
python dev\serve.py 5000
pause
