# Setup Guide:
Document Extraction Libraries (DEL) features can be experienced in two ways, and both are explained below:
1. `App Flow:` Using various apps, services and tools, run pipelines to perform document indexing, search and evaluation.
2. `Notebook Flow:` Using Jupyter Notebook, run pipelines to perform document indexing, search and evaluation.

Below is the deployment diagram for both `App Flow` as well as `Notebook Flow`:

<img src="assets/component-diagram.svg">

Below you will find detailed instructions on how to set up and run DEL for both approaches.

## Pre-requisites:
Before you begin, ensure that the below pre-requisites like software installations and setups are successfully completed.

### Software Requirements:
- Python (version >=3.10.5 and <3.12)
- Java (JDK or JRE) >= 8
- Apache Maven >= 3.8
- Tesseract >= 5.0 (Optional, Ref: https://tesseract-ocr.github.io)
- Neo4j >= 5.17.0 (Optional)

>**Note:** To verify successfull installation of the above softwares, you can run the below commands one by one in a command prompt terminal and compare the results. <br>The versions mentioned below are just for reference and can vary based on the version you have installed.:
  ```bash
  python --version
  # Python 3.11.2
  java -version
  # openjdk version "1.8.0_402"
  mvn -version
  # Apache Maven 3.9.0
  tesseract --version
  # tesseract v5.4.0.20240606
  ```
  >For `Neo4j`, navigate to the `/bin` folder in the directory where its installed and run the below command in a command prompt terminal. <br>To check if its running, you can navigate to the following endpoint `http://<localhost>:7474/` in your browser.
  ```bash
  neo4j.bat console
  ``` 

### Assumptions:
* We recommend cloning this project in suitable directories, such as `C:` or `D:` drives. 
* All the below instructions and commands are under the assumption that the project is cloned in the following directory `C:\Document-Extraction-Libraries`.
* If the project is cloned to a different path, please adjust the below commands accordingly.

### Environment Variable Setup:
To run DEL, we need to setup certain environment variables, which are mentioned in the below table:   
>**Note:** The hostname mentioned below as `localhost` is under the assumption that you run these services locally. <br>If this changes, you will need to update the same.

| Env Key                        | Env Value                                 | Example                                     |
|--------------------------------|-------------------------------------------|---------------------------------------------|
| INFY_MODEL_SERVICE_BASE_URL    | http://localhost:8003/modelservice        | http://`hostname`:8003/modelservice         |
| INFY_SEARCH_SERVICE_BASE_URL   | http://localhost:8004/searchservice       | http://`hostname`:8002/searchservice        |
| INFY_DB_SERVICE_BASE_URL       | http://localhost:8005/dbservice           | http://`hostname`:8005/dbservice            |
| INFY_RESOURCE_SERVICE_BASE_URL | http://localhost:8006/resourceservice     | http://`hostname`:8006/resourceservice      |
| AZURE_OPENAI_SERVER_BASE_URL   | <AZURE_OPENAI_SERVER_URL>                 | https://`hostname`.azure.com                |
| AZURE_OPENAI_SECRET_KEY        | <AZURE_OPENAI_SECRET_KEY>                 | <AZURE_OPENAI_SECRET_KEY>                   |
| LITELLM_PROXY_SERVER_BASE_URL  | <LITELLM_PROXY_SERVER_BASE_URL>           | http://`hostname`:`portnumber`              |
| LITELLM_PROXY_SECRET_KEY       | <LITELLM_PROXY_SECRET_KEY>                | <LITELLM_PROXY_SECRET_KEY>                  |
| NEO4J_URL                      | http://localhost:7474                     | http://`hostname`:7474                      |
| NEO4J_USR_NAME                 | <NEO4J_USR_NAME>                          | <NEO4J_USR_NAME>                            |
| NEO4J_PWD                      | <NEO4J_PWD>                               | <NEO4J_PWD>                                 |

### DEL Setup Requirements:
The table below outlines some internal setup requirements for DEL based on the approach you decide to go with, i.e., `App Flow` or `Notebook Flow`:

| No | Step                     | App Flow | Notebook Flow |
|----|--------------------------|----------|---------------|
| 1  | InfyFormatConverter      |     ✅    |      ✅     |
| 2  | InfyOcrEngine            |     ✅    |      ✅     |
| 3  | NLTK Data                |     ✅    |      ✅     |
| 4  | Tiktoken encoding        |     ✅    |      ✅     |
| 5  | infy_model_service       |     ✅    |      ✅     |
| 6  | infy_db_service          |     ✅    |      ❌     |
| 7  | infy_resource_service    |     ✅    |      ❌     |
| 8  | infy_search_service      |     ✅    |      ❌     |
| 9  | infy_search_service_tool |     ✅    |      ❌     |
| 10 | infy_dpp_processor       |     ✅    |      ❌     |
| 11 | infy_dpp_eval_processor  |     ✅    |      ❌     |


### Common Setup Instructions:
The steps below provide detailed instructions for internal setups that are common to both approaches:
* Open a command prompt terminal and run the following command to navigate to the root directory of the project.   
  ```bash
  cd C:\Document-Extraction-Libraries
  ```
1. **InfyFormatConverter :**
  - To set up `InfyFormatConverter`, in the command prompt terminal run below command:   
    ```bash
    python _internal\scripts\infy_format_converter_script.py
    ```
  - This will build the binary file and copy it to the required location `C:\del\programfiles\InfyFormatConverter`.
  - > **Verification :** After running the script, check if the binary file `infy-format-converter-x.x.xx.jar` is present at the location mentioned above.
2. **InfyOcrEngine :**
  - To set up `InfyOcrEngine`, in the command prompt terminal run below command:
    ```bash
    python _internal\scripts\infy_ocr_engine_script.py
    ```
  - This will get the data file and copy it to the required location `C:\del\ai\models\tessdata`
  - And this will build the binary file and copy it to the required location `C:\del\programfiles\InfyOcrEngine`.
  - > **Verification :** After running the script, check if the tessdata file `eng.traineddata` is present in the tessdata folder and binary file `infy-ocr-engine-x.x.x.jar` is present at the location mentioned above.
3. **NLTK Data :**
  - To setup `NLTK Data`, in the command prompt terminal run below command:
    ```bash
    python _internal\scripts\nltk_script.py
    ```
  - This will get the files and copy it to the required location `C:\del\ai\nltk_data`.

    >**Note:** This script requires `nltk` library to be installed, if it is not there in your system then the script will prompt you to setup a dummy virtual environment and install the library to run the script. <br>Post script execution, this dummy virtual environment will be deleted. <br>If you get any errors related to ssl certificate issue, please check this [Troubleshooting guide](../_internal/Troubleshooting.md#nltk-data-issue-sslcertificate_verify_failed).
  - > **Verification :** After running the script, check if `corpora` and `tokenizers` folders are present at the location mentioned above.
4. **Tiktoken encoding :**
  - To setup `Tiktoken encoding`, in the command prompt terminal run below command:
    ```bash
    python _internal\scripts\tiktoken_script.py
    ```
  - This will get the files and copy it to the required location `C:\del\ai\models\tiktoken_encoding`.
  - > **Verification :** After running the script, check if a hash value file is present at the location mentioned above.
5. **infy_model_service :**
  - To create a virtual environment and install the required dependencies, run the following commands in order to create a virtual environment and install all the required dependencies for `infy_model_service`:
    ```bash
    cd services\infy_model_service
    python ..\..\_internal\scripts\install.py
    cd ..\..
    ```
  - To run this service, you need to download certain models locally, the instructions for the same are mentioned in this [README](../services/infy_model_service/README.md) file under `Pre-requisites` section.
  - Once the models are downloaded, to launch the service, run the following command in the terminal and select the `infy_model_service` as the service to launch:
    ```bash
    python _internal\scripts\launch.py
    ```
  - This will open a new command prompt terminal where it will start the ray server where the models are hosted.
     >**Note:** It may take some time for this service to start, so please wait for a few minutes before proceeding to the next steps.
  - You can check access the ray dashboard by opening the following URL in the browser: `http://localhost:8265/#/overview`.
  - If you want to access the swagger for all the deployed models, you can open the below URL's in the browser:
    - For embedding: `http://localhost:8003/modelservice/api/v1/model/embedding/docs#`
    - For yolox: `http://localhost:8003/modelservice/api/v1/model/yolox/docs#`
    - For docling: `http://localhost:8003/modelservice/api/v1/model/docling/docs#`
  - >**Verification:** After running the script, you can open the following URL `http://localhost:8265/#/overview` in your browser and navigate to `Serve` in the top bar. <br>All your deployments will be listed there.<br>Make sure all of them are `Running/Healthy`.

>**Note:** The above mentioned setups for `InfyFormatConverter`, `InfyOcrEngine`, `NLTK Data`, `Tiktoken encoding` and `infy_model_service` are one time/ first time activities. <br>Once setup, for subsequent runs these are not necessary and will prompt you if you want to overwrite existing files.<br>
For `infy_model_service`, although the setup is a one time activity, the service needs to be running whenever you want to run the pipelines.



## App Flow:
For detailed instructions on setting up DEL App Flow, please refer to the following [README](AppFlow.md).

## Notebook Flow:

For detailed instructions on setting up DEL with jupyter notebook, please refer to the following [README](notebook/NotebookFlow.md).

## Troubleshooting:

For any issues faced while setting up or running code, please refer to the Troubleshooting [README](../_internal/Troubleshooting.md).
