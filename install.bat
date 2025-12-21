@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
  echo Creando entorno virtual...
  python -m venv venv || (echo Error: no se pudo crear el venv & pause & exit /b 1)
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Actualizando pip...
python -m pip install --upgrade pip

if not exist "requirements.txt" (
  echo Error: requirements.txt no encontrado en %CD%
  pause
  exit /b 1
)

echo Instalando dependencias...
python -m pip install -r requirements.txt || (echo Error en pip install & pause & exit /b 1)

echo Aplicando migraciones (creara db.sqlite3 si usas SQLite)...
python manage.py migrate || (echo Error en migrate & pause & exit /b 1)

set /p CREATE_ADMIN="Crear superusuario ahora? (Y/N): "
if /I "%CREATE_ADMIN%"=="Y" (
  python manage.py createsuperuser
)

echo Instalacion completada.
pause