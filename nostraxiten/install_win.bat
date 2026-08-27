@echo off
setlocal enabledelayedexpansion

echo =================================================
echo       NOSTRAXITEN Installer (Windows)
echo =================================================
echo.

:: 1. Comprobar si Python 3 está en PATH
set PYTHON_CMD=python
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    set PYTHON_CMD=py
    %PYTHON_CMD% --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [X] Python no se encontro en el PATH.
        echo Por favor, instala Python 3 y marcalo para agregar al PATH.
        pause
        exit /b 1
    )
)

:: 2. Crear venv
echo [*] Creando entorno virtual (.venv)...
%PYTHON_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [X] Error al crear el entorno virtual.
    pause
    exit /b 1
)

:: 3. Activar venv
echo [*] Activando entorno virtual...
call .venv\Scripts\activate

:: 4. Instalar requirements.txt
echo [*] Instalando dependencias base (requirements.txt)...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Hubo problemas instalando requirements.txt.
)

:: 5. Instalar pywin32 (solo Windows)
echo [*] Instalando dependencias especificas de Windows (pywin32)...
pip install pywin32
if %errorlevel% neq 0 (
    echo [!] No se pudo instalar pywin32. Algunas funciones forenses pueden fallar.
)

:: 6. Generar lanzador nostraxiten.bat
echo [*] Generando lanzador nostraxiten.bat...
echo @echo off > nostraxiten.bat
echo setlocal >> nostraxiten.bat
echo cd /d "%%~dp0" >> nostraxiten.bat
echo call .venv\Scripts\activate >> nostraxiten.bat
echo python nostraxiten.py %%* >> nostraxiten.bat
echo endlocal >> nostraxiten.bat

echo.
echo [!] INSTALACION COMPLETADA
echo [!] Para iniciar, ejecuta nostraxiten.bat
echo.
pause
