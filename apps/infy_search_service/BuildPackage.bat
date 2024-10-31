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

if exist .git\ (
	GOTO VALIDATE_GIT
) else (
	GOTO VALIDATE_TFS
)

:VALIDATE_GIT
echo.
echo Checking for any local changes 
CALL git diff --quiet || echo Local changes found
if %ERRORLEVEL% GEQ 1 (
	GOTO LOCAL_CHANGES_WARNING
) else (
	GOTO LOCAL_CHANGES_NONE
)

:LOCAL_CHANGES_WARNING
echo.
CALL git diff --compact-summary
echo.
SET /P AREYOUSURE= **WARNING** Local changes found. Cancel build:([Y]/N) ?
IF /I "%AREYOUSURE%" NEQ "N" GOTO LOCAL_CHANGES_PRESENT_ERROR

:LOCAL_CHANGES_NONE
echo.
echo Getting latest commit id
FOR /f "tokens=1" %%f IN ('git rev-parse --short HEAD' ) DO SET LAST_COMMIT_ID=%%f
echo Last CommitId=%LAST_COMMIT_ID%
GOTO SHOW_MENU

:VALIDATE_TFS
echo.
echo Checking for TFS executable
call tf.exe 1>nul

if %ERRORLEVEL% GEQ 1 GOTO TFS_EXE_NOT_FOUND_ERROR

echo.
echo Getting latest TFS changeset number
call:fnGetTfsChangesetNumber LAST_TFS_CHANGESET_NUM
echo Latest TFS changeset number=%LAST_TFS_CHANGESET_NUM%

:SHOW_MENU
SET L_DEPLOY_ENV_NAME=""
ECHO.
ECHO ***************************************
ECHO SELECT ENV TO BUILD
ECHO A - Dev
ECHO B - Test
ECHO C - Prod
ECHO D - Demo
ECHO.
ECHO Z - Cancel
ECHO ***************************************
CHOICE /c:ABCDZ
::echo %ERRORLEVEL%
::ERRORLEVEL is always an index value of the choice value and not equal to the actual choice value 
IF %ERRORLEVEL% EQU 1 (
	SET L_DEPLOY_ENV_NAME=dev
)
IF %ERRORLEVEL% EQU 2 (
	SET L_DEPLOY_ENV_NAME=test
)
IF %ERRORLEVEL% EQU 3 (
	SET L_DEPLOY_ENV_NAME=prod
)
IF %ERRORLEVEL% EQU 4 (
	SET L_DEPLOY_ENV_NAME=demo
)
IF %ERRORLEVEL% EQU 5 (
	GOTO END
)

::Do Clean up 
if exist .\target rmdir /Q /S .\target


set PACKAGE_NAME=%CURRENT_FOLDER_NAME%
set PACKAGE_FOLDER=.\target\%PACKAGE_NAME%
echo %PACKAGE_FOLDER%

mkdir %PACKAGE_FOLDER%
echo. 
echo Copying config.ini file
mkdir %PACKAGE_FOLDER%\config
copy .\config\config.%L_DEPLOY_ENV_NAME%.ini %PACKAGE_FOLDER%\config\config.ini
echo.

:VALIDATE_APP_METADATA
set CONFIG_FILE_PATH=%PACKAGE_FOLDER%\config\config.ini
set SETUP_APP_NAME=
set SETUP_APP_VERSION=
set CONFIG_APP_NAME=
set CONFIG_APP_VERSION=

echo.
echo Validating %CONFIG_FILE_PATH%

call:fnGetPropFromFile setup.py, name, SETUP_APP_NAME
call:fnGetPropFromFile setup.py, version, SETUP_APP_VERSION
call:fnGetPropFromFile %CONFIG_FILE_PATH%, service_name, CONFIG_APP_NAME
call:fnGetPropFromFile %CONFIG_FILE_PATH%, service_version, CONFIG_APP_VERSION

SET VALIDATE_APP_METADATA_ERROR_FOUND=
IF %SETUP_APP_NAME% NEQ %CONFIG_APP_NAME% (
	ECHO **Error** Config property "service_name" is outdated !!!
	ECHO File=%CONFIG_FILE_PATH%
	ECHO Expected = %SETUP_APP_NAME% (from setup.py^)
	ECHO Found = %CONFIG_APP_NAME%
	ECHO.
	SET VALIDATE_APP_METADATA_ERROR_FOUND=Yes
)
IF %SETUP_APP_VERSION% NEQ %CONFIG_APP_VERSION% (
	ECHO **Error** Config property "service_version" is outdated !!!
	ECHO File=%CONFIG_FILE_PATH%
	ECHO Expected = %SETUP_APP_VERSION% (from setup.py^)
	ECHO Found = %CONFIG_APP_VERSION%
	ECHO.
	SET VALIDATE_APP_METADATA_ERROR_FOUND=Yes
)

IF "%VALIDATE_APP_METADATA_ERROR_FOUND%" EQU "Yes" (
	ECHO.
	GOTO VALIDATE_APP_METADATA_ERROR
) ELSE (
	ECHO.
	echo Validation successful
	echo -------------------------------------
	echo.SETUP_APP_NAME = %SETUP_APP_NAME%
	echo.CONFIG_APP_NAME = %CONFIG_APP_NAME%
	echo.SETUP_APP_VERSION = %SETUP_APP_VERSION%
	echo.CONFIG_APP_VERSION = %CONFIG_APP_VERSION%
	echo -------------------------------------
	ECHO.
)	

xcopy lib %PACKAGE_FOLDER%\lib\ /s /e
xcopy src %PACKAGE_FOLDER%\src\ /s /e
xcopy template %PACKAGE_FOLDER%\template\ /s /e

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
copy .env.%L_DEPLOY_ENV_NAME% %PACKAGE_FOLDER%\.env
echo Converting .env file to UNIX format
python -c "file_path=r'%PACKAGE_FOLDER%\.env'; data = open(file_path,'r').read(); open(file_path,'w',newline='\n').write(data)"
echo.

echo Copying other files
copy requirements.txt %PACKAGE_FOLDER%
::copy Pipfile %PACKAGE_FOLDER%
copy pythonservicemanager.bat %PACKAGE_FOLDER%
copy winsw-2.3.0-net4.xml %PACKAGE_FOLDER%
copy *.service %PACKAGE_FOLDER%

echo.
echo Creating Manifest file
SET MANIFEST_FILE_PATH=%PACKAGE_FOLDER%\MANIFEST.TXT
echo TfsChangesetNum=%LAST_TFS_CHANGESET_NUM% > %MANIFEST_FILE_PATH%
echo GitCommitId=%LAST_COMMIT_ID% >> %MANIFEST_FILE_PATH%
echo BuildTimestamp=%CURR_DATE% %CURR_TIME% >> %MANIFEST_FILE_PATH%
echo BuildEnvironment=%L_DEPLOY_ENV_NAME% >> %MANIFEST_FILE_PATH%
echo BuildUser=%USERNAME% >> %MANIFEST_FILE_PATH%
echo.

echo.
echo Creating tar file
cd .\target
tar.exe cf %PACKAGE_NAME%.tar  %PACKAGE_NAME%
cd..

echo.
echo ***************************************
echo Build command completed for environment: %L_DEPLOY_ENV_NAME%
echo TFS Changeset Num : %LAST_TFS_CHANGESET_NUM%
echo Git Commitid      : %LAST_COMMIT_ID% 
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

:LOCAL_CHANGES_PRESENT_ERROR
echo.
echo Build cancelled by user due to local changes found.
echo.
pause 
GOTO END

:VALIDATE_APP_METADATA_ERROR
echo.
echo Please fix the issues.
echo.
pause
GOTO END 

:TFS_EXE_NOT_FOUND_ERROR
echo.
echo ERROR: Source control validation failed. Please ensure tf.exe is available on PATH. 
echo Usually, it's found at C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\IDE
echo.
echo ------------------------------------------------
echo NOTE: To disable this validation in case working in client environment: 
echo Modify below property found at the beginning of this script and rerun.
echo SET SOURCE_CONTROL_VALIDATION=N
echo ------------------------------------------------
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
