# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import subprocess
import hashlib

def download_tiktoken_encoding():
    target_directory = "C:/del/ai/models/tiktoken_encoding"
    file_url = 'https://openaipublic.blob.core.windows.net/encodings/p50k_base.tiktoken'
    
    hash_value = hashlib.sha1(file_url.encode()).hexdigest()
    file_path = os.path.join(target_directory, f"{hash_value}")

    if os.path.exists(target_directory):
        overwrite = input(f"The directory {target_directory} already exists. Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
    else:
        os.makedirs(target_directory)

    commands = [
        f"curl -L -o {file_path} {file_url}"
    ]

    for command in commands:
        try:
            subprocess.run(command, check=True, shell=True)
            print(f"Executed: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute: {command}\nError: {e}")
            
if __name__ == "__main__":
    download_tiktoken_encoding()