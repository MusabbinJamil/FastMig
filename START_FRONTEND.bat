@echo off
echo ========================================
echo FastMig Frontend Starter
echo ========================================
echo.

cd flutter-frontend-app

echo ========================================
echo Starting Flutter on Chrome...
echo ========================================
echo.
echo PLEASE WAIT:
echo - First launch takes 30-60 seconds
echo - Compiling Dart code to JavaScript...
echo - Chrome will open automatically
echo.
echo IGNORE these warnings (they're normal):
echo - "file_picker:windows references..."
echo.
echo KEEP THIS WINDOW OPEN!
echo Press Ctrl+C to stop the app
echo ========================================
echo.
flutter run -d chrome

echo.
echo.
echo ========================================
echo App stopped
echo ========================================
pause
