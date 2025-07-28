# Infy Search Service Tool Guide

## Overview:
The Infy Search Service Tool is an Angular-based user interface that helps in querying indexes generated for documents after running the DEL indexing pipeline. The tool uses the `infy_search_service`, a semantic search service, to search the documents based on user queries.

## Pre-requisites:
Ensure the following services are set up and running properly:
1. `infy_model_service`
2. `infy_db_service`
3. `infy_resource_service`
4. `infy_search_service`

>**Note:** For detailed instructions on setting up and running these services, refer to the [README](../../docs/README.md).

## Default Example:
This tool utilizes indexes created after running the DEL indexing pipeline to provide answers to your queries. If you have already run the DEL indexing pipeline, you can directly use this tool to query the created indexes by navigating to [Usage Guide](#usage-guide) section.

If you have not ran the DEL indexing pipeline, please follow the below steps setup some pre-created indexes for using the tool:
1. Open a command prompt terminal and run the following command to navigate to the root directory of the project.   
    ```bash
    cd C:\Document-Extraction-Libraries
    ```
2. Run the following commands in order to setup the tool:
    ```bash
    python _internal\scripts\del_tools_setup.py
    ```
3. Select the `infy_search_service_tool` from the menu and hit enter. This will copy pre-created vector and sparse indexes for the sample document `AR_2022-23_page-14-17.pdf` to the following paths:
    - Vector index: `C:/del/fs/services/dbsvc/STORAGE/data/vectordb/encoded/sentence_transformer-all-MiniLM-L6-v2/documents`
    - Sparse index: `C:/del/fs/services/dbsvc/STORAGE/data/db/sparseindex/bm25s/documents`
    - Resource: `C:/del/fs/services/resourcesvc/STORAGE/data/vectordb/resources`
4. > **Verification:** Once the setup is done, check if the necessary files are present at the locations mentioned above.

## Usage Guide:
1. Ensure all pre-requisite services are set up and running.
2. Open a command prompt terminal and run the following command to navigate to the root directory of the project.   
    ```bash
    cd C:\Document-Extraction-Libraries
    ```
3. Run the following command to run the launcher script:
    ```bash
    python _internal\scripts\launch.py
    ```
4. This will launch a menu where you can select the tools you want to run, select the `infy_search_service_tool` and hit enter.
5. This will open a new terminal, open the Infy Search Service Tool in your browser at the endpoint mentioned in the terminal.<br>The default endpoint is: `http://localhost:8000`.
6. Once you open the application in the browser, there will be a panel on the right hand side opened, where you can enter the required details. Refer below table for more details.
    ### Tool Configurations:
    The table below provides information about the fields, along with recommended/default values to get started:
    >**Note:** The default values are based on pre-created indexes. For custom indexes, ensure to enter the correct values.

    | Field Name                           | Recommended/Default Value              |
    |--------------------------------------|----------------------------------------|
    | LLM Base Url                         | <LLM_Base_Url>                         |
    | LLM Key                              | <LLM_Key>                              |
    | LLM Model Name                       | <LLM_Model_Name>                       |
    | LLM Deployment Name                  | <LLM_Deployment_Name>                  |
    | Index Id                             | For Custom run(DEL indexing pipeline) use appropriate index id.<br>For Default Example: test-6819be53-6800-48bd-ab2d           |
    | Base Resource Service Endpoint (DEL) | http://localhost:8006/resourceservice  |
    | Base Search Service Endpoint (DEL)   | http://localhost:8004/searchservice    |
    | Retrieve Top_K                       | 4                                      |
    | Pre-filter Fetch k                   | 10                                     |
    | Filter Metadata                      | NA                                     |
    | Vector Index                         | Click check mark                       |
    | Sparse Index                         | Click check mark                       |
    | Hybrid-RRF Index                     | Click check mark                       |

7. Minimize the panel by clicking the `>` icon on the top left of the panel.
8. Enter your query in the search bar and hit enter to get results.<br>Some example queries are mentioned below:
    ```bash
    What is the percent of women employees in Infosys?
    How many fresh graduates did Infosys hire globally?
    ```
9. The results will display a list of chunks arranged by score, with additional information such as page number, chunk content, metadata, and document name.
10. Click on the document name to open it in a new tab with the document loaded on the left side.
11. In the new tab, you can modify additional fields like Max Tokens, Temperature, Top K Used, and Total Attempts which are all set to default values as needed.
12. Click on submit to search within the document.
13. The answer to your query will be displayed in the results section below the submit button, along with a drop down which you can expand to view the further breakdown.