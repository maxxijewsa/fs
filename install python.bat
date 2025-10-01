@echo off
echo Downloading Python 3.11.6...
bitsadmin /transfer "PythonDownloadJob" /download /priority normal https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe "%cd%\python-3.11.6.exe"


if not exist "%cd%\python-3.11.6.exe" (
    echo Download failed. Please check your internet connection or URL and try again.
    pause
    exit
)

echo Installing Python 3.11.6...

"%cd%\python-3.11.6.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %ERRORLEVEL% equ 0 (
    echo Python 3.11.6 has been installed successfully.
    echo Adding Python Scripts directory to system PATH...
    setx PATH "%PATH%;C:\Program Files\Python311\Scripts"
    echo Python Scripts directory has been added to the system PATH.
) else (
    echo Installation failed. Error code: %ERRORLEVEL%
)

pause