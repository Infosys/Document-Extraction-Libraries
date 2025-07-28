# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import glob
import os
from IPython.display import display, Markdown
from _internal_utils.pipeline_visualizer import PipelineVisualizer

class PipelineHelper():
    
    def __init__(self, pipeline_input_config_file_path, storage_root_path, container_root_path):
        self.__pipeline_input_config_file_path = storage_root_path + pipeline_input_config_file_path
        self.__pipeline_file_name = os.path.basename(self.__pipeline_input_config_file_path)
        self.__storage_root_path = storage_root_path
        with open(self.__pipeline_input_config_file_path, 'r') as f:
            data = json.load(f)
        self.__data = data
        
    def show_pipeline_card(self):
        storage_root_path = self.__storage_root_path
        pipeline_input_config_file_path = self.__pipeline_input_config_file_path
        data = self.__data 
        nodes = self.__create_graph_nodes()
        # print('nodes =', nodes)
        pv = PipelineVisualizer(nodes)
        img_html= pv.get_img_html()
        
        DESCRIPTION=f"""      
<sub><b>  >>>>>>>>>>>>>>> PIPELINE CARD >>>>>>>>>>>>>>> </b></sub>
<div style='background-color:#feffdf; padding:10px'>

## Pipeline: `{self.__pipeline_file_name}`

**Pipeline config File Path (absolute):** `{pipeline_input_config_file_path}`  
**Pipeline Name:** {data['name']}  
**Description:** {data['description']}  
**Graph:**
{img_html}

**No. of steps:** {len(data['processor_list'])} |
**No. of steps enabled:** {len( [x for x in data['processor_list'] if x['enabled']])} |
**No. of steps disabled:** {len( [x for x in data['processor_list'] if not x['enabled']])}  
**Pipeline input:**  
{self.__describe_flow(data, 'RequestCreator')}  
**Pipeline output:**  
{self.__describe_flow(data, 'RequestCloser')}   

**Pipeline workflow:**  
{self.__describe_flow(data, 'Workflow')}  
**Start conditions:**  
{self.__describe_flow(data, 'StartConditions')}  
</div>
<sub><b>  <<<<<<<<<<<<<<< PIPELINE CARD <<<<<<<<<<<<<<< </b></sub>
            """
        display(Markdown(DESCRIPTION))
        
    
    def __create_graph_nodes(self):
        data = self.__data
        nodes = []        
        processors =data['processor_list']
        max_length = len(processors)
        # print('max_length =', max_length)
        for idx ,proc in enumerate(processors):
            idx_base_1 = idx+1
            # print(idx, proc)
            step_name = f"{proc['processor_name']}\n({idx_base_1})"
            step_name = step_name.replace("_","_\n")
            if idx+1 == max_length:
                next_nodes = []
            else:
                next_step_name =  f"{processors[idx+1]['processor_name']}\n({idx_base_1+1})"
                next_step_name = next_step_name.replace("_","_\n")
                # next_nodes = [processors[idx+1]['processor_name']]
                next_nodes = [next_step_name]
            if not proc['enabled']:
                status = 'Disabled'
            else:
                status = "Scheduled"
            nodes.append({
                "name": step_name,
                "status": status,
                "nodes": next_nodes
            })
        
#         max_length = 10
#         for i in range(1,max_length+1):
#             status = None # Scheduled, Running, Cancelled, Completed, Failed
#             if i==5:
#                 status = "Running"
#             elif i>5:
#                 status = "Scheduled"
#             else:
#                 status = "Completed"
#             if i == max_length:
#                 next_nodes = []
#             else:
#                 next_nodes = [f"My\n process\n {i+1}"]
#             nodes.append({
#                 "name": f"My\n process\n {i}",
#                 "status": status,
#                 "nodes": next_nodes
#             })
        # nodes[0:2]
        return nodes
    
    def __get_files(self, storage_root_path, sub_folder_path, search_pattern ):
        pattern = storage_root_path + sub_folder_path + "/" + search_pattern 
        pattern = pattern.replace("//","/")        
        files = glob.glob(pattern)
        files = [x.replace("\\","/") for x in files]
        files = [x.replace("//","/") for x in files]
        files = [x.replace(storage_root_path + sub_folder_path + "/", "") for x in files ]
        return files
        

    def __describe_flow(self, pipeline_data, topic):
        storage_root_path = self.__storage_root_path
        DOCUMENT_ID_SAMPLE = 'D-XXX'
        GROUP_REQUEST_FILE_SAMPLE = 'G-XXX_group_request.json'
        GROUP_QUEUE_FOLDER_SAMPLE = 'G-XXX'
        description = ''
        request_creator_data = pipeline_data['processor_input_config']['RequestCreator']
        request_closer_data = pipeline_data['processor_input_config']['RequestCloser']
        input_folder_path = None
        new_request_file_path = None
        existing_request_file_read_path = None
        existing_request_file_save_path = None
        work_root_path = None
        if request_creator_data['from_data_file']['enabled']:
            input_folder_path = request_creator_data['from_data_file']['read_path']
            work_root_path = request_creator_data['from_data_file']['work_root_path']
            new_request_file_path =  request_creator_data['from_data_file']['to_request_file']['save_path']
        elif request_creator_data['from_request_file']['enabled']:
#           # TODO: This should come from 'from_request_file' section
            work_root_path = request_creator_data['from_data_file']['work_root_path']
            existing_request_file_read_path = request_creator_data['from_request_file']['read_path']
            existing_request_file_save_path = request_creator_data['from_request_file']['save_path']
        queue_folder_path = work_root_path + 'queue'
        
        output_folder_path = request_closer_data['data_file']['output_root_path']
        read_request_file_path = request_closer_data['from_request_file']['read_path']
        save_request_file_path = request_closer_data['from_request_file']['save_path']

        if topic == 'RequestCreator':
            if input_folder_path:
                description = f"One or more **data file(s)** (e.g. `*.pdf, *.jpg` or as per configuration) need to be present in `{input_folder_path}` folder " 
                description+= "*before* executing the pipeline. If no files are present, no processing will be done.  "
            elif existing_request_file_read_path:
                description = f"A previously run pipeline's **group request file** should be available in `{existing_request_file_read_path}` folder.  "
        elif topic == 'RequestCloser':
            description = "The original **data file** (e.g. `*.pdf, *.jpg` or as per configuration) and the extracted data (`document_data.json`) "
            description+= f"will be written to `{output_folder_path}{DOCUMENT_ID_SAMPLE}` folder.   "
            if work_root_path:
                description+= f"\nSupporting files generated during the processing will be written to "
                description+= f"`{work_root_path}{DOCUMENT_ID_SAMPLE}` folder "
        elif topic == "Workflow":
            if input_folder_path:
                description += f"1. Pick up a fixed number of **data file(s)** from `{input_folder_path}` folder, "
                description += f"generate a unique document ID and copy to `{work_root_path}{DOCUMENT_ID_SAMPLE}` folders.   "
                description += f"\n1. Create **group request file** `{new_request_file_path}/`**`{GROUP_REQUEST_FILE_SAMPLE}`** "
                description += f"containing the work location paths  "
            else:
                description += f"1. Pick up an existing **group request file** from `{existing_request_file_read_path}` folder.  "
                description += f"\n1. Move **group request file** to `{existing_request_file_save_path}` folder.  "
                
            description += f"\n1. Create a **group queue folder** `{queue_folder_path}/`**`{GROUP_QUEUE_FOLDER_SAMPLE}`** for the group request file "
            description += f"\n1. Add a file entry in the **group queue folder** for each **data file** to be processed.  "
            description += f"\n1. Do the processing for all the **data file(s)** picked up in current batch.  "
            description += f"\n1. Remove the file entry from **group queue folder** for each **data file** processed  "
            description += f"\n1. Move the **group request file** from `{read_request_file_path}/`**`{GROUP_REQUEST_FILE_SAMPLE}`** to "
            description += f"`{save_request_file_path}/`**`{GROUP_REQUEST_FILE_SAMPLE}`** "
        elif topic == 'StartConditions':
            can_be_started = False
            if input_folder_path:
                files = self.__get_files(storage_root_path, input_folder_path, "*.*")
                file_count = len(files)
                if file_count ==0:
                    description+= f"1. No **data file** found in `{input_folder_path}` folder.  "
                    description+= f"\n<b><span style='color:red'>Status: Failed</span></b>  "
                else:
                    description+= f"1. Found `{file_count}` **data file(s)** in `{input_folder_path}` folder.  "
                    description+= f"\nFile details: `{files}`   "
                    description+= f"\n<b><span style='color:green'>Status: Passed</span></b>"
                    can_be_started = True
            else:
                files = self.__get_files(storage_root_path, existing_request_file_read_path, "*.*")
                file_count = len(files)
                if file_count ==0:
                    description+= f"1. No expected **group request file** found in `{existing_request_file_read_path}` folder.  "
                    description+= f"\n<b><span style='color:red'>Status: Failed</span></b>  "
                    files = self.__get_files(storage_root_path, existing_request_file_save_path, "*.*")
                    file_count = len(files)
                    if file_count >0:
                        description+= f"\n<i><span style='color:blue'>"
                        description+= f"**Hint:** Found `{file_count}` **group request file(s)** in "
                        description+= f"`{existing_request_file_save_path}` indicating a (possible) **failed** previous run.  "
                        description+= f"\nFile details: `{files}`   "
                        description+= f"\nConsider moving one of them to `{existing_request_file_read_path}` folder."
                        description+= f"</span></i>  "
                    files = self.__get_files(storage_root_path, save_request_file_path, "*.*")
                    file_count = len(files)
                    if file_count >0:
                        description+= f"\n<i><span style='color:blue'>"
                        description+= f"**Hint:** Found `{file_count}` **group request file(s)** in "
                        description+= f"`{save_request_file_path}` indicating a **successful** previous run.  "
                        description+= f"\nFile details: `{files}`   "
                        description+= f"\nConsider moving one of them to `{existing_request_file_read_path}` folder."
                        description+= f"</span></i>  "
                else:
                    description+= f"1. Found `{file_count}` expected **group request file(s)** in `{existing_request_file_read_path}` folder.   "
                    description+= f"\nFile details: `{files}`   "
                    description+= f"\n<b><span style='color:green'>Status: Passed</span></b>"
                    group_queue_folder_names = self.__get_files(storage_root_path, queue_folder_path, "*")
                    matches_found_list = []
                    for group_request_file in files:
                        group_request_id = group_request_file.split('_group_request.json')[0]                 
                        if group_request_id in group_queue_folder_names:
                            matches_found_list.append(queue_folder_path + "/" + group_request_id)
                    if not matches_found_list:
                        can_be_started = True
                    else:
                        description+= f"\n1. Found unexpected **group queue folder(s)** : `{matches_found_list}`   "
                        description+= f"\n<b><span style='color:red'>Status: Failed</span></b>  "
                        description+= f"\n<i><span style='color:blue'>"
                        description+= f"Hint: Consider deleting the folder corresponding to required **group queue folder**.  "
                        description+= f"</span></i>"
            if can_be_started:
                description+= "\n1. <b><span style='color:green'>Pipeline can be started.</span></b>"
            else:
                description+= "\n1. <b><span style='color:red'>Pipeline cannot be started under current conditions until issues are fixed.</span></b>"
                
        return description