## Prerequisites:
- Python =3.11

## Testing:
It is implementation of inferencing pipeline. 
1. Create, activate virtual environment, and install the dependencies.
2. Look at `config.ini` file for `STORAGE_ROOT_PATH` and `dpp_input_config_file_path` and create path.    
e.g. Create C:/DPP/infy_libraries_client/STORAGE/
3. Copy config file from `\apps\config\dpp_docwb_infy_search_service_processor_input_config.json` to `STORAGE_ROOT_PATH`+`dpp_input_config_file_path`  
e.g. C:/DPP/infy_libraries_client/STORAGE/data/config/
dpp_docwb_infy_search_service_processor_input_config.json
4. If centralised db is being used to query from (i.e. indexed stored via infy_db_service), modify config file of infy_search_service: 
    * Enable `infy_db_service` under `vectordb` and `sparseindex` of _`QueryRetriever`_ and _`Reader`_ processor config 
    * Provide value for `db_service_url` under `storage` of `QueryRetriever` processor.  
        * For vectordb `http://<hostname>:8005/api/v1/vectordb/getmatches` 
        * For sparseindex `http://<hostname>:8005/api/v1/sparsedb/getmatches`.  
        (Replace the hostname from URL with your hostname).
        ```
        "QueryRetriever": {
                    "embedding": {},
                    "storage": {
                        "vectordb": {
                            "faiss": {},
                            "infy_db_service": {
                                "enabled": true,
                                "configuration": {
                                    "db_service_url": "http://localhost:8005/api/v1/vectordb/getmatches",
                                    "model_name": "",
                                    "index_id": "",
                                    "collections": [
                                        {
                                            "collection_name": "",
                                            "collection_secret_key": ""
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
                                    "db_service_url": "http://localhost:8005/api/v1/sparsedb/getmatches",
                                    "method_name": "",
                                    "index_id": "",
                                    "collections": [
                                        {
                                            "collection_name": "",
                                            "collection_secret_key": ""
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "hybrid_search": {
                        "rrf": {
                            "enabled": true
                        },
                    "queries": []
                }
        ```
5. At `variables` part of the config file provide respective LLM URL and Key to be used, under `Reader` processor for fetching answer.
6. When you run the code from local, run this in browser http://localhost:8004/api/v1/docs# 
7. Now use `http://localhost:8004/api/v1/inference/search` API by passing `question` and `index_id` (created at time of indexing pipeline; check `processor_response_data.json` file after running indexing pipeline for it).


## Build Package: 
1. Run `BuildPackage.bat`.
2. Package will be available at `apps\infy_search_service\target`.

## Deploy:
### Installation 
1. Copy the package from `apps\infy_search_service\target` to target server machine where you want to deploy.
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
### Firewall settings
1. Steps to follow for only the first time you are setting up the service.
* Update Firewall:  
( replace <port_number> with the port number used for this service in code)
  ```
  sudo firewall-cmd --zone=public --add-port=8004/tcp --permanent
  sudo firewall-cmd --reload
  ```
* Start in Foreground (for Verification):  
Make sure you are inside the service folder and run the following commands:
  ```
  export PYTHONPATH=`pwd`/src
  cd src
  python main.py
  ```


## Configure as Systemmd Service in Linux
1.  Copy the service file to the systemd directory:
  ```
  sudo cp infy_search_service.service /etc/systemd/system/
  ```
2. Verify the service file:
  ```
  sudo cat /etc/systemd/system/infy_search_service.service
  ```
3. Enable and start the service:
```
sudo systemctl enable infy_search_service.service
sudo systemctl daemon-reload
sudo systemctl start infy_search_service.service
sudo systemctl status infy_search_service.service
```

### Verification
Verify if the URL is working from browser.  
`http://<hostname>:8004/api/v1/docs`


