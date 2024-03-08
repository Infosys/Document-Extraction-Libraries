# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""## 1. Introduction

`infy_field_extractor` is a python library for extracting data from documents provided as image files.
It provides APIs to extract attributes which can be of types `key-value` or `key-state` pair:
- Checkbox
- Radio button
- Text

The library requires two providers one to get text from a bbox and
another to search the text within a bbox in the given image.
This library itself provides two different providers for which they have their own prerequisites:
- NativePdf Data Service Provider
  - infy_common_utils (Python library)
- Tesseract Data Service Provider
  - infy_ocr_parser (Python library)

## 2. Version History

- **V 0.0.8** _(2021-11-23)_
  - Internal: package restructure

- **V 0.0.7** _(2021-11-03)_
  - Updated 'scaling_factor' input parameter format
  - Internal: package restructure

- **V 0.0.6** _(2021-08-10)_
  - Added new provider interface `DataServiceProviderInterface` for delegating get text and search text
  - Implemented new `NativePdfDataServiceProvider` for native PDF text extraction
  - Converted existing tesseract logic to new provider `TesseractDataServiceProvider`

- **V 0.0.5** _(2021-06-30)_
  - `scaling_factor` as optional parameter to all APIs to handle training image vs actual image dimension differences
  - Retain line breaks in multiline text
  - Internal: package restructure and dependencies cleanup
  
- **V 0.0.4** _(2021-03-02)_
  - Standardization of APIs for text, radio button and checkbox
  - New API `extract_custom_fields` to accept list of fields and value positions

- **V 0.0.3** _(2021-02-08)_
  - API to extract label text value from images
  
- **V 0.0.2** _(2021-02-08)_
  - API to extract radio button state from images

- **V 0.0.1** _(2021-02-08)_
  - API to extract checkbox state from images



## 3. Prerequisite

The following software should be installed in your local

- Python 3.6

"""
