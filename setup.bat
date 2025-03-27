@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo Environment Setup Script
echo ===================================================
echo.

REM Check if Python is installed
echo Checking for Python installation...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python 3...
    
    REM Create a temporary directory for the installer
    mkdir %TEMP%\python_installer
    cd %TEMP%\python_installer
    
    echo Downloading Python installer...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe', 'python_installer.exe')"
    
    echo Running Python installer...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo Cleaning up...
    cd %~dp0
    rmdir /s /q %TEMP%\python_installer
    
    echo Python installation complete!
) else (
    echo Python is already installed.
)

REM Install Python requirements
echo.
echo Installing Python requirements...
if exist Backend/requirementspy.txt (
    python -m pip install -r Backend/requirementspy.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python requirements.
        echo Please check Backend/requirementspy.txt and try again.
    ) else (
        echo Python requirements installed successfully!
    )
) else (
    echo Warning: Backend/requirementspy.txt not found.
)

REM Check if npm is installed
echo.
echo Checking for npm installation...
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo npm is not installed. Installing Node.js and npm...
    
    REM Create a temporary directory for the installer
    mkdir %TEMP%\nodejs_installer
    cd %TEMP%\nodejs_installer
    
    echo Downloading Node.js installer...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi', 'nodejs_installer.msi')"
    
    echo Running Node.js installer...
    start /wait msiexec /i nodejs_installer.msi /quiet /qn
    
    echo Cleaning up...
    cd %~dp0
    rmdir /s /q %TEMP%\nodejs_installer
    
    echo Node.js and npm installation complete!
    
    REM Refresh environment variables
    echo Refreshing environment variables...
    call RefreshEnv.cmd >nul 2>nul || (
        echo Warning: Unable to refresh environment variables automatically.
        echo You may need to restart your command prompt to use npm.
    )
) else (
    echo npm is already installed.
)

REM Install JavaScript requirements
echo.
echo Installing JavaScript requirements...
if exist Backend/requirementsjs.txt (
    for /F "tokens=*" %%i in (Backend/requirementsjs.txt) do (
        echo Installing: %%i
        npm install -g %%i
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install %%i
        )
    )
    echo JavaScript requirements installation complete!
) else (
    echo Warning: Backend/requirementsjs.txt not found
)

echo.
echo ===================================================
echo Setup completed!
echo ===================================================

pause