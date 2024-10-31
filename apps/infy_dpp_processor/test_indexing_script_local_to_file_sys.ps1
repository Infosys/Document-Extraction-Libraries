#For testing basic indexing pipeline -from local system & local file system 

#Steps:Manually create C:\Temp\unittest\infy_dpp_processor\STORAGE 
#and from apps\infy_dpp_processor\config\dev\testing keep config file at below:
#1."C:\Temp\unittest\infy_dpp_processor\STORAGE\data\config\dpp_pipeline_index_input_config.json"
#2. and input files at C:\Temp\unittest\infy_dpp_processor\STORAGE\data\input\
# 3. in .env file provide values against DPP_STORAGE_ACCESS_KEY= and DPP_STORAGE_SECRET_KEY=
#activate virtual env then run below script

# Save the current directory
$original_dir = Get-Location
# Change the current directory to the src directory
Set-Location -Path "./src"
$env:DPP_STORAGE_ROOT_URI = "file://C:/temp/unittest/infy_dpp_processor/STORAGE"
$env:DPP_STORAGE_SERVER_URL = ""
$env:LOG_FILE_NAME = "indexer"
$env:LOG_LEVEL = "DEBUG"
# $env:CONTAINER_ROOT_PATH = "C:/temp/unittest/infy_libraries_client/CONTAINER"


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

# Change back to the original directory
Set-Location -Path $original_dir
