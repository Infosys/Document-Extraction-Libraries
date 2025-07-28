:: =============================================================================================================== *
:: Copyright 2025 Infosys Ltd.                                                                                     *
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
echo.


echo.
echo Deleting build related folders as part of clean up
for /d %%i in (.\dist) do rmdir /s /q "%%i"
for /d %%i in (.\build) do rmdir /s /q "%%i"
for /d %%i in (.\*.egg-info) do rmdir /s /q "%%i"
echo.
echo Cleanup complete
echo. 

echo.
python -m build --wheel

echo.
echo Deleting build related folders as part of clean up
for /d %%i in (.\build) do rmdir /s /q "%%i"
for /d %%i in (.\*.egg-info) do rmdir /s /q "%%i"
echo.
echo Cleanup complete
echo. 

pause

