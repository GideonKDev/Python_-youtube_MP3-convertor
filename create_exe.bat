@echo off
echo Building YouTube to MP3 Converter executable...
echo.

REM Check for PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Create the executable
echo.
echo Creating executable...
pyinstaller --onefile ^
            --windowed ^
            --name="YouTube2MP3_Converter" ^
            --add-data="assets;assets" ^
            --icon=assets/icon.ico ^
            --noconsole ^
            run.py

echo.
echo Done! Executable created in: dist\YouTube2MP3_Converter.exe
echo.
pause