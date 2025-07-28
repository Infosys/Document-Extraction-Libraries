# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
""" This script is used to run the DPP pipelines. """
import os
import re
import sys
import json
import argparse
import traceback
import subprocess
from pathlib import Path
from urllib.parse import urlparse

INPUT_DATA_DICT = {
    "dpp_config_file_path": None,
    "dpp_deployment_config_path": None
}

def __parse_input():
    input_data_dict = INPUT_DATA_DICT.copy()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dpp_config_file_path", default=None, required=True)
    parser.add_argument("--dpp_deployment_config_path", default=None, required=True)
    args = parser.parse_args()
    input_data_dict['dpp_config_file_path'] = args.dpp_config_file_path
    input_data_dict['dpp_deployment_config_path'] = args.dpp_deployment_config_path
    return input_data_dict

def __load_config_file(file_path):
    def __replace_placeholders(config, variables):
        if isinstance(config, dict):
            return {k: __replace_placeholders(v, variables) for k, v in config.items()}
        elif isinstance(config, list):
            return [__replace_placeholders(i, variables) for i in config]
        elif isinstance(config, str):
            return re.sub(r'\$\{(\w+)\}', lambda match: variables.get(match.group(1), match.group(0)), config)
        else:
            return config

    with open(file_path, 'r') as f:
        config = json.load(f)
    variables = config.get('variables', {})
    return __replace_placeholders(config, variables)

def __flatten_processors(processors):
    flat_list = []
    for processor in processors:
        if 'processor_list' in processor:
            flat_list.extend(__flatten_processors(processor['processor_list']))
        else:
            flat_list.append(processor['processor_name'])
    return flat_list

