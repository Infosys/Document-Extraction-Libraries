# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
""" NLTK data setup script """
import os
import subprocess
import sys
import shutil

def create_venv_and_install_nltk():
    venv_dir = "._venv"
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    subprocess.check_call([os.path.join(venv_dir, "Scripts", "python"), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([os.path.join(venv_dir, "Scripts", "pip"), "install", "nltk"])
    return venv_dir

def run_script():
    print("Set the base directory for NLTK data(e.g: C:/del/ai): ")
    BASE_DIR = "C:/del/ai"

    print("Base directory: ", BASE_DIR)
    custom_dir = os.path.join(BASE_DIR, "nltk_data").replace("\\", "/")

    if not os.path.exists(custom_dir):
        os.makedirs(custom_dir)

    import nltk
    nltk.download('punkt', download_dir=custom_dir)
    nltk.download('stopwords', download_dir=custom_dir)
    nltk.data.path.append(custom_dir)
    print("NLTK data setup completed successfully.")
    
try:
    import nltk
except ImportError:
    response = input("The 'nltk' library is not installed.\nProceed by creating a dummy virtual environment and installing the library? (y/n): ")
    if response.lower() == 'y':
        venv_dir = create_venv_and_install_nltk()
        subprocess.check_call([os.path.join(venv_dir, "Scripts", "python"), __file__])
        shutil.rmtree(venv_dir)
        print("Deleting dummy virtual environment")
        exit(0)
    else:
        print("Operation cancelled.")
        exit(1)

run_script()
