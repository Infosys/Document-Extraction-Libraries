#!/bin/bash
#For Docker Container testing parallel segment generator nodes.

# Save the current directory
original_dir=$(pwd)
# Change the current directory to the src directory
# cd "./src"

export DPP_STORAGE_ROOT_URI=s3://docwb-engg/dev/STORAGE
export DPP_STORAGE_SERVER_URL=<Provide s3 bucket URL>
export LOG_FILE_NAME="indexer"
export LOG_LEVEL="DEBUG"
# Array of processor names
processors=("request_creator" "metadata_extractor" "content_extractor" "segment_generator_pdfbox" "segment_generator_pdf_table_extract"  "segment_generator_pdf_img_extract" "segment_consolidator" "segment_classifier" "page_column_detector" "segment_merger" "Segment_sequencer" "chunk_generator" "db_indexer" "request_closer")
# Initial previous response file path
prev_response_file_path="NULL"
seg_gen_response_file_path_1="NULL"
seg_gen_response_file_path_2="NULL"
seg_gen_response_file_path_3="NULL"

#input_config_file_path = "/data/config/dpp_tf_parallel_pipeline_index_input_config_data.json"
# Counter
counter=0

# Loop over processors
for processor in "${processors[@]}"; do
    # Increment counter
    ((counter++))

    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "Running script # $counter : $processor"
    # echo "prev_response_file_path=$prev_response_file_path"

    # Run the command
    if [ "$processor" == "segment_consolidator" ]; then
        command="python app_dpp_container_external.py --processor_name \"$processor\" --input_config_file_path \"/data/config/dpp_tf_parallel_pipeline_index_input_config_data.json\" --prev_proc_response_file_path \"$seg_gen_response_file_path_1\" --prev_proc_response_file_path_2 \"$seg_gen_response_file_path_2\" --prev_proc_response_file_path_3 \"$seg_gen_response_file_path_3\""
    else
        command="python app_dpp_container_external.py --processor_name \"$processor\" --input_config_file_path \"/data/config/dpp_tf_parallel_pipeline_index_input_config_data.json\" --prev_proc_response_file_path \"$prev_response_file_path\""
    fi
    
    echo "$command"

    output=$(eval $command)

    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "An error occurred while running the script for $processor. Exiting."
        break
    fi

    # Print the output
    echo "Output of script ($processor):"
    echo "$output"

    if [ "$processor" == "segment_generator_pdfbox" ]; then
        seg_gen_response_file_path_1=$(echo $output | grep -oP 'response_file_path=\K(.*)')
    elif [ "$processor" == "segment_generator_pdf_table_extract" ]; then
        seg_gen_response_file_path_2=$(echo $output | grep -oP 'response_file_path=\K(.*)')
    elif [ "$processor" == "segment_generator_pdf_img_extract" ]; then
        seg_gen_response_file_path_3=$(echo $output | grep -oP 'response_file_path=\K(.*)')
    else
        # Extract the response file path from the output for the next iteration
        prev_response_file_path=$(echo $output | grep -oP 'response_file_path=\K(.*)')
    fi

    # Extract the status from the output
    status=$(echo $output | grep -oP 'status=\K(\w+)')

    # Check if the status is "failure"
    if [ "$status" == "failure" ]; then
        echo "The script for $processor failed. Exiting."
        break
    fi

    echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    echo ""
done

# Change back to the original directory
cd "$original_dir"