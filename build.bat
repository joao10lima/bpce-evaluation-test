@echo off
REM Build the executable with PyInstaller
pipenv run pyinstaller --name reviseur --hidden-import=reviewer --hidden-import=settings --hidden-import=utils --onefile .\reviseur\main.py

REM Copy the param.xml file to the output directory
xcopy param.xml dist\ /Y
REM Copy the images folder to the output directory
xcopy /E /I /Y ".\images" ".\dist\images"

REM Clean up (optional)
echo Cleaning up...
