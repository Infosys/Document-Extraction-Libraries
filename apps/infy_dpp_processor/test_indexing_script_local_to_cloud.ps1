# SCRIPT for basic indexing -from local machine using cloud storage

# 1. create input folder and put file in s3://docwb-engg/dev/STORAGE/data/input and config files manually
# 2. in .env file provide values against DPP_STORAGE_ACCESS_KEY= and DPP_STORAGE_SECRET_KEY=
# 3.Activate virtual env and run this script
# Change the current directory to the src directory
Set-Location -Path "./src"

$env:DPP_STORAGE_ROOT_URI = "s3://docwb-engg/dev/STORAGE"
$env:DPP_STORAGE_SERVER_URL = "<Provide s3 bucket URL>"
# $env:CONTAINER_ROOT_PATH = "C:/dpp_demo"
$env:LOG_FILE_NAME = "indexer_local_to_cloud"

# Array of processor names
$processors = "request_creator", "metadata_extractor", "content_extractor", "segment_generator", "segment_consolidator", "segment_classifier", "page_column_detector", "segment_merger", "Segment_sequencer", "chunk_generator", "db_indexer", "request_closer"

# Initial previous response file path
$prev_response_file_path = "NULL"

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
    $command = "python app_dpp_container_external.py --processor_name `"$processor`" --input_config_file_path `"/data/config/dpp_pipeline_index_input_config.json`" --prev_proc_response_file_path `"$prev_response_file_path`""
    
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

    # Extract the response file path from the output for the next iteration
    $prev_response_file_path = [regex]::match($output, 'response_file_path=(.*)').Groups[1].Value

    Write-Host "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    Write-Host ""
}