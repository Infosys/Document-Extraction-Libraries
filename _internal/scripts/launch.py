# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import subprocess
from pathlib import Path

# Global variables for root directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INFY_DB_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_db_service/src")
INFY_MODEL_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_model_service/src")
INFY_RESOURCE_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_resource_service/src")
INFY_SEARCH_SERVICE_DIR = os.path.join(BASE_DIR, "../../services/infy_search_service/src")
INFY_SEARCH_SERVICE_TOOL_DIR = os.path.join(BASE_DIR, "../../tools/infy_search_service_tool/packaging")
INFY_DPP_PROCESSOR_APP_DIR = os.path.join(BASE_DIR, "../../apps/infy_dpp_processor")
INFY_DPP_EVAL_PROCESSOR_APP_DIR = os.path.join(BASE_DIR, "../../apps/infy_dpp_eval_processor")

def list_apps():
    """List available DEL applications."""
    apps = {
        "Apps": [
            "infy_dpp_processor",
            "infy_dpp_eval_processor"
        ],
        "Services": [
            "infy_model_service",
            "infy_resource_service",
            "infy_db_service",
            "infy_search_service"
        ],
        "Tools": [
            "infy_search_service_tool"
        ]
    }
    return apps

def open_cmd_window(selected_app, command, env_vars):
    """Open a new command window and run the specified command."""
    try:
        print(f"Running command for {selected_app}: {command}")
        subprocess.Popen(f"start cmd /k \"{command}\"", env=env_vars, shell=True)
        print(f"Command window opened for: {selected_app}")
    except Exception as e:
        print(f"Failed to open command window: {e}")
 
def get_script_command(script_name, script_path):
    """Get the command to run the script based on the script name."""
    base_command = f".venv\\Scripts\\python.exe {script_path}"
    config_paths = {
        "dpp_indexing_pipeline_sequential": r"\data\config\dpp_pipeline_index_input_config.json",
        "dpp_indexing_pipeline_parallel": r"\data\config\dpp_tf_parallel_pipeline_index_input_config_data.json",
        "dpp_synthetic_data_generation_pipeline": r"\data\config\dpp_pipeline_idx_gen_input_config.json",
        "dpp_synthetic_data_evaluation_pipeline": r"\data\config\dpp_tf_pipeline_qna_truth_data_eval_input_config.json",
        "dpp_rag_evaluation_pipeline": r"\data\config\dpp_tf_pipeline_rag_evaluation.json"
    }
    if script_name in config_paths:
        return f"{base_command} --dpp_config_file_path {config_paths[script_name]} --dpp_deployment_config_path ..\..\_internal\scripts\dpp_deployment_config.json"
    return base_command
       
def show_script_menu(app_dir, selected_app):
    """Show a menu to select a script to run for apps."""
    scripts = {
        "infy_dpp_processor": {
            "1": ("dpp_indexing_pipeline_sequential", os.path.abspath(os.path.join(BASE_DIR, "dpp_pipeline_executor_cli.py"))),
            "2": ("dpp_indexing_pipeline_parallel", os.path.abspath(os.path.join(BASE_DIR, "dpp_pipeline_executor_cli.py")))
        },
        "infy_dpp_eval_processor": {
            "1": ("dpp_synthetic_data_generation_pipeline", os.path.abspath(os.path.join(BASE_DIR, "dpp_pipeline_executor_cli.py"))),
            "2": ("dpp_synthetic_data_evaluation_pipeline", os.path.abspath(os.path.join(BASE_DIR, "dpp_pipeline_executor_cli.py"))),
            "3": ("dpp_rag_evaluation_pipeline", os.path.abspath(os.path.join(BASE_DIR, "dpp_pipeline_executor_cli.py")))
        }
    }

    print("\nSelect a script to run:")
    for key, (name, path) in scripts[selected_app].items():
        print(f"{key}. {name}")

    while True:
        choice = input("\nEnter the number of the script you want to run (or 0 to go back): ")
        if choice == "0":
            return False
        if choice in scripts[selected_app]:
            script_name, script_path = scripts[selected_app][choice]
            command = get_script_command(script_name, script_path)
            open_cmd_window(script_name, command, os.environ.copy())
            break
        else:
            print("Invalid choice. Please select a valid script number.")
    return True

def load_env_file(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def main():
    """Main function to launch applications."""
    print("DEL Apps Launcher\n")
    print("NOTE: Make sure you have created the virtual environment and installed the required dependencies in the respective apps, services, and tools.")
    
    root_dirs = {
        "infy_model_service": INFY_MODEL_SERVICE_DIR,
        "infy_resource_service": INFY_RESOURCE_SERVICE_DIR,
        "infy_db_service": INFY_DB_SERVICE_DIR,
        "infy_search_service": INFY_SEARCH_SERVICE_DIR,
        "infy_search_service_tool": INFY_SEARCH_SERVICE_TOOL_DIR,
        "infy_dpp_processor": INFY_DPP_PROCESSOR_APP_DIR,
        "infy_dpp_eval_processor": INFY_DPP_EVAL_PROCESSOR_APP_DIR
    }
    
    apps = list_apps()
    print("\nSelect an app to run:")
    index = 1
    for category, app_list in apps.items():
        print(f"\n{category}:")
        for app in app_list:
            print(f"{index}. {app}")
            index += 1

    while True:
        try:
            choice = int(input("\nEnter the number of the app you want to run (or 0 to exit): "))
            if choice == 0:
                break
            if 1 <= choice < index:
                selected_app = None
                for app_list in apps.values():
                    if choice <= len(app_list):
                        selected_app = app_list[choice - 1]
                        break
                    choice -= len(app_list)
                
                app_dir = root_dirs[selected_app]
                os.chdir(app_dir)

                env_path = Path(app_dir).parent / ".env"
                if env_path.exists():
                    load_env_file(env_path)
                    
                if selected_app in ["infy_dpp_processor", "infy_dpp_eval_processor"]:
                    if not show_script_menu(app_dir, selected_app):
                        continue
                elif selected_app in ["infy_db_service", "infy_search_service", "infy_resource_service"]:
                    command = f"..\\.venv\\Scripts\\python.exe main.py"
                    open_cmd_window(selected_app, command, os.environ.copy())
                elif selected_app == "infy_model_service":
                    command = f"..\\.venv\\Scripts\\activate && ray stop && ray start --head --num-cpus=3 --num-gpus=0 --dashboard-host 0.0.0.0 && serve run config.yaml" 
                    open_cmd_window(selected_app, command, os.environ.copy())
                elif selected_app == "infy_search_service_tool":
                    command = f".\\.venv\\Scripts\\activate && infy_search_service_tool start" 
                    open_cmd_window(selected_app, command, os.environ.copy())    
                
            else:
                print("Invalid choice. Please select a valid app number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()