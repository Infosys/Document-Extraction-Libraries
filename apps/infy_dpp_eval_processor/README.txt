Build Package:
--------------
Before building the package please add values for DPP_STORAGE_ACCESS_KEY and DPP_STORAGE_SECRET_KEY in .env.tf file.

Testing:
--------
1. From command prompt activate virtual environment.
2. cd to scr folder
3. Keep input files and config files in correct folder (check script for folder path)
4. Run the script for indexing or inferencing pipeline.

If Testing in VM: uncomment below in src\app_dpp_container_external.py
root_dir = '/tmp/dpp_processor_container' #os.environ.get('CONTAINER_ROOT_PATH')