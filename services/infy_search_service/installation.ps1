# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
"""Creation of Virtual Environment & Installation of Dependencies"""

$userInput = Read-Host "Do you want to create a virtual environment & install required dependencies? (y/n)"

if ($userInput -eq "y") {
    python -m venv .venv
    Write-Host "Virtual environment created."
    . .\.venv\Scripts\Activate

    python -m pip install --upgrade pip
    Write-Host "Pip upgraded to latest version."

    pip install -r requirements.txt
    Write-Host "Dependencies installed from requirements.txt."
} else {
    Write-Host "Exiting script."
}
pause