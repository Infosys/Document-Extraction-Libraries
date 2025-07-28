## Notebook Flow:
The Notebook Flow is a collection of Jupyter Notebooks that demonstrate the usage of the Document Extraction Libraries (DEL). The notebooks are organized into two main categories:
1. **Low-level Libraries**: This category contains notebooks that demonstrate the usage of low-level libraries in various use cases.
2. **High-level Libraries**: This category contains notebooks that demonstrate the usage of the libraries in various use cases.

To run the notebook files and pipelines locally, please follow the instructions below: 

### Instructions to setup Notebook Flow:

1. **Requirements:**
    - Ensure that all the software requirements and setups mentioned in the `Pre-requisites` section of this [README](../SetupGuide.md) are successfully completed.

2. **Installing Dependencies:**
    - To create a virtual environment and install the required dependencies, open a command prompt terminal and run the following commands to navigate to the notebook folder inside the root directory of the project:
        ```bash
        cd C:\Document-Extraction-Libraries\docs\notebook
        ```
    - Run the following commands to create a virtual environment and install all the required dependencies for running the notebooks:
        ```bash
        python ..\..\_internal\scripts\install.py
        cd ..\..
        ```

3. **Starting Jupyter Lab:**    
    You can start the Jupyter lab from either the `Command Prompt` or `Powershell` terminal:
    1. To start the Jupyter lab from the `Command Prompt` terminal:
        - Open a command prompt terminal and run the following commands in order:
            ```bash
            cd C:\Document-Extraction-Libraries\docs\notebook
            .\.venv\Scripts\activate
            SET PYTHONPATH=%CD%/src
            jupyter lab
            ```
        - A browser window will open automatically with the Jupyter Notebook running.<br>If it doesn't open the following URL in your browser: [http://localhost:8888/lab](http://localhost:8888/lab)
    2. To start the Jupyter lab from the `Powershell` terminal:
        - Open a Powershell terminal and run the following commands in order:
            ```bash
            cd C:\Document-Extraction-Libraries\docs\notebook
            .\.venv\Scripts\activate
            $env:PYTHONPATH = "$(Get-Location)/src"
            jupyter lab
            ```
        - A browser window will open automatically with the Jupyter lab running.<br>If it doesn't open automatically, navigate to the following URL in your browser: [http://localhost:8888/lab](http://localhost:8888/lab)

4. **Installing Additional Dependencies:**
    - Open the Jupyter lab in the browser window at the above-mentioned URL and navigate to the following installation files via the jupyter lab file browser, according to the type of use cases you want to run:
        1. For `Low-level library notebooks`:
            ```dos
            src/libraries_usage/installation.ipynb
            ```
        2. For `High-level library notebooks`:
            ```dos
            src/use_cases/dpp/installation.ipynb
            ```
    - Go through all the cells in the respective installation notebooks and follow the instructions to install the additional dependencies and set up the required environment for running different usecases.
    - Depending on the type of notebooks you want to run, you might need to install from either one or both of these installation notebooks.

5. **Running Notebooks:**
    * Low-level library notebooks:
        - This category contains low-level libraries, having notebooks that showcases their usage and implementation.
        - To run the notebooks for these libraries, navigate to the following directory in the Jupyter lab file browser:
            ```dos
            src/libraries_usage
            ```
        - From here you can select which library you want to explore and run their respective notebooks.
        - The different libraries that are available here are as follows: ~pending~
            1. `infy_field_extractor`:
            2. `infy_model_evaluation`:
            3. `infy_ocr_generator`:
            4. `infy_ocr_parser`:
            5. `infy_table_extractor`:
    

    * High-level library notebooks:
        - These notebooks make use of high-level DPP libraries to run various the pipelines related to indexing, retrieval, inferencing, etc.
        - The notebooks are organized into different categories like `use_cases`, `tools`, and `evaluation`.
        - To run the `use_cases` notebooks, navigate to the following directory in the Jupyter lab file browser:
            ```dos
            src/use_cases/dpp
            ``` 
        - The table below provides a brief description of each `use_cases` notebooks:

            | Usecase                                   | Description                                                                           |
            |-------------------------------------------|---------------------------------------------------------------------------------------|
            | uc_00_guide.ipynb                         | A guide to get started with the Document Extraction Libraries (DEL).                  |
            | uc_03_custom_processor_addition.ipynb     | Demonstrates how to add a custom processor to the pipeline.                           |
            | uc_30_indexing_vectordb.ipynb             | Demonstrates DEL indexing pipeline to index documents to a vector database.           |
            | uc_31_indexing_graphdb.ipynb              | Demonstrates DEL indexing pipeline to index documents to a graph database.            |
            | uc_40_retrieval_batch.ipynb               | Demonstrates batch retrieval using DEL libraries.                                     |
            | uc_40.1_retrieval_custom.ipynb            | Demonstrates custom processor addtion to a DEL retrieval pipeline.                    |
            | uc_41_retrieval_online.ipynb              | Demonstrates online retrieval using DEL libraries.                                    |
            | uc_50_inferencing_batch.ipynb             | Demonstrates DEL batch inferencing pipeline on indexed documents.                     |
            | uc_51_inferencing_online.ipynb            | Demonstrates DEL online inferencing pipeline on indexed documents.                    |
            | uc_52_inferencing_online_moderation.ipynb | Demonstrates DEL online inferencing pipeline on indexed documents with moderation.    |
        - To run the `tools` notebooks, navigate to the following directory in the Jupyter lab file browser:
            ```dos
            src/use_cases/dpp/tools
            ``` 
        - The table below provides a brief description of each `tools` notebooks:

            | Tool                                      | Description                                                                                           |
            |-------------------------------------------|-------------------------------------------------------------------------------------------------------|
            | tool_01_qna.ipynb                         | Tool to demonstrate the applicability of `uc_51_inferencing_online.ipynb` for building interactive UI.|
            | tool_02_semantic_search.ipynb             | Tool to demonstrate the applicability of `uc_41_retrieval_online.ipynb for` building interactive UI.  |
            | tool_03_prompt_engineering.ipynb          | Tool to experiment with different prompts on LLM.                                                     |
            | tool_04_rag_metrics.ipynb                 | Tool to experiment with data and RAG performance metrics.                                             |
            | tool_05_embedding_clusters.ipynb          | Tool to experiment with different embedding models and their clusters.                                |
            | tool_06_hybrid_search.ipynb               | Tool to see hybrid search capability by showing comparison between vector and sparse indexes.         |
            | tool_07_segmentation_visualized.ipynb     | Tool to showcase DEL segmentation approach.                                                           |
        - To run the `evaluation` notebooks, navigate to the following directory in the Jupyter lab file browser:
            ```dos
            src/use_cases/dpp/evaluation
            ``` 
        - The table below provides a brief description of each `evaluation` notebooks:

            | Evaluation                        | Description                                                 |
            |-----------------------------------|-------------------------------------------------------------|
            | uc_01_qna_generation_batch.ipynb  | Evaluation notebook to generate synthetic data.             |
            | uc_02_evaluation_batch.ipynb      | Evaluation notebook for running DEL RAG evaluation pipeline.|

## Troubleshooting:

For any issues faced while setting up or running code, please refer to the [Troubleshooting](../../_internal/Troubleshooting.md) guide.
