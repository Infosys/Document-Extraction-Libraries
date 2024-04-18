# Document-Extraction-Libraries
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