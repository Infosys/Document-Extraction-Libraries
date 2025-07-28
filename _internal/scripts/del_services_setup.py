# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import subprocess
from dotenv import load_dotenv
from pathlib import Path
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INFY_RESOURCE_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_resource_service")
INFY_DB_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_db_service")
INFY_SEARCH_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_search_service")

def list_apps():
    """List available DEL applications."""
    apps = [
        "infy_resource_service",
        "infy_db_service",
        "infy_search_service"
    ]
    return apps

def prompt_overwrite(file_path):
    """Prompt the user to overwrite the file if it exists."""
    if os.path.exists(file_path):
        while True:
            response = input(f"{file_path} already exists. Do you want to overwrite it? (y/n): ").lower()
            if response in ['y', 'n']:
                return response == 'y'
            print("Invalid input. Please enter 'y' or 'n'.")
    return True

def setup_service(service_name):
    """Move the service config file for respective folder."""
    if service_name == "infy_resource_service":
        dest_dir = "C:/del/fs/services/resourcesvc/STORAGE/data/vectordb/resources"
        dest_config_file = ""
    elif service_name == "infy_db_service":
        config_file = os.path.abspath(os.path.join(INFY_DB_SERVICE_DIR, "config/external/infy_db_service_processor_input_config.json"))
        dest_dir = "C:/del/fs/services/dbsvc/STORAGE/data/config"
        dest_config_file = os.path.join(dest_dir, "infy_db_service_processor_input_config.json")
    elif service_name == "infy_search_service":
        config_file = os.path.abspath(os.path.join(INFY_SEARCH_SERVICE_DIR, "config/external/dpp_docwb_infy_search_service_processor_input_config.json"))
        prompts_folder = os.path.abspath(os.path.join(INFY_SEARCH_SERVICE_DIR, "config/external/prompt_templates"))
        dest_dir = "C:/del/fs/services/searchsvc/STORAGE/data/config"
        dest_config_file = os.path.join(dest_dir, "dpp_docwb_infy_search_service_processor_input_config.json")
        dest_prompts_folder = os.path.join(dest_dir, "prompt_templates")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory: {dest_dir}")
    
    if dest_config_file and prompt_overwrite(dest_config_file):
        shutil.copy(config_file, dest_config_file)
        print(f"Copied config file to: {dest_config_file}")
    
    if service_name == "infy_search_service" and os.path.exists(prompts_folder):
        if prompt_overwrite(dest_prompts_folder):
            shutil.copytree(prompts_folder, dest_prompts_folder)
            print(f"Copied prompts_template folder to: {dest_prompts_folder}")
    
def main():
    """Main function to launch applications."""
    print("DEL Services Setup\n")    
    apps = list_apps()
    print("Select a service to setup:")
    for i, app in enumerate(apps, start=1):
        print(f"{i}. {app}")

    while True:
        try:
            choice = int(input("\nEnter the number of the service you want to setup (or 0 to exit): "))
            if choice == 0:
                break
            if 1 <= choice <= len(apps):
                selected_app = apps[choice - 1]
                setup_service(selected_app)
            else:
                print("Invalid choice. Please select a valid service number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()