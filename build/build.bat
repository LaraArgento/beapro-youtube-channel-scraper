@ECHO OFF
:: Get the folder where this .bat file is located
set "SCRIPT_DIR=%~dp0"
:: Call build.ps1 with full path
powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%build.ps1"