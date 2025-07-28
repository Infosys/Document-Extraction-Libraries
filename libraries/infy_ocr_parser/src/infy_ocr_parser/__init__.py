# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""## 1. Introduction

`infy_ocr_parser` is a python library for parsing OCR xml files. It provides APIs to detect regions (bounding boxes) given a search criteria.

The regions (bounding boxes) are then given as the input to other data extraction libraries.

Currently, it works with the following OCR tools. Support for other OCR tools may be added in future.

- Tesseract
- Azure Read v3
- Azure OCR v3


## 2. Version History

- **V 0.0.10** _(2021-11-24)_
  - Internal: Package restructure

- **V 0.0.9** _(2021-11-22)_
  - Added new provider interface `DataServiceProviderInterface` for delegating get tokens
  - Implemented new `AzureReadDataServiceProvider` and `AzureOcrDataServiceProvider` for Azure read and ocr tools
  - Modified existing ocr tools implementation into new providers - `TessearctOcrDataServiceProvider` and `AbbyyOcrDataServiceProvider`
  - Nearby Tokens API - Added `distance` property to specify the distance of the nearby tokens from anchor text
  - Changed format to store `scaling_factor` as dicitonary for storing both vertical and horizontal scaling factors
  - Changed logic to get page num from attribute value and not HOCR file
  - Search API - Changes made to search anchor text  in `line dictionary` if not found in `phrase dictionary`

- **V 0.0.8** _(2021-09-24)_
  - Nearby Tokens API - Introduced new API to get get nearby tokens in all four directions
  - Fixed issue of regionbbox for phrases

- **V 0.0.7** _(2021-08-03)_
  - Added `max_word_space` property to allow phrase creation to be configurable
  - Changed logic to consider text as within a bounding box only if fully inside (earlier it was partial)
  - Fixed issue of measurement unit not taking value beyond 10th decimal place

- **V 0.0.6** _(2021-06-29)_
  - Name changed from `ocr-parser` to `infy_ocr_parser`
  - Added `pageDimensions": {width:0,height:0}` to `REG_DEF_DICT` to handle training and production image size differences
  - Tokens API - Added `id` (read-only) field to word, phrases and line dictionaries for traceability
  - Raise exceptions when keys in dictionaries are misspelled or unrecognized
  - Internal: package restructure and dependencies cleanup

- **V 0.0.5** _(2021-06-09)_
  - Read and parse ABBYY FineReader Engine 12 XML files
  - Search API - Extended to ABBYY
  - Tokens API - Extended to ABBYY
  - Scaling factor as optional parameter to all APIs to handle image vs PDF page dimension differences
  - New API `calculate_scaling_factor`

- **V 0.0.4** _(2021-03-31)_
  - Search API - Ability to specify multiple measurement units - pixels, % and text size
  - Search API - Ability to use keywords to denote beginning/end of document

- **V 0.0.3** _(2021-03-29)_
  - Search API - Ability to detect regions spanning multiple pages
  - Search API - Page number is optional and ability to provide page ranges, numbers etc.
  - Search API - Ability to subtract regions from detected regions

- **V 0.0.2** _(2021-03-18)_
  - Search API - change anchor text match logic to consider phrases instead of lines
  - Search API - Allow synonyms to be passed in anchor text
  - Search API - Allow match type to be set as a) 'normal' with similarity score (0 to 1) b) 'regex' with valid patterns

- **V 0.0.1** _(2021-03-03)_
  - Search API standardized : get_bbox_for()
  - Tokens API standardized : get_tokens_from_hocr()
  - Use anchor text for region definition

- **V 0.0.0** _(2021-02-01)_
  - Call Tesseract for HOCR file generation
  - Read HOCR file
  - Search API - Identify region between text - row-wise and col-wise
  - Search API - Identify region containing a text
  - Search API - Identify region nearby a text
  - Tokens API - Get tokens (words, phrases and lines)


## 3. Prerequisite

The following software should be installed in your local

- Python 3.6

"""
