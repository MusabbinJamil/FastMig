@echo off
echo ========================================
echo FastMig Backend - Conda Environment
echo ========================================
echo.

cd python-backend

echo Activating conda environment 'fastmig'...
call conda activate fastmig
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate conda environment 'fastmig'
    echo Make sure conda is installed and the 'fastmig' environment exists
    pause
    exit /b 1
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
