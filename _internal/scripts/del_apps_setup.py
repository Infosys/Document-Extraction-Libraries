# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "del_apps_setup.json")
INFY_DPP_PROCESSOR_DIR = os.path.join(BASE_DIR, "../../apps/infy_dpp_processor")
INFY_DPP_EVAL_PROCESSOR_DIR = os.path.join(BASE_DIR, "../../apps/infy_dpp_eval_processor")

def list_apps():
    """List available DEL applications."""
    apps = [
        "infy_dpp_processor",
        "infy_dpp_eval_processor"
    ]
    return apps

def load_config():
    """Load the configuration from the JSON file."""
    with open(CONFIG_FILE_PATH, 'r') as file:
        config = json.load(file)
    return config

def prompt_overwrite(file_path):
    """Prompt the user to overwrite the file if it exists."""
    if os.path.exists(file_path):
        while True:
            response = input(f"{file_path} already exists. Do you want to overwrite it? (y/n): ").lower()
            if response in ['y', 'n']:
                return response == 'y'
            print("Invalid input. Please enter 'y' or 'n'.")
    return True

def setup_app_config(app_name, config):
    """Move the service config files and prompt templates for the respective app."""
    app_config = config.get(app_name, {})
    dest_dir = "C:/del/fs/appuc/STORAGE/data/config"

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    if app_name == "infy_dpp_processor":
        # Copy config files
        for config_file in app_config.get("config_file_path", []):
            src = os.path.abspath(os.path.join(INFY_DPP_PROCESSOR_DIR, config_file))
            dest = os.path.join(dest_dir, os.path.basename(config_file))
            if prompt_overwrite(dest):
                shutil.copy(src, dest)
                print(f"Copied config file to: {dest}")

        # Copy prompt templates
        for prompt_template in app_config.get("prompt_template_path", []):
            src = os.path.abspath(os.path.join(INFY_DPP_PROCESSOR_DIR, prompt_template))
            dest = os.path.join(dest_dir, os.path.basename(prompt_template))
            if os.path.isdir(src):
                if prompt_overwrite(dest):
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    print(f"Copied prompt template to: {dest}")
            else:
                if prompt_overwrite(dest):
                    shutil.copy(src, dest)
                    print(f"Copied prompt template to: {dest}")

        # Display dataset menu
        dataset_menu(app_config, app_name)
    elif app_name == "infy_dpp_eval_processor":
        # Copy config files
        for config_file in app_config.get("config_file_path", []):
            src = os.path.abspath(os.path.join(INFY_DPP_EVAL_PROCESSOR_DIR, config_file))
            dest = os.path.join(dest_dir, os.path.basename(config_file))
            if prompt_overwrite(dest):
                shutil.copy(src, dest)
                print(f"Copied config file to: {dest}")

        # Copy prompt templates
        for prompt_template in app_config.get("prompt_template_path", []):
            src = os.path.abspath(os.path.join(INFY_DPP_EVAL_PROCESSOR_DIR, prompt_template))
            dest = os.path.join(dest_dir, os.path.basename(prompt_template))
            if os.path.isdir(src):
                if prompt_overwrite(dest):
                    shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    print(f"Copied prompt template to: {dest}")
            else:
                if prompt_overwrite(dest):
                    shutil.copy(src, dest)
                    print(f"Copied prompt template to: {dest}")

        # Display dataset menu
        dataset_menu(app_config, app_name)

def dataset_menu(app_config, app_name):
    """Display the dataset menu and copy the selected dataset."""
    datasets = app_config.get("dataset_path", {})
    if not datasets:
        print("No datasets available.")
        return

    print("\nSelect a dataset to copy:")
    dataset_keys = list(datasets.keys())
    for i, key in enumerate(dataset_keys, start=1):
        print(f"{i}. {key}")

    while True:
        try:
            choice = int(input("\nEnter the number of the dataset you want to copy (or 0 to go back): "))
            if choice == 0:
                break
            if 1 <= choice <= len(dataset_keys):
                selected_dataset = dataset_keys[choice - 1]
                copy_dataset_files(selected_dataset, datasets[selected_dataset], app_name)
            else:
                print("Invalid choice. Please select a valid dataset number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def copy_dataset_files(dataset_name, dataset_paths, app_name):
    """Copy the dataset files to the input directory."""
    dest_dir = "C:/del/fs/appuc/STORAGE/data/input"

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    if app_name == "infy_dpp_processor":
        for dataset_file in dataset_paths:
            src = os.path.abspath(os.path.join(BASE_DIR, dataset_file))
            dest = os.path.join(dest_dir, os.path.basename(dataset_file))
            if prompt_overwrite(dest):
                shutil.copy(src, dest)
                print(f"Copied {dataset_name} file to: {dest}")
    elif app_name == "infy_dpp_eval_processor":
        for dataset_file in dataset_paths:
            src = os.path.abspath(os.path.join(BASE_DIR, dataset_file))
            dest = os.path.join(dest_dir, os.path.basename(dataset_file))
            if prompt_overwrite(dest):
                shutil.copy(src, dest)
                print(f"Copied {dataset_name} file to: {dest}")
 
def main():
    """Main function to launch applications."""
    print("DEL Application Setup\n")
    
    config = load_config()
    apps = list_apps()
    print("Select an app to setup:")
    for i, app in enumerate(apps, start=1):
        print(f"{i}. {app}")

    while True:
        try:
            choice = int(input("\nEnter the number of the app you want to setup (or 0 to exit): "))
            if choice == 0:
                break
            if 1 <= choice <= len(apps):
                selected_app = apps[choice - 1]
                setup_app_config(selected_app, config)
            else:
                print("Invalid choice. Please select a valid app number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()