@echo off
set cwd=%~DP0
python "%cwd%\packages\postinstall.py"
pause
