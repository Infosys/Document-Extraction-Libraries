![](https://img.shields.io/github/license/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/issues/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/issues-closed/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/badge/Python-3-blue)
![](https://img.shields.io/github/forks/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/stars/Infosys/Document-Extraction-Libraries)
![](https://img.shields.io/github/last-commit/Infosys/Document-Extraction-Libraries)

# Document Extraction Libraries

Document Extraction Libraries are a suite of python libraries that provide APIs to **extract attributes from documents** (e.g. scanned PDFs, images etc.) in a simple and predictable manner. 

The suite consists of libraries that can be used to **generate** OCR files from image files using free/commercial OCR tools; **parse** OCR files to extract regions of interest; and **extract** texts and selection field values from the regions of interest.

These libraries can be used as SDKs to solve document digitization problems. 

## Prerequisites 

- OCR Tool (Tesseract / Azure Read OCR V 3.2)
- Python 3.6
- Any utility to convert PDF to images (Currently, the libraries take only images as input)

## Libraries

The details of each library and its core functionality is given below. For more details, please read the [docs](docs).

Library	| Description | 
----------|---------------|
infy_ocr_generator| Provides APIs to generate OCR files from image files by specifying an OCR tool.
infy_ocr_parser| Provides APIs to parse OCR files and detect regions of interest (bounding boxes) given a search criteria. 
infy_field_extractor|Provides APIs for extracting free text and selection fields (checkboxes and radio buttons) from image files using regions of interest (bounding boxes) as input. 
infy_bordered_table_extractor|Provides APIs to extract rows and columns from an image of a bordered table.

## How does it Work

The libraries use **computer vision** in the form of an **OCR engine** (e.g. Tesseract, Azure OCR Read etc.) for positional text detection. It then takes a "region definition" as input and applies techniques to detect regions of interest within the document. 

This makes it possible to extract attributes -**free text, selection fields (checkboxes, radio buttons) and bordered tables** - specifically from the regions of interest and eliminates the risk of potential errors in future should the document layout change but not the regions of interest. 

The logical API input/output is given below. 

Step |Library | Input | Output  
---|---|---|---|
1 | infy_ocr_generator | `image file` | `OCR file` 
2 | infy_ocr_parser | `OCR file`, `region definition` | `region of interest [x,y,w,h]`
3 | infy_field_extractor | `OCR file`, `region of interest [x,y,w,h]` | `text`, `checkbox state(T/F)`, `radio button state(T/F)` 
4 | infy_bordered_table_extractor | `image file` | `table data with rows and cols` 

## Examples

For code examples, please read [docs/notebook](docs/notebook).

## Reference

For API specifications, please read [docs/reference](docs/reference).
