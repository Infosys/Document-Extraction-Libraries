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
7. If a elasticsearch instance is being used to store store indexes, then:
    ### Elasticsearch Setup:
    * To use Elasticsearch as a vector database, first set up your Elasticsearch database. By also setting up a Kibana instance, you can not only visualize the data stored in the Elasticsearch database but also easily create and manage roles and users. 
    * Below are the steps to create roles and users in Kibana:

    `Create Roles & Users`:
    * Login to your Kibana instance and go to the `Management` tab in the left side panel, then click on `Stack Management`. Under `Security` on the left side, you can find both `Roles` and `Users`.
    * We will create two roles, one for writing data and the other for reading data. We will also create two users, one for writing data and the other for reading data. This degree of separation is recommended so that the user who is writing data cannot read the data and the user who is reading data cannot accidentally write the data.
    * To create a role:
        - Click on `Roles` and then click on `Create Role`. Fill in the details as shown below and then click on `Save`.
        #### Role Name: role-del-write (write role)
        - `Role Name:` <_write_role_name_>
        - `Indices:` idx-del-*
        - `Privileges:` create_index, create_doc, create, manage
        #### Role Name: role-del-read (read role)    
        - `Role Name:` <_read_role_name_>
        - `Indices:` idx-del-*
        - `Privileges:` read, index
    * To create a user:
        - Click on `Users` and then click on `Create User`. Fill in the details as shown below and then click on `Save`.
        #### User Name: del-producer-1 (write user)
        - `Username:` <_name_>
        - `Password:` <_password_>
        - `Full name:` <_full_name_>
        - `Roles:` role-del-write
        #### User Name: del-consumer-1 (read user)
        - `Username:` <_name_>
        - `Password:` <_password_>
        - `Full name:` <_full_name_>
        - `Roles:` role-del-read, viewer
    #### NOTE:
    * Please make sure to replace the values of the fields enclosed in <> with the values you want to set, the names of the roles, users mentioned above are just for reference; you can name them anything you want.
    * Make sure the mentioned privileges and indices are set accordingly, else it might result in errors when indexing or querying.

    ### Indexing to elasticsearch:
    * To index the data to the Elasticsearch database, you need to enable elasticsearch under `DbIndexer`->`storage`->`vectordb`->`elasticsearch` in the config(keep others as disabled).
    * Modify indexing pipline input config file to `enable` _only_ `elasticsearch` under `vectordb` of `DbIndexer` processor config and provide the `db_server_url`, `username`, `password`, `cert_fingerprint`    and mention the `ca_certs_path` in the variables section at the top of the config.
    * Provide `index_name` and `enable` index under `DbIndexer` processor config.
    ```
    "DbIndexer": {
    "embedding": {},
    "index": {
            "enabled": true,
            "index_name": "<index_name>",
            "index_id": ""
        },
    "storage": {
        "vectordb": {
            "faiss": {},
            "infy_db_service": {},
            "elasticsearch": {
                "enabled": true,
                "configuration": {
                    "db_server_url": "<db_server_url>",
                    "username": "<username>",
                    "password": "<password>",
                    "verify_certs": "true",
                    "cert_fingerprint": "<cert_fingerprint>",
                    "ca_certs_path": "${CA_CERTS_PATH}"
                }
            }
        }
    }
    ```
    #### NOTE:
    * The `db_server_url` should be the url of the elasticsearch instance.
    * The `username` and `password` should be the credentials of the elasticsearch instance where the write roles are specified.
    * The `cert_fingerprint` should be the fingerprint of the ssl_certificate used by the elasticsearch instance.
    * The `ca_certs_path` should be the path to the ssl_certificate of the elasticsearch instance.
    * To obtain the ssl_certificate fingerprint, you can open your elasticsearch instance in your browser and click on the lock/site information icon in the address bar, then click on the certificate, a pop up will open which will allow you to export the certificate and save locally. You can then open the certificate file and in the details section there will be key called thumbprint which will have the fingerprint.
    * The fingerprint should be in the format of `xx:xx:xx:...`, if not just add `:` after every two characters.
    * As of now only vector indexes can be stored in elasticsearch.

8. Run the provided scripts for testing indexing pipeline. 
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
2.  Create docker image 
    ```
    docker build -t <ImageURI> .
    ```
3. If you want to run container using created docker image.
    ```
    docker run -it <ImageURI>
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





