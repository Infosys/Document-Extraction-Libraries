# Document-Extraction-Libraries
## V3.9.0
- Llama-3.1-70B model support added for inferencing.
- Below are apps implementing indexing and inferencing pipeline:
  * `infy_dpp_processor`: For indexing pipeline to deploy infy_dpp_processor as docker image on Kubernetes cluster.
  * `infy_db_service`: There are two ways to store the indexes created, one is locally in the environment where this pipeline is running, and the other one is using infy_db_service which provides way to store indexes in a central environment where this service is hosted.
  * `infy_search_service`: If infy_db_service is used to store created indexes then use infy_search_service to query on those documents.

## V3.8.0
- New interactive tool `tool_06_hybrid_search.ipynb` to demonstrates hybrid search capabilities.
- Table detection and extraction feature for pdf and image input(.tiff, .jpg, .png) in indexing pipeline added.
- Bug fix for pdf_plumber table extraction
- New chunking technique i.e.page_and_segment_type added.
- Added support of index_id while indexing.
- Added support for scanned pdf in content extraction.
## V3.7.0
- New interactive tool `tool_05_embedding_clusters.ipynb` to experiment with embeddings and their clusters.

## V3.6.0
- New interactive tool tool_03_prompt_engineering.ipynb to help with prompt engineering added.
- Made changes to the different techniques used to generate segments to be able to run in parallel.
- Merged chunk_parser and chunk_saver to chunk_generator.
- Made changes to new chunk_generator to save the resources inside vectordb folder.
- Renamed paragraph chunking to segment chunking. Available chunking methods are page and segments based.
- Made changes to Reader processor:
  - added retry logic for LLM calls if response format is not as expected (up to a configurable max value)
  - added option to consider a subset of top_k values from retriever while building the context
- Custom embedding support added.

## V3.5.3
- InfyFormatConverter modified to handle error.

## V3.5.2
- Added missing files for tool_02_semantic_search.ipynb

## V 3.5.1
- Bug fix for kernel issue.
- Ability to filter response based on document name during QnA.
- Vectordb file type changed.
- Support for chat models gpt-4 and gpt-4-32k.

## V 3.5.0
- Ability to extract images from native pdf and do OCR to get any text within it. (The libraries modified - InfyFormatConverterJAR, infy_common_utils, infy_dpp_content_extractor, infy_dpp_segmentation)
- Modified pipeline card to visualize the pipeline.
- Bug fix.

## V 3.4.0
- The default OCR tool used in all notebooks is InfyOcrEngine (Tess4J - tesseract)
- Segmentation processor logic revamped into separate processor based on specific feature.
  - `segment_parser` processor deprecated.
  - `segment_generator` processor modified, now takes care of detecting segment using techniques (e.g., ocr, native_pdf, txt, json, detectron)
- Below are new processors in infy_dpp_segmentation library:
    - `segment_classifier` classifies segment as header & footer (e.g., segments near to page edges controlled by threshold value)
    - `segment_consolidator`takes best of all techniques (e.g., union of bboxes from different techniques)      
    - `page_column_detector`:
      - Auto-detection of columns in a page based on segments already detected.
      - It can also remove header and footers segments from the already detected segments if mentioned in configuration, under exclude parameter section.
    - `segment_merger` merges smaller segments to create larger segments (e.g., lines to paragraphs).
        
    - `segment_sequencer` gives sequence number to all segments based on some params (e.g., sequencing to form a reading order for LLM)
- Debug feature added to all segmentation related processor, which can plot processor's output on images.
- For `single column` document below processors are optional. For `multi-column` document segmentation all six processors of infy_dpp_segmentation is mandatory to be used in pipeline.
    - segment_classifier
    - segment_consolidator  
    - page_column_detector  
    - segment_merger
- **Table extraction technique** introduced in segmentation for `bordered table` from a native pdf document.
- New library `infy_dpp_content_extractor` added for extracting raw contents from documents.
- `infy_dpp_sdk library` modified, where OrchestratorNativeBasic class marked as depercated in favour of new class OrchestratorNative used for running pipeline.
- Improved installation steps.
- Indexing pipeline config files modified with new segmentation processors.
- Bug fixes
- For more details [docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb](docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb)

## V 3.3.0
- Feature added to specify environment variables in config files, to avoid hard coding of confidential data. All the sample config files updated.
- Consolidation of two indexing notebook files to handle pdf and image in single pipeline.
- Bug fix in BuildJAR.bat, library and some notebook files.
- Notebook files updated with more notes and clear instructions.
- For more details [docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb](docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb) 

## V 3.2.1
- Bug fix - entails OpenAI model name handling and sentence transformer embedding model at local which help not to send PII on API,
- New library InfyOcrEngineJAR 
- Few libraries update
- Q&A tool
- For more details [docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb](docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb) 
## V 3.2.0
- Unstructured data from text or pdf file visualization in graph DB (Neo4j)
- For more details [docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb](docs/notebook/src/use_cases/dpp/uc_00_guide.ipynb)   
## V 3.1.0
- Inter document search ability
- Minor defect fix 
## V 3.0.0
- Indexing of PDF and image files to vector DB (FAISS)
- Retrieval of chunks based on query within a document (intra-document search)
- Q&A on documents