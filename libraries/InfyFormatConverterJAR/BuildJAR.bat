:: =============================================================================================================== *
:: Copyright 2022 Infosys Ltd.                                                                                     *
:: Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at   * 
:: http://www.apache.org/licenses/                                                                                 *
:: =============================================================================================================== *

@echo off

@REM echo Invalidating Zulu Java path
@REM set path=%path:zulu=xxx%


echo.
echo Checking for JAVA
call java -version 1>nul
echo.
if %ERRORLEVEL% GEQ 1 GOTO JAVA_NOT_FOUND_ERROR
echo.
echo Checking for maven
call mvn -version 1>nul
if %ERRORLEVEL% GEQ 1 GOTO MAVEN_NOT_FOUND_ERROR
echo.
echo Building JAR file
call mvn clean package -P client -DskipTests
echo.
echo --------------------------------------------------------------------------------------------------
echo NOTE:
echo Copy .\target\EXECUTABLE\infy-format-converter-*.jar to C:/del/programfiles/InfyFormatConverter/infy-format-converter-*.jar
echo Make sure to keep only one currently generated jar file in the folder.
echo ------------------------------------------------------------------------------------------------
echo.
echo.

pause 
GOTO END

:JAVA_NOT_FOUND_ERROR
echo.
echo ERROR: Java not found. Please install and then re-run this script. 
echo.
pause 
GOTO END

:MAVEN_NOT_FOUND_ERROR
echo.
echo ERROR: Maven not found. Please install and then re-run this script. 
echo.
pause 
GOTO END

:END
endlocal