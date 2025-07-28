## App Flow:
DEL can be effectively utilized with a combination of the below apps, services, and tools to extract data from documents. Below are the details of each service, app, and tool:

- **Apps**
  - `infy_dpp_processor`: Application to run DEL indexing pipelines.
  - `infy_dpp_eval_processor`: Application to run DEL synthetic data generation, evaluation and rag evaluation pipelines.

- **Services**
  - `infy_db_service`: Service to store created vector and sparse indexes via indexing pipeline in a central environment.
  - `infy_model_service`: Service to host and serve models.
  - `infy_resource_service`: Service to store and fetch resources during indexing and inference pipelines.
  - `infy_search_service`: Service to query on indexes created after running indexing pipeline.

- **Tools**
  - `infy_search_service_tool`: A tool which acts as a UI for `infy_search_service`.

### Instructions to setup App Flow:
1. **Requirements:**
  - Ensure that all the software requirements and setups mentioned in `Pre-requisites` section of this [README](SetupGuide.md#pre-requisites) are successfully completed.

2. **Installing Dependencies:**
  - To create a virtual environment and install the required dependencies, open a command prompt terminal and run the following command to navigate to the root directory of the project. 
    ```bash
    cd C:\Document-Extraction-Libraries
    ```
  - Run the following commands in order to create a virtual environment and install all the required dependencies for the respective apps, services, and tools:
    * **App: infy_dpp_processor**
      ```bash
      cd apps\infy_dpp_processor
      python ..\..\_internal\scripts\install.py
      cd ..\..
      ```
    * **App: infy_dpp_eval_processor**
      ```bash
      cd apps\infy_dpp_eval_processor
      python ..\..\_internal\scripts\install.py
      cd ..\..
      ```
    * **Service: infy_db_service**
      ```bash
      cd services\infy_db_service
      python ..\..\_internal\scripts\install.py
      cd ..\..
      ```
    * **Service: infy_resource_service**
      ```bash
      cd services\infy_resource_service
      python ..\..\_internal\scripts\install.py
      cd ..\..
      ```
    * **Service: infy_search_service**
      ```bash
      cd services\infy_search_service
      python ..\..\_internal\scripts\install.py
      cd ..\..
      ```
    * **Tool: infy_search_service_tool**
       ```bash
       cd tools\infy_search_service_tool\packaging
       python ..\..\..\_internal\scripts\install.py
       cd ..\..\..
       ```
    >**Note:** Assuming that `infy_model_service` is already setup and running as mentioned in Step 5 under [Common Setup Instructions](SetupGuide.md#common-setup-instructions).

3. **Service Setup:**
  - For `infy_resource_service`, `infy_db_service` and `infy_search_service`, some additional setup is required which is mentioned below:
  - Open a command prompt terminal and run the following command to navigate to the root directory of the project.  
    ```bash
    cd C:\Document-Extraction-Libraries
    ```
  - Run the following commands in order to setup the services:
    ```bash
    python _internal\scripts\del_services_setup.py
    ```
  - This will launch a menu where you can select the services you want to setup, select the respective service and hit enter.
    - For `infy_resource_service`, this will create the following directory if not present `C:\del\fs\services\resourcesvc\STORAGE\data\vectordb\resources`.
    - For `infy_db_service`, this will copy the required configuration file to a base location `C:\del\fs\services\dbsvc\STORAGE\data\config`.
      
      >**Note:** By default, in the config file `infy_model_service` is set to run on `localhost:8003` and use `sentence_transformer(all-MiniLM-L6-v2)` as embedding model, if there is a change in said api url or if you want to use other supported embedding models then please edit the configuration file as per requirements.
    - For `infy_search_service`, this will copy the required configuration and prompt_templates files to a base location `C:\del\fs\services\searchsvc\STORAGE\data\config`.
  - > **Verification:** Once the setup is done, you can check if the necessary configuration and prompt files are present at the locations mentioned above.

    >**Note:** The above mentioned setups for `infy_resource_service`, `infy_db_service` and  `infy_search_service` are one time/ first time activities.<br>Once setup, for subsequent runs these are not necessary and will prompt you if you want to overwrite existing files.

4. **Application Setup:**
  - For `infy_dpp_processor` and `infy_dpp_eval_processor`, some additional setup is required which is mentioned below:
  - Open a command prompt terminal and run the following command to navigate to the root directory of the project.  
    ```bash
    cd C:\Document-Extraction-Libraries
    ```
  - Run the following commands in order to setup the services:
    ```bash
    python _internal\scripts\del_apps_setup.py
    ```
  - This will launch a menu where you can select the apps you want to set up. Select the respective app and press Enter.
  - For both `infy_dpp_processor` and `infy_dpp_eval_processor`, this will copy the required config and prompt_template files to the base location `C:\del\fs\appuc\STORAGE\data\config`.
  - After you select either `infy_dpp_processor` or `infy_dpp_eval_processor`, it will prompt you to choose a dataset to use. These are the input files for the pipelines. You can change the input files in the dataset or add additional datasets by editing the [del_apps_setup.json](../_internal/scripts/del_apps_setup.json). All the files under a selected dataset are then copied to `C:\del\fs\appuc\STORAGE\data\input` folder.
  - For testing various pipelines under both apps below is a breakdown of what datasets can be used for what pipelines:
    * For `infy_dpp_processor`:
      - For both `dpp_indexing_pipeline_sequential` and `dpp_indexing_pipeline_parallel`, you can use the `dataset_annualreport`.
    * For `infy_dpp_eval_processor`:
      - For `dpp_synthetic_data_generation_pipeline`, you can use the `dataset_annualreport`.
      - For `dpp_synthetic_data_evaluation_pipeline`, you can use the `dataset_ar_qna_data`.
      - For `dpp_rag_evaluation_pipeline`, you can use `dataset_ar_qna_data` or `dataset_ar_qna_report`.
  - > **Verification:** Once this is done, you can check if the configuration and input files are present at the locations mentioned above.
  
    >**Note:** After every successful pipeline run, the input files inside the `C:\del\fs\appuc\STORAGE\data\input` folder are deleted.<br>For successive runs, you will need to run the setup script again to copy the dataset files.<br>When you run the script again, it will ask whether to overwrite the existing configuration and prompt template files in the `C:\del\fs\appuc\STORAGE\data\config` folder.<br>You can select `n` to keep the existing files as is, and then only the dataset files will be copied to the `C:\del\fs\appuc\STORAGE\data\input` folder.

5. **Run the Apps, Services and Tools:**
  - To launch the apps, services, and tools, open a command prompt terminal and run the following command to navigate to the root directory of the project.  
    ```bash
    cd C:\Document-Extraction-Libraries
    ```
  - Run the following command to run the launcher script:
    ```bash
    python _internal\scripts\launch.py
    ```
  - This will launch a menu-driven launcher, displaying a list of apps, services, and tools that can be launched.
  - Select the app, service, or tool that you want to launch and hit enter. This will open a new terminal where your app, service, or tool will be running.
  - To stop the app, service, or tool, press `Ctrl+C` in the terminal where it is running.
  - Details about the running the apps, services, and tools for indexing and search is mentioned under `Indexing and Search Guide`.
  - Details about the running the apps, services, and tools for all evaluation pipelines are mentioned under `Evaluation Guide`.

6. **Indexing and Search Guide:**
  - If you want to perform indexing on document/s, you can use the `infy_dpp_processor` app.
  - To run this app, make sure that: 
    1. You have setup all the necessary setps as mentioned in `Pre-requisites`, .
    2. The below services are running and are setup according to `Service Setup`:
        - `infy_model_service`
        - `infy_resource_service`
        - `infy_db_service`
        - `infy_search_service` *(Only necessary if you want to query on the created indexes)*
    3. `infy_dpp_processor` app is setup according to the pipeline you want to run as mentioned in `Application Setup`.
  -  Open a command prompt terminal and run the following commands in order to navigate to the root directory of the project and run the launcher.  
      ```bash
      cd C:\Document-Extraction-Libraries
      python _internal\scripts\launch.py
      ```
  - This will open a terminal where you can select the app you want to run. Select `infy_dpp_processor` and press Enter.
  - A new menu will be displayed, prompting you to choose between `dpp_indexing_pipeline_sequential` and `dpp_indexing_pipeline_parallel` pipelines for indexing. Select the desired pipeline and press Enter.
  - This will open a new command prompt terminal to start the indexing pipeline execution, where you can monitor its progress.
  - > **Verification:** Once the indexing pipeline is completed, the indexes would be created here `C:\del\fs\services\dbsvc\STORAGE\data`.<br>Vector indexes are stored in `\vectordb\encoded` folder and sparse indexes are stored in `\db\sparseindex` folder.
  - You can find the `index_id` needed to query the created indexes by opening the `processor_response_data.json` file. This file can be found in the following directory: `C:\del\fs\appuc\STORAGE\data\work\D-<uuid>\<file_name>.pdf_files`.
  - Inside the JSON file, based on the indexing pipeline you run, look for the `index_id` value under:
    - For `dpp_indexing_pipeline_sequential`: `context_data.db_indexer.vector_db.index_id`.<br>Note that in the above path instead of `vector_db` you can also get it from `sparseindex` the `index_id` value is same in both places.
    - For `dpp_indexing_pipeline_parallel`: `context_data.db_indexer_vector.vector_db.index_id`.<br>Note that in the JSON path, instead of `db_indexer_vector` you can also get it from `db_indexer_sparse` the `index_id` value is same in both places.
  - You can then launch `infy_search_service_tool` through the same launch script and fill in the details to query the indexed documents, the details on how to use the said tool are given in this [README](../_internal/demo/semantic_search_via_tool.md) file.

7. **Evaluation Guide:**
  * **Synthetic Data Generation:**
    - If you want run a pipline for qna generation, you can run `dpp_synthetic_data_generation_pipeline` in `infy_dpp_eval_processor` app.
    - To run this app, make sure that: 
      1. The below services are running and are setup according to `Service Setup`:
          - `infy_model_service`
          - `infy_resource_service`
          - `infy_db_service`
      2. `infy_dpp_eval_processor` app and `dpp_synthetic_data_generation_pipeline` are setup according to `Application Setup`.
    -  Open a command prompt terminal and run the following commands in order to navigate to the root directory of the project and run the launcher.  
        ```bash
        cd C:\Document-Extraction-Libraries
        python _internal\scripts\launch.py
        ```
    - This will open a terminal where you can select the app you want to run. Select `infy_dpp_eval_processor` and then select `dpp_synthetic_data_generation_pipeline`.
    - This will open a new command prompt terminal to start the qna generation pipeline execution, where you can monitor its progress.
    - > **Verification:** Once it is completed, you can get the `question_data.xlsx` from `C:\del\fs\appuc\STORAGE\data\output`, inside a `G-<uuid>` folder.

  * **Synthetic Data Evaluation:**
    - If you want run a pipline for qna evaluation on the `question_data.xlsx` generated by the `Qna Generation` pipeline, you can run `dpp_synthetic_data_evaluation_pipeline` in `infy_dpp_eval_processor` app.
    - To run this app, make sure that: 
      1. `infy_dpp_eval_processor` app and `dpp_synthetic_data_evaluation_pipeline` are setup according to `Application Setup`.
    -  Open a command prompt terminal and run the following commands in order to navigate to the root directory of the project and run the launcher.  
        ```bash
        cd C:\Document-Extraction-Libraries
        python _internal\scripts\launch.py
        ```
    - This will open a terminal where you can select the app you want to run. Select `infy_dpp_eval_processor` and then select `dpp_synthetic_data_evaluation_pipeline`.
    - This will open a new command prompt terminal to start the qna evaluation pipeline execution, where you can monitor its progress.
    - > **Verification:** Once it is completed, you can get the `qna_report.xlsx` from `C:\del\fs\appuc\STORAGE\data\work\D-<uuid>\report` folder.

    >**Note:** By default the qna evaluation pipeline would be run on a sample `question_data.xlsx` file, if you want to run it on a different file, you can put/replace the file in the `C:\del\fs\appuc\STORAGE\data\input` folder.
  
  * **RAG Evaluation:**
    - If you want run a RAG evaluation pipline, you can run the `dpp_rag_evaluation_pipeline` in `infy_dpp_eval_processor` app.
    - To run this app, make sure that: 
      1. `infy_dpp_eval_processor` app and `dpp_rag_evaluation_pipeline` are setup according to `Application Setup`.
      2. During application setup, when selecting the dataset for `dpp_rag_evaluation_pipeline`, you can select `dataset_ar_qna_data`(which is the output of `dpp_synthetic_data_generation_pipeline`) or `dataset_ar_qna_report`(which is the output of `dpp_synthetic_data_evaluation_pipeline`) to run the RAG evaluation pipeline.We recommend to go with the later one, i.e `dataset_ar_qna_report` to run this pipeline.
      3. Before running the RAG evaluation pipeline, you need to update the `index_id` in the configuration file. Follow the below steps:
          - Navigate to the following directory, created after running the indexing pipeline: `C:\del\fs\appuc\STORAGE\data\work\D-<uuid>\<file_name>.<extension>_files`.
          - Open the `processor_response_data.json` file in this directory.
          - Find the `index_id` value in the JSON file under `context_data.db_indexer.vector_db.index_id`
            >**NOTE:**<br>Instead of `vector_db` you can also get it from `sparseindex` the `index_id` value is same in both places.<br>If you run `dpp_indexing_pipeline_parallel`, in the JSON path, `db_indexer` would be named as `db_indexer_vector` and `db_indexer_sparse`, the `index_id` value would be same in both places.
          - Navigate to the following directory: `C:\del\fs\appuc\STORAGE\data\config`.
          - Open the `dpp_tf_pipeline_rag_evaluation.json` configuration file.
          - Update the `index_id` value in the configuration file under `processor_input_config.SemanticSearch.services.request_payload.retrieval` with the value you found in the `processor_response_data.json` file.
    -  Open a command prompt terminal and run the following commands in order to navigate to the root directory of the project and run the launcher.  
        ```bash
        cd C:\Document-Extraction-Libraries
        python _internal\scripts\launch.py
        ```
    - This will open a terminal where you can select the app you want to run. Select `infy_dpp_eval_processor` and then select `dpp_rag_evaluation_pipeline`.
    - This will open a new command prompt terminal to start the rag evaluation pipeline execution, where you can monitor its progress.
    - > **Verification:** Once it is completed, you can get the `rag_report.xlsx` from `C:\del\fs\appuc\STORAGE\data\work\D-<uuid>\report` folder.

    >**Note:** By default the rag evaluation pipeline would be run on a sample `qna_report.xlsx` file, if you want to run it on a different valid file, you can put/replace the file in the `C:\del\fs\appuc\STORAGE\data\input` folder.


## Troubleshooting:

For any issues faced while setting up or running code, please refer to the [Troubleshooting](../_internal/Troubleshooting.md) guide.
