#For testing indexing pipeline - parallel segment generator nodes -from local system & cloud storage.

$original_dir = Get-Location
# Change the current directory to the src directory
Set-Location -Path "./src"
$env:DPP_STORAGE_ROOT_URI = "s3://docwb-engg/dev/STORAGE"
$env:DPP_STORAGE_SERVER_URL = "<Provide s3 bucket URL>"
$env:LOG_FILE_NAME = "indexer_local_to_cloud"
$env:LOG_LEVEL = "DEBUG"
# $env:CONTAINER_ROOT_PATH = "C:/temp/unittest/infy_libraries_client/CONTAINER"


# Array of processor names
$processors = "request_creator", "metadata_extractor", "content_extractor", "segment_generator_pdfbox", "segment_generator_pdf_table_extract" , "segment_generator_pdf_img_extract",
"segment_consolidator", "segment_classifier", "page_column_detector", "segment_merger", "Segment_sequencer", "chunk_generator", "chunk_saver", "db_indexer", "request_closer"

# Initial previous response file path
$prev_response_file_path = "NULL"
$seg_gen_response_file_path_1 = "NULL"
$seg_gen_response_file_path_2 = "NULL"
$seg_gen_response_file_path_3 = "NULL"
# Counter
$counter = 0

# Loop over processors
foreach ($processor in $processors) {
    # Increment counter
    $counter++

    Write-Host ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    Write-Host "Running script # $counter : $processor"
    Write-Host "prev_response_file_path=$prev_response_file_path"

    # Run the command
    if ($processor -eq 'segment_consolidator') {
        $command = "python app_dpp_container_external.py --processor_name `"$processor`" --input_config_file_path `"/data/config/dpp_tf_parallel_pipeline_index_input_config_data.json`" --prev_proc_response_file_path `"$seg_gen_response_file_path_1`" --prev_proc_response_file_path_2 `"$seg_gen_response_file_path_2`" --prev_proc_response_file_path_3 `"$seg_gen_response_file_path_3`""
    }
    else {
        $command = "python app_dpp_container_external.py --processor_name `"$processor`" --input_config_file_path `"/data/config/dpp_tf_parallel_pipeline_index_input_config_data.json`" --prev_proc_response_file_path `"$prev_response_file_path`""
    }
    
    Write-Host "$command"

    $output = Invoke-Expression -Command $command

    # Check if the command was successful
    if ($LASTEXITCODE -ne 0) {
        Write-Host "An error occurred while running the script for $processor. Exiting."
        break
    }

    # Print the output
    Write-Host "Output of script ($processor):"
    Write-Host "$output"

    if ($processor -eq 'segment_generator_pdfbox') {
        $seg_gen_response_file_path_1 = [regex]::match($output, 'response_file_path=(.*)').Groups[1].Value
    }
    elseif ($processor -eq 'segment_generator_pdf_table_extract') {
        $seg_gen_response_file_path_2 = [regex]::match($output, 'response_file_path=(.*)').Groups[1].Value
    }
    elseif ($processor -eq 'segment_generator_pdf_img_extract') {
        $seg_gen_response_file_path_3 = [regex]::match($output, 'response_file_path=(.*)').Groups[1].Value
    }
    else {
        # Extract the response file path from the output for the next iteration
        $prev_response_file_path = [regex]::match($output, 'response_file_path=(.*)').Groups[1].Value
    }

    # Extract the status from the output
    $status = [regex]::match($output, 'status=(\w+)').Groups[1].Value

    # Check if the status is "failure"
    if ($status -eq 'failure') {
        Write-Host "The script for $processor failed. Exiting."
        break
    }

    Write-Host "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    Write-Host ""
}

# Change back to the original directory
Set-Location -Path $original_dir
