## Prerequisites:
- Python =3.11

## Testing:
1. Create, activate virtual environment, and install the dependencies.
2. Look at `config.ini` file for `STORAGE_ROOT_PATH` and `model_details_path` and create path.  
e.g., Create C:/DPP/infy_libraries_client/STORAGE/
3. Copy config file from `\apps\config\dpp_docwb_infy_db_service_processor_input_config.json` to `STORAGE_ROOT_PATH`+`model_details_path`   
e.g., C:/DPP/infy_libraries_client/STORAGE/data/config/dpp_docwb_infy_db_service_processor_input_config.json
4. For sparse index - download `nltk_data` tokens from a script shared in `installation.ipynb` of `Document Extraction Libraries`.
5. When you run the code from local, run this in browser http://localhost:8005/api/v1/docs#

### API details for testing
1. To store indexes below API are used.
  * `/api/v1/sparsedb/saverecords`
    * method_name can be only bm25s.  
  * `/api/v1/vectordb/saverecords` 
    * model_name can be :
      * all-MiniLM-L6-v2 (default)
      * text-embedding-ada-002 (In config file provide URL and key )
      * mistral-embd (In config file provide URL and key )
2. To get the matches in close proximity to the query below are used.
  * `/api/v1/sparsedb/getmatches`
  * `/api/v1/vectordb/getmatches` 

## Build Package
1. Run `BuildPackage.bat`.
2. Package will be available at `apps\infy_db_service\target`.

## Deploy:
### Installation 
1. Copy the package from `apps\infy_db_service\target` to target server machine where you want to deploy.
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
  sudo firewall-cmd --zone=public --add-port=8005/tcp --permanent
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
  sudo cp infy_db_service.service /etc/systemd/system/
  ```
2. Verify the service file:
  ```
  sudo cat /etc/systemd/system/infy_db_service.service
  ```
3. Enable and start the service:
```
sudo systemctl enable infy_db_service.service
sudo systemctl daemon-reload
sudo systemctl start infy_db_service.service
sudo systemctl status infy_db_service.service
```

### Verification
Verify if the URL is working from browser.  
`http://<hostname>:8005/api/v1/docs`