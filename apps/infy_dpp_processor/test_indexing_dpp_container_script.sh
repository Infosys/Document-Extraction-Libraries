#!/bin/bash
#SCRIPT - From Docker Container basic indexing pipeline testing (login to AI cloud VM make DEL indexing docker image and then run this script)
# 1. create input folder and put file in s3://docwb-engg/dev/STORAGE/data/input and 
# 2. manually keep config files from apps\infy_dpp_processor\config\dev\ at s3://docwb-engg/dev/STORAGE/data/config
# 3. in .env file provide values against DPP_STORAGE_ACCESS_KEY= and DPP_STORAGE_SECRET_KEY=
############### INDEXER PIPELINE ##############################

export DPP_STORAGE_ROOT_URI=s3://docwb-engg/dev/STORAGE
export DPP_STORAGE_SERVER_URL=<Provide s3 bucket URL>
# export CONTAINER_ROOT_PATH=/home/data
export LOG_FILE_NAME=indexer
#"content_extractor"
# Array of processor names
processors=("request_creator" "metadata_extractor"  "content_extractor" "segment_generator" "segment_consolidator" "segment_classifier" "page_column_detector" "segment_merger" "Segment_sequencer" "chunk_generator" "chunk_saver" "data_encoder" "request_closer" ) 

# Initial previous response file path
prev_response_file_path="NULL"
# Counter
counter=0
# Loop over processors
for processor in "${processors[@]}"; do
    # Increment counter
    ((counter++))
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "Running script # $counter : $processor" 
    echo "prev_response_file_path=$prev_response_file_path"
    # Run the command
    command="python app_dpp_container_external.py --processor_name \"$processor\" --input_config_file_path \"/data/config/dpp_pipeline_index_input_config.json\" --prev_proc_response_file_path \"$prev_response_file_path\""

    echo "$command"
    # output=$command
    output=$(python app_dpp_container_external.py --processor_name "$processor" --input_config_file_path "/data/config/dpp_pipeline_index_input_config.json" --prev_proc_response_file_path "$prev_response_file_path")
    
    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "An error occurred while running the script for $processor. Exiting."
        break
    fi

    # Print the output
    echo "Output of script ($processor):"
    echo "$output"
    
    # Extract the response file path from the output for the next iteration
    prev_response_file_path=$(echo "$output" | grep -oP 'response_file_path=\K.*')
    echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    echo ""
done
