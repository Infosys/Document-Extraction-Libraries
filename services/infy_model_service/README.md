# Infy Model Service

## Pre-requisites

1. Sentence Transformer
    ```
    mkdir C:\del\ai\models
    cd C:\del\ai\models
    git lfs install
    git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    ``` 

2. Docling dependent ML models download
   ```
   mkdir c:\temp
   cd c:\temp
   git lfs install
   git clone https://huggingface.co/ds4sd/docling-models
   xcopy /s /e /i /y docling-models\model_artifacts C:\del\ai\models\docling_models\model_artifacts
   ```
3. Yolox
    ```
    mkdir C:\del\ai\models\unstructuredio
    cd C:\del\ai\models\unstructuredio
    git lfs install
    git clone https://huggingface.co/unstructuredio/yolo_x_layout
    ```



## Setup

1. Create a virtual environment:

   ```
   python -m venv venv
   ```

2. Install the requirements:

   ```
   pip install -r requirements.txt
   ```

3. Run the service:

   - Pre-requisites:
     - Make sure to check the config.ini and update the paths accordingly.
   - If you want to run the service manually, follow the below steps:
     - You can run the service using the following commands one by one in order(after activating you virtual environment):
       ```
       cd src
       ray start --head --num-cpus=3 --num-gpus=0 --dashboard-host 0.0.0.0
       serve run config.yaml
       ```
     - To check if the ray server status, you can run the below command:
       ```
       ray status
       ```
     - To stop the ray server, you can run the below command:
       ```
       ray stop
       ```
   - If you want to run the service using a script, follow the below steps:

     **NOTE:** Make sure you have bash installed on your system.
     Go through the script and make changes to the paths for your virtual environment. If running on Windows, change `bin` to `Scripts` in the path.

     - You can run the service via script by opening the bash terminal in the directory and running the below command:
       ```
       ./infy_model_service_script.sh start
       ```
     - You can stop the service by running the below command:
       ```
       ./infy_model_service_script.sh stop
       ```
