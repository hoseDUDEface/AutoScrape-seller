@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo Running AutoScrape
echo ===================================================
echo.

REM Store the current directory
set "ORIGINAL_DIR=%CD%"

REM Check if the backend directory exists
if not exist backend\ (
    echo Error: The backend directory does not exist.
    echo Please make sure you're running this script from the correct location.
    goto :error
)

REM Check if the autoscrape.py file exists
if not exist backend\autoscrape.py (
    echo Error: Could not find backend\autoscrape.py
    echo Please make sure the file exists.
    goto :error
)

REM Check if setup.bat exists
if not exist setup.bat (
    echo Warning: setup.bat does not exist. Cannot automatically install dependencies.
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed.
    
    if exist setup.bat (
        echo Running setup.bat to install dependencies...
        call setup.bat
        
        REM Check again if Python is installed after setup
        where python >nul 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo Error: Python installation failed.
            goto :error
        )
    ) else (
        echo Error: setup.bat not found. Cannot install Python.
        goto :error
    )
)

REM Create a temporary script to check for required modules
echo import sys > "%TEMP%\check_modules.py"
echo try: >> "%TEMP%\check_modules.py"
echo     from PyQt5.QtWidgets import QApplication >> "%TEMP%\check_modules.py"
echo     from PyQt5.QtCore import QThread >> "%TEMP%\check_modules.py"
echo     print("Dependencies OK") >> "%TEMP%\check_modules.py"
echo except ImportError as e: >> "%TEMP%\check_modules.py"
echo     print(f"Missing dependency: {e}") >> "%TEMP%\check_modules.py"
echo     sys.exit(1) >> "%TEMP%\check_modules.py"

REM Run the dependency check
python "%TEMP%\check_modules.py" > "%TEMP%\module_check_result.txt" 2>&1
set /p CHECK_RESULT=<"%TEMP%\module_check_result.txt"
del "%TEMP%\check_modules.py"
del "%TEMP%\module_check_result.txt"

REM If dependencies are missing, run setup.bat
echo !CHECK_RESULT! | findstr /C:"Missing dependency" >nul
if %ERRORLEVEL% EQU 0 (
    echo !CHECK_RESULT!
    
    if exist setup.bat (
        echo Running setup.bat to install dependencies...
        call setup.bat
    ) else (
        echo Error: setup.bat not found. Cannot install dependencies.
        goto :error
    )
)

REM Change to the backend directory and run the script
echo Changing to backend directory...
cd backend

echo Running autoscrape.py...
python autoscrape.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: The script encountered an error during execution.
    cd "%ORIGINAL_DIR%"
    goto :error
)

REM Return to the original directory
cd "%ORIGINAL_DIR%"

echo.
echo ===================================================
echo AutoScrape completed successfully!
echo ===================================================
goto :end

:error
echo.
echo ===================================================
echo AutoScrape execution failed.
echo ===================================================

:end
pause