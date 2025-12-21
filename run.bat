REM ...existing code...
@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem elegir directorio del virtualenv (.venv preferido)
set "VENV_DIR="
if exist ".venv\Scripts\activate.bat" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\activate.bat" set "VENV_DIR=venv"
if not defined VENV_DIR (
  echo Entorno virtual no encontrado. Ejecuta install.bat primero.
  pause
  exit /b 1
)

rem obtener IP local dando preferencia a la interfaz Wi‑Fi/WLAN; si no hay, usar la primera IPv4 válida
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$adpt = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' -and ($_.Name -match 'Wi|Wireless|WLAN' -or $_.InterfaceDescription -match 'Wi|Wireless|WLAN') } | Select-Object -First 1; if($adpt){$ip=(Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $adpt.ifIndex | Where-Object { $_.IPAddress -notmatch '^(169|127)' } | Select-Object -First 1 -ExpandProperty IPAddress)}; if(-not $ip){$ip=(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^(169|127)' } | Select-Object -First 1 -ExpandProperty IPAddress)}; Write-Output $ip"`) do set "LOCAL_IP=%%i"
if "%LOCAL_IP%"=="" set "LOCAL_IP=localhost"

echo Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"

echo Aplicando migraciones...
python manage.py migrate

echo Iniciando servidor en nueva ventana...
rem usar cmd /k con cd y call para garantizar que active el venv en la nueva ventana
start "Django Server" cmd /k "cd /d "%~dp0" && call "%VENV_DIR%\Scripts\activate.bat" && python manage.py runserver 0.0.0.0:8000"

rem esperar un momento para que el servidor arranque
timeout /t 2 >nul

rem abrir la ruta /servidor en el navegador
if defined LOCAL_IP (
  echo Abriendo navegador en http://%LOCAL_IP%:8000/servidor
  start "" "http://%LOCAL_IP%:8000/servidor"
) else (
  echo Abriendo navegador en http://localhost:8000/servidor
  start "" "http://localhost:8000/servidor"
)

exit /b 0