@echo off
del /f /s /q build
del /f /s /q dist
pyinstaller -y main.spec
xcopy detects dist\main\detects\ /e
copy configs.yml dist\main\
