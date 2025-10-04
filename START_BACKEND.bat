@echo off
echo ========================================
echo FastMig Backend - Virtual Environment
echo ========================================
echo.

cd python-backend

echo Checking for virtual environment...
if exist "venv\Scripts\python.exe" (
    echo Virtual environment found!
    goto :activate_venv
)

echo Virtual environment not found. Creating one...
echo This will take a minute...
echo.

python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python is installed correctly
    pause
    exit /b 1
)

echo Virtual environment created!
echo.

:activate_venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Installing/Updating required packages...
echo.

pip install Flask Flask-CORS pandas openpyxl numpy
if %errorlevel% neq 0 (
    echo.
    echo Warning: Some packages may not have installed correctly.
    echo Continuing anyway...
)

echo.
echo ========================================
echo Starting FastMig Backend Server...
echo Server will be available at http://localhost:5000
echo.
echo KEEP THIS WINDOW OPEN!
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python server.py

pause
