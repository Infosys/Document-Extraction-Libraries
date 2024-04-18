![](https://img.shields.io/github/license/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/issues/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/issues-closed/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/badge/Python-3-blue)
![](https://img.shields.io/github/forks/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/stars/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/last-commit/Infosys/Document-Extraction-Libraries)

# Document Extraction Libraries 3.5.0

Document Extraction Libraries are a suite of python/java libraries that provide APIs to **extract information from documents** (e.g. scanned/native PDFs, images etc.). For semi-structured documents (e.g. form-like documents), this can be done in a simple and predictable manner. For unstructured documents, it can extract the raw content, retrieve relevant text from it using **semantic search** and use a **Large Language Model (LLM)** to extract information.

The suite consists of libraries that can be used to **generate** OCR files using free/commercial tools; **parse** OCR files to extract regions of interest; and **extract** texts and selection field values from the regions of interest. It can **extract segments** from pages, **generate chunks**, **generate embeddings**, and save them to a vector DB which can then be **retrieved as context** and given to LLM to extract information from documents.    

Additionally, it includes a data pipeline framework - **Document Processor Platform (DPP)** - for creating **reusable components** and **configurable pipelines**. The pipeline brings all the libraries together to create a logical workflow.

These libraries can be used as SDKs to solve document digitization problems and help with semantic search and information extraction requirements.

## Prerequisites 

- Python >=3.8 or <=3.11
- Java >=8
- OCR Tool (Tesseract / Azure Read OCR V 3.2) _(for non-digital documents)_

## Libraries

The details of each library and its core functionality is given below. For more details, please read the [docs](docs).

S# | Library	| Description | 
---|-------|---------------|
1 | infy_ocr_generator| Provides APIs to generate OCR files by specifying an OCR provider.
2 | infy_ocr_parser| Provides APIs to parse OCR files and detect regions of interest (bounding boxes) when given a search criteria. 
3| infy_field_extractor|Provides APIs for extracting free text and selection fields (checkboxes and radio buttons) from image files using regions of interest (bounding boxes) as input. 
4| infy_table_extractor|Provides APIs to extract rows and columns from an image of a table.
5| infy_common_utils | Provides APIs to invoke external tools like JAR files.
6| infy_fs_utils | Provides APIs to abstract underlying file system and object stores.
7| infy_gen_ai_sdk | Provides APIs for using embeddings, Large Language Models (LLM), vector DB etc.
8| InfyFormatConverterJAR | Provides APIs to convert documents from one format to another. E.g., PDF to image, JSON etc.
9| InfyOcrEngineJAR | Provides APIs to invoke OCR engines. Currently, it has tesseract. 
10| infy_dpp_sdk|The sdk for document processor platform (DPP) containing the interfaces for processors, schema definition for document data and in-built orchestrators to execute a data pipeline made from processors.
11| infy_dpp_core|A collection of processors for core  tasks like request creation, meta-data extraction etc.
12| infy_dpp_segmentation|A collection of processors for tasks like document segmentation, chunk creation etc.
13| infy_dpp_ai | A collection of processors for tasks like generating embeddings, calling LLMs with prompt templates etc.
14 | infy_dpp_storage | A collection of processors to help store data to graph DB etc. 
15 | infy_dpp_content_extractor | A collection of processors for extracting raw contents from documents. 
## How does it Work

### Semi-structured documents

The libraries use **computer vision** in the form of an **OCR engine** (e.g. Tesseract, Azure OCR Read etc.) for positional text detection. It then takes a "region definition" as input and applies techniques to detect regions of interest within the document. 

This makes it possible to extract attributes -**free text, selection fields (checkboxes, radio buttons) and bordered tables** - specifically from the regions of interest and eliminates the risk of potential errors in future should the document layout change but not the regions of interest. 

### Unstructured documents

The libraries along with the data pipeline framework help create a workflow where raw content is extracted from documents and stored in a vector DB as embeddings. From this, useful information is extracted using the Retrieval augmented generation (RAG) approach. 

The API logical input/output is given below. 

Step |Library | Input | Output  
---|---|---|---|
1 | infy_ocr_generator | `image file` | `OCR file` 
2 | infy_ocr_parser | `OCR file`, `region definition` | `region of interest [x,y,w,h]`
3 | infy_field_extractor | `OCR file`, `region of interest [x,y,w,h]` | `text`, `checkbox state(T/F)`, `radio button state(T/F)` 
4 | infy_table_extractor | `image file` | `table data with rows and cols` 
5  | infy_dpp_core <br/> infy_dpp_segmentation <br/> infy_dpp_ai <br/> infy_dpp_storage <br/> infy_dpp_content_extractor <br/>| `config_data,document_data, context_data` | `document_data, context_data`

## Examples

For code examples, please read [docs/notebook](docs/notebook).

## Reference

For API specifications, please read [docs/reference](docs/reference).
