@echo off
del /f /s /q build
del /f /s /q dist
del /f /q main.spec
pyinstaller --noupx -y main.py
xcopy detects dist\main\detects\ /e
copy configs.yml dist\main\