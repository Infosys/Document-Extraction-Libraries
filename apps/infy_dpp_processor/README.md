## Prerequisites:
- Python >=3.10 or <=3.11

## Testing:
It is implementation of indexing pipeline which by default stores indexes locally. 
1. From command prompt create, activate virtual environment, and install the dependencies using requirement.txt.    

2. Manually create below folders:  
    - For file system:  
        C:\Temp\unittest\infy_dpp_processor\STORAGE 
        C:\Temp\unittest\infy_dpp_processor\STORAGE\data\input
        C:\Temp\unittest\infy_dpp_processor\STORAGE\data\config  

    OR
    - For cloud storage:  
        Make `input` and `config` folder inside `data` folder relative to your cloud storage path i.e., `DPP_STORAGE_ROOT_URI` in script.

3. Keep input files and config files in correct folder (check script for config file names)

4. Based on from where you are running the script use/modify config file.  
    - Local system:    
        Take config files from `\config\dev\testing\`
    
    OR
    - Container image in VM:   
        Refer config files from `\config\dev\`

5. In .env files provide values against `DPP_STORAGE_ACCESS_KEY=` and `DPP_STORAGE_SECRET_KEY=`

6. If a centralized vector dB is being used to store indexes, then:
    * `infy_db_service` is expected to be running or deployed.
    * Modify indexing pipline input config file to `enable` _only_ `infy_db_service` under `vectordb`and `sparseindex` of `DbIndexer` processor config and provide the `db_service_url`.
    * Below URL's are supposed to added in config against `db_service_url`.(replace the hostname with your hostname where `infy_db_service` is deployed).
    *  http://<hostname>:8005/api/v1/sparsedb/saverecords
    *  http://<hostname>:8005/api/v1/vectordb/saverecords
    * Provide `index_name` and `enable` index under `DbIndexer` processor config.
    ```
    "DbIndexer": {
    "embedding": {},
    "index": {
            "enabled": true,
            "index_name": "",
            "index_id": ""
        },
    "storage": {
        "vectordb": {
            "faiss": {},
            "infy_db_service": {
                    "enabled": true,
                    "configuration": {
                    "db_service_url": "http://localhost:8005/api/v1/vectordb/saverecords",
                    "model_name": "all-MiniLM-L6-v2",
                    "collections": [
                        {
                        "collection_name": "documents",
                        "collection_secret_key": "",
                        "chunk_type": ""
                        }
                    ]
                    }
                }
            },
            "sparseindex": {
                "bm25s": {},
                "infy_db_service": {
                    "enabled": true,
                    "configuration": {
                    "db_service_url": "http://localhost:8005/api/v1/sparsedb/saverecords",
                    "method_name": "bm25s",
                    "collections": [
                        {
                        "collection_name": "documents",
                        "collection_secret_key": "",
                        "chunk_type": ""
                        }
                    ]
                    }
            }
            }
        }
    }
    ```
    * Indexing pipeline creates index_id
7. Run the provided scripts for testing indexing pipeline. 
e.g.`test_indexing_script_local_to_file_sys.ps1`
 > NOTE: While running indexing script ignore list index out of range error for now, in Content Extractor processor 

## Build Package 

1. Before building the package please add values for `DPP_STORAGE_ACCESS_KEY` and `DPP_STORAGE_SECRET_KEY` in `.env.tf` file.
2. Run `BuildPackage.bat`.
3. Package will be available at `apps\infy_dpp_processor\target`.

## Deploy Package as Docker container:
1. Copy the below folders to the machine where you have access to create a docker image.
- `apps\infy_dpp_processor\target`
- `MyProgramFiles` (refer `docs/notebook/src/use_cases/dpp/installation.ipynb`)  

    The folder structure should look as below:
    ```
    <folder_root_path>
            /dpp_processor_app
            /Dockerfile
            /MyProgramFiles
    ```
2. Create, activate virtual environment, and install packages.
3. Create docker image. 
    ```
    docker build -t <ImageURI> .
    ```


## Deploy Package to a Virtual Environment:
### MyProgramFiles folder creation
1. Create `MyProgramFiles` folder (refer `docs/notebook/src/use_cases/dpp/installation.ipynb`)

### Installation
1. Copy the package from `apps\infy_dpp_processor\target` to target server machine where you want to deploy.
2. Create and activate a virtual environment:
    ```
    python -m venv .venv
    source ./.venv/bin/activate
    ```
3. Upgrade pip:
    ```
    pip install --upgrade pip
    ```
4. Install required dependencies  
    ```
    pip install -r requirements.txt
    ```