def do_processing():
    input_data_dict = __parse_input()
    dpp_deployment_config_path = input_data_dict['dpp_deployment_config_path']
    dpp_config_file_path = input_data_dict['dpp_config_file_path']
    deployment_config = __load_config_file(dpp_deployment_config_path)
    
    parsed_uri = urlparse(deployment_config.get('variables').get('DPP_STORAGE_ROOT_URI'))
    config_file_path = parsed_uri.netloc + parsed_uri.path + dpp_config_file_path
    dpp_config = __load_config_file(config_file_path)

    processors_list = __flatten_processors(dpp_config.get('processor_list'))
    original_dir = Path.cwd()

    try:    
        counter = 0
        proc_response = {}
        
        for processor_name in processors_list:
            processor_config = deployment_config['processors'].get(processor_name)
            if not processor_config:
                print(f"No configuration found for processor: {processor_name}. Skipping.")
                continue

            prev_proc_command = ""
            prev_response_keys = [key for key in processor_config.get('args', {}).keys() if key.startswith('prev_proc_response_file_path')]
            use_parallel = any(key.endswith(f'_{i}') and processor_config['args'][key] in proc_response for i in range(1, len(prev_response_keys) + 1) for key in prev_response_keys)

            del_args_list = []
            for arg_key, arg_value in processor_config.get('args', {}).items():
                if arg_key.startswith('prev_proc_response_file_path'):
                    del_args_list.append(arg_value)
                    if arg_value != "NULL":
                        prev_response_value = proc_response.get(arg_value)
                        if prev_response_value:
                            processor_config['args'][arg_key] = prev_response_value
                    else:
                        processor_config['args'][arg_key] = "NULL"
            
            if use_parallel:
                for i in range(1, len(prev_response_keys) + 1):
                    key = f'prev_proc_response_file_path_{i}'
                    if key in processor_config['args']:
                        if i == 1:
                            prev_proc_command += f'--prev_proc_response_file_path "{processor_config["args"][key]}" '
                        else:
                            prev_proc_command += f'--{key} "{processor_config["args"][key]}" '
                        
                        for del_args in del_args_list:
                            if del_args in proc_response:
                                del proc_response[del_args]
            else:
                key = 'prev_proc_response_file_path'
                if key in processor_config['args']:
                    prev_proc_command += f'--{key} "{processor_config["args"][key]}" '
                        
            counter += 1
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(f"Running script # {counter} : {processor_name}")
            if use_parallel:
                for i in range(1, len(prev_response_keys) + 1):
                    key = f'prev_proc_response_file_path_{i}'
                    if key in processor_config['args']:
                        print(f"{key}={processor_config['args'][key]}")
            else:
                print(f"prev_proc_response_file_path={processor_config['args'].get('prev_proc_response_file_path', 'NULL')}")
            
            dpp_app_dir = processor_config.get('cli_controller_dir')
            cli_controller_file = processor_config.get('cli_controller_file')
            python_venv_path = processor_config.get('venv_script_dir')
            venv_activateion_cmd = processor_config.get('venv_activate_cmd')
            venv_activate_path = os.path.join(python_venv_path, venv_activateion_cmd)
            
            dpp_processor_docker_img_name = processor_config.get('env').get('container_img_name')
            selected_env = processor_config.get('env').get('env_type')
            dpp_storage_root_uri = processor_config.get('env').get('storage_root_uri')
            dpp_storage_server_url = processor_config.get('env').get('storage_root_url')
            log_file_name = processor_config.get('env').get('log_file_name')
            log_level = processor_config.get('env').get('log_level')
        
            os.environ["DPP_STORAGE_ROOT_URI"] = dpp_storage_root_uri
            os.environ["DPP_STORAGE_SERVER_URL"] = dpp_storage_server_url
            os.environ["LOG_FILE_NAME"] = log_file_name
            os.environ["LOG_LEVEL"] = log_level
            
            response_file_path = processor_config.get('output').get('variables').get('SYS_CONTROLLER_RES_FILE_PATH')
            previous_file_path = processor_config.get('output').get('variables').get('SYS_CONTROLLER_PREVIOUS_FILE_PATH')

            if selected_env == "dev":
                command = (
                    f"docker run -it "
                    f"-e LOG_FILE_NAME='{log_file_name}' "
                    f"-e DPP_STORAGE_ROOT_URI='{dpp_storage_root_uri}' "
                    f"-e DPP_STORAGE_SERVER_URL='{dpp_storage_server_url}' "
                    f"-e LOG_LEVEL='{log_level}' "
                    f"<your artifactory name>/{dpp_processor_docker_img_name} "
                    f"-c \"python {cli_controller_file} "
                    f"--processor_name '{processor_name}' "
                    f"--input_config_file_path '{dpp_config_file_path}' "
                    f"{prev_proc_command}"
                )
            elif selected_env == "local":
                os.chdir(f"../{dpp_app_dir}")
                venv_activate_path = os.path.abspath(venv_activate_path)
                os.chdir(f"./src")
                command = (
                    f'{venv_activate_path} {cli_controller_file} '
                    f'--processor_name "{processor_name}" '
                    f'--input_config_file_path "{dpp_config_file_path}" '
                    f'{prev_proc_command}'
                )
                    
            if selected_env == "dev":
                command += '"'
            print("\ncommand:", command)
            sub_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True, shell=True)
            stdout, stderr = sub_process.communicate()
            output = stdout
            print(f"\nOutput of ({processor_name}):{output}")
            os.chdir("../")
            if stderr:
                print(f"An error occurred while running the script for {processor_name}. Exiting.")
                print(f"\nError: {stderr}")

            match = re.search(f'{response_file_path}=(.*)', output)
            if match:
                proc_response[previous_file_path] = match.group(1).strip()
                
            status_match = re.search(r'status=(\w+)', output)
            if status_match:
                status = status_match.group(1).strip()
                if status == 'failure':
                    print(f"The script for {processor_name} failed. Exiting.")
                    break

            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print("")
    except subprocess.CalledProcessError as e:
        print("An error occurred while running the script. Exiting.")
        print(f"Exception: {e}")
        traceback.print_exc()
        raise e
    finally:
        os.chdir(original_dir)
    
if __name__ == '__main__':
    # sys.argv = ['dpp_pipeline_executor_cli.py',
    #             '--dpp_config_file_path',
    #             r'/data/config/dpp_pipeline_index_input_config.json',
    #             '--dpp_deployment_config_path',
    #             r'dpp_deployment_config.json'
    #         ]
    # sys.argv = ['dpp_pipeline_executor_cli.py',
    #             '--dpp_config_file_path',
    #             r'/data/config/dpp_tf_parallel_pipeline_index_input_config_data.json',
    #             '--dpp_deployment_config_path',
    #             r'dpp_deployment_config.json'
    #         ]
    # sys.argv = ['dpp_pipeline_executor_cli.py',
    #             '--dpp_config_file_path',
    #             r'/data/config/dpp_pipeline_idx_gen_input_config.json',
    #             '--dpp_deployment_config_path',
    #             r'dpp_deployment_config.json'
    #         ]
    # sys.argv = ['dpp_pipeline_executor_cli.py',
    #             '--dpp_config_file_path',
    #             r'/data/config/dpp_tf_pipeline_qna_truth_data_eval_input_config.json',
    #             '--dpp_deployment_config_path',
    #             r'dpp_deployment_config.json'
    #         ]
    # sys.argv = ['dpp_pipeline_executor_cli.py',
    #             '--dpp_config_file_path',
    #             r'/data/config/dpp_tf_pipeline_rag_evaluation.json',
    #             '--dpp_deployment_config_path',
    #             r'dpp_deployment_config.json'
    #         ]
    do_processing()