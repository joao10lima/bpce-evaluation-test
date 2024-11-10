@echo off
REM Build the executable with PyInstaller
pipenv run pyinstaller --name reviseur --add-data "./images:images" --onefile .\reviseur\main.py

REM Copy the param.xml file to the output directory
xcopy param.xml dist\ /Y

REM Clean up (optional)
echo Cleaning up...
