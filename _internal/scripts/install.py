# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import subprocess
import sys

def create_virtualenv():
    venv_dir = os.path.join(os.getcwd(), '.venv')
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment at {venv_dir}")
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual environment: {e}")
            sys.exit(1)
    else:
        print(f"Virtual environment already exists at {venv_dir}")

def upgrade_pip():
    venv_dir = os.path.join(os.getcwd(), '.venv')
    python_executable = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'python')

    if not os.path.exists(python_executable):
        print(f"Python executable not found in virtual environment at {venv_dir}")
        sys.exit(1)

    print(f"Upgrading pip in virtual environment at {venv_dir}")
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

def install_requirements():
    venv_dir = os.path.join(os.getcwd(), '.venv')
    pip_executable = os.path.join(venv_dir, 'Scripts', 'pip.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'pip')

    if not os.path.exists(pip_executable):
        print(f"pip executable not found in virtual environment at {venv_dir}")
        sys.exit(1)

    requirements_file = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(requirements_file):
        print(f"requirements.txt not found in the current directory")
        sys.exit(1)

    print(f"Installing packages from {requirements_file} into virtual environment")
    subprocess.check_call([pip_executable, 'install', '-r', requirements_file])
    print("Packages installed successfully")

if __name__ == "__main__":
    create_virtualenv()
    upgrade_pip()
    install_requirements()