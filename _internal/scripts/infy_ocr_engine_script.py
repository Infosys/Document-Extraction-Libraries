# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import subprocess

def download_tesseract_data():
    target_directory = "C:\\del\\ai\\models\\tessdata"
    if os.path.exists(target_directory):
        overwrite = input(f"The directory {target_directory} already exists. Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
    else:
        os.makedirs(target_directory)
    commands = [
        f"curl -L -o {os.path.join(target_directory, 'eng.traineddata')} https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/eng.traineddata"
    ]

    for command in commands:
        try:
            subprocess.run(command, check=True, shell=True)
            print(f"Executed: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute: {command}\nError: {e}")

def build_and_copy_jar():
    ocr_engine_library_path = "libraries/InfyOcrEngineJAR"
    os.chdir(ocr_engine_library_path)

    target_directory = "C:\\del\\programfiles\\InfyOcrEngine"
    if os.path.exists(target_directory):
        overwrite = input(f"The directory {target_directory} already exists. Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
        
    commands = [
        ".\\BuildJAR.bat",
        f"mkdir {target_directory}",
        f"copy .\\target\\EXECUTABLE\\*.jar {target_directory}\\"
    ]

    for command in commands:
        try:
            subprocess.run(command, check=True, shell=True)
            print(f"Executed: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute: {command}\nError: {e}")

if __name__ == "__main__":
    download_tesseract_data()
    build_and_copy_jar()
