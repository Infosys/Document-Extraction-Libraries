# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

$SERVICE_DIR = "..\infy_search_service"
$DIST_PATH = ".\dist\search_service_ui\browser"

# Print user-defined paths
Write-Host "Please check if these paths are correct:"
Write-Host "Search_service_dir = $SERVICE_DIR"
Write-Host "Angular_dir = $DIST_PATH"

# Ask for user confirmation
$IS_CORRECT = Read-Host -Prompt 'Do you want to proceed? (y/n)'
if ($IS_CORRECT -ne 'y') {
    pause
    exit
}

# Resolve the paths
$SERVICE_DIR = Resolve-Path $SERVICE_DIR
$DIST_PATH = Resolve-Path $DIST_PATH

# Check if the paths are valid
if (!(Test-Path $SERVICE_DIR)) {
    Write-Host "The path $SERVICE_DIR does not exist. Please check the path and try again."
    pause
    exit
}

if (!(Test-Path $DIST_PATH)) {
    Write-Host "The path $DIST_PATH does not exist. Please check the path and try again."
    pause
    exit
}

# Derived pathsc
$VENV_PATH = Join-Path $SERVICE_DIR ".venv"
$SERVICE_PATH = Join-Path $SERVICE_DIR "src\app_service.py"
$ENV_PATH = Join-Path $SERVICE_DIR ".env"

# Check if the derived paths are valid
if (!(Test-Path $VENV_PATH)) {
    Write-Host "The path $VENV_PATH does not exist. Please check the path and try again."
    pause
    exit
}

if (!(Test-Path $SERVICE_PATH)) {
    Write-Host "The path $SERVICE_PATH does not exist. Please check the path and try again."
    pause
    exit
}

if (!(Test-Path $ENV_PATH)) {
    Write-Host "The path $ENV_PATH does not exist. Please check the path and try again."
    pause
    exit
}

# Activate the virtual environment
. "$VENV_PATH\Scripts\Activate.ps1"

# Change to the directory containing the .env file
Set-Location -Path $SERVICE_DIR

# Load environment variables from .env file
python -c "from dotenv import load_dotenv; load_dotenv(r'$ENV_PATH')"

# Start the service in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit","-Command Write-Host 'Please open the following url to access the service: http://localhost:8004/api/v1/docs#/'; cd src; python $SERVICE_PATH"

# Serve the Angular application in the current PowerShell window
Set-Location -Path $DIST_PATH
Write-Host "Please open the following url to access the application: http://localhost:8005."
Start-Process "http://localhost:8005"
python -m http.server 8005

