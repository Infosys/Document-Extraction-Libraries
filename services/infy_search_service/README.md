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
4. Copy prompt_templates folder from `\docs\notebook\src\use_cases\dpp\data\sample\config\prompt_templates` to `STORAGE_ROOT_PATH`+`prompt_templates`.
e.g. C:/DPP/infy_libraries_client/STORAGE/data/config/prompt_templates
5. If centralised db is being used to query from (i.e. indexed stored via infy_db_service), modify config file of infy_search_service: 
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
6. If elastic search is used as the vectordb to query from, modify config file of infy_search_service:
    * To query the data stored in the Elasticsearch database via the search service. In the config you need to enable elasticsearch under `QueryRetriever*`->`storage`->`vectordb`->`elasticsearch`(keep others as disabled).
    * Provide value for `db_server_url`, `username`, `password`, `cert_fingerprint` and mention the `ca_certs_path` in the variables section at the top of the config.  
        ```
        "QueryRetriever": {
                    "embedding": {},
                    "storage": {
                        "vectordb": {
                            "faiss": {},
                            "infy_db_service": {},
                            "elasticsearch": {
                                "enabled": true,
                                "configuration": {
                                    "db_server_url": "",
                                    "username": "",
                                    "password": "",
                                    "verify_certs": "true",
                                    "cert_fingerprint": "",
                                    "ca_certs_path": "${CA_CERTS_PATH}",
                                    "index_id": ""
                                }
                            }
                        }
                    }
        }
        ```
    #### NOTE:
    * `db_server_url`: Provide the URL of the Elasticsearch server.
    * `username` & `password`: Provide the username and password where the read roles are specified.
    * `verify_certs`: Keep as true
    * The `cert_fingerprint` should be the fingerprint of the ssl_certificate used by the elasticsearch instance.
    * The `ca_certs_path` should be the path to the ssl_certificate of the elasticsearch instance.
    * To obtain the ssl_certificate fingerprint, you can open your elasticsearch instance in your browser and click on the lock/site information icon in the address bar, then click on the certificate, a pop up will open which will allow you to export the certificate and save locally. You can then open the certificate file and in the details section there will be key called thumbprint which will have the fingerprint.
    * The fingerprint should be in the format of `xx:xx:xx:...`, if not just add `:` after every two characters.
    * Please also enable elasticsearch under `Reader*`->`storage`->`vectordb`->`elasticsearch`(keep others as disabled).
    * As of now only vector search is supported from elasticsearch.
7. Switching between different data sources (e.g., `infy_db_service` or `elasticsearch`) is not possible once the application is running, as these are start-time configurations. Please make your selection carefully based on your requirements.
8. At `variables` part of the config file provide respective LLM URL and Key to be used, under `Reader` processor for fetching answer.
9. When you run the code from local, run this in browser http://localhost:8004/api/v1/docs# 
10. Now use `http://localhost:8004/api/v1/inference/search` API by passing `question` and `index_id` (created at time of indexing pipeline; check `processor_response_data.json` file after running indexing pipeline for it).


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


