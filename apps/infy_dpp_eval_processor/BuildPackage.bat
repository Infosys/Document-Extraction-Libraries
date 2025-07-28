:: =============================================================================================================== *
:: Copyright 2022 Infosys Ltd.                                                                                     *
:: Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at   * 
:: http://www.apache.org/licenses/                                                                                 *
:: =============================================================================================================== *

@echo off
setlocal enabledelayedexpansion
setlocal

echo. 
echo #########################################
echo Build Package for Python Project
echo #########################################

::Overrides
SET SOURCE_CONTROL_VALIDATION=Y

::Get current date and time
SET CURR_DATE=""
SET CURR_TIME=""
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set CURR_DATE=%%c-%%a-%%b)
For /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set CURR_TIME=%%a:%%b)

::Get current directory
SET CURRENT_FOLDER_NAME=""
for %%I in (.) do set CURRENT_FOLDER_NAME=%%~nxI

echo.
echo PROJECT NAME - %CURRENT_FOLDER_NAME%
@REM echo PROJECT NAME - dpp_processor_app
echo.
:PROMPT
SET /P AREYOUSURE=Enter Y to confirm package creation: (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

echo.
echo Checking for python (any version) installation
call python --version

if %ERRORLEVEL% GEQ 1 GOTO PYTHON_NOT_FOUND_ERROR

IF "%SOURCE_CONTROL_VALIDATION%" NEQ "Y" (
	GOTO SHOW_MENU
)

echo.

::Do Clean up 
if exist .\target rmdir /Q /S .\target


@REM set PACKAGE_NAME=%CURRENT_FOLDER_NAME%
set PACKAGE_NAME=infy_dpp_eval_processor_app
set PACKAGE_FOLDER=.\target\%PACKAGE_NAME%
echo %PACKAGE_FOLDER%

mkdir %PACKAGE_FOLDER%
echo. 
echo Copying config file
mkdir %PACKAGE_FOLDER%\config
copy .\config %PACKAGE_FOLDER%\config
echo.

xcopy lib %PACKAGE_FOLDER%\lib\ /s /e
@REM xcopy src %PACKAGE_FOLDER%\src\ /s /e
mkdir %PACKAGE_FOLDER%\src
copy src\app_dpp_container_external.py %PACKAGE_FOLDER%\src\app_dpp_container_external.py 
echo.
echo Deleting __pycache__ folder
FOR /d /r %PACKAGE_FOLDER%\ %%d IN (__pycache__) DO @IF EXIST "%%d" rd /s /q "%%d"
echo.

echo.
echo Deleting logs folder
FOR /d /r %PACKAGE_FOLDER%\ %%d IN (logs) DO @IF EXIST "%%d" rd /s /q "%%d"
echo.


echo. 
echo Copying .env file
copy .env.tf %PACKAGE_FOLDER%\.env
echo Converting .env file to UNIX format
python -c "file_path=r'%PACKAGE_FOLDER%\.env'; data = open(file_path,'r').read(); open(file_path,'w',newline='\n').write(data)"
echo.


echo Copying other files
copy requirements.txt %PACKAGE_FOLDER%\requirements.txt
@REM copy Pipfile %PACKAGE_FOLDER%
@REM copy pythonservicemanager.bat %PACKAGE_FOLDER%
@REM copy winsw-2.3.0-net4.xml %PACKAGE_FOLDER%
copy Dockerfile .\target\Dockerfile

echo.
echo Creating Manifest file
SET MANIFEST_FILE_PATH=%PACKAGE_FOLDER%\MANIFEST.TXT

echo BuildTimestamp=%CURR_DATE% %CURR_TIME% >> %MANIFEST_FILE_PATH%

echo.

echo.
echo Creating tar file
cd .\target
tar.exe cf %PACKAGE_NAME%.tar  %PACKAGE_NAME%
cd..

echo.
echo ***************************************
echo Build output      : %PACKAGE_FOLDER% 
echo ***************************************
echo.

pause 
GOTO END

:PYTHON_NOT_FOUND_ERROR
echo.
echo Please install python first!
echo.
pause 
GOTO END

:VALIDATE_APP_METADATA_ERROR
echo.
echo Please fix the issues.
echo.
pause
GOTO END 



:: Function Definitions

:fnGetPropFromFile - Read key=value from file
set RESULT=
::for /f %%i in ('findstr %~2 %~1') do (set RESULT=%%i)
for /f "tokens=*" %%i in ('findstr %~2 %~1') do (set RESULT=%%i)
::echo RESULT=%RESULT%
set RESULT=%RESULT: =%
set RESULT=%RESULT:"=%
set RESULT=%RESULT:,=%

FOR /f "tokens=1,2 delims==" %%a IN ("%RESULT%") do (SET RESULT=%%b)
::ECHO %RESULT%

SET "%~3=%RESULT%"
goto:eof

:fnGetTfsChangesetNumber - Get changeset number from TFS
set RESULT=
for /f "tokens=*" %%i in ('tf history ./ /noprompt /recursive  /stopafter:1') do (set RESULT=%%i)
::echo %RESULT%

FOR /f "tokens=1,2 delims= " %%a IN ("%RESULT%") do (SET RESULT=%%a)
::echo %RESULT%
SET "%~1=%RESULT%"
goto:eof


:END
endlocal
