# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#



"""## 1. Introduction

`infy_ocr_generator` is a python library for generating OCR xml files which is used as the input for `infy_ocr_parser` python library.

Currently, it works with the following OCR tools. Support for other OCR tools may be added in future.

- Tesseract
- Azure Read API v3
- Azure OCR API v3
- ABBYY FineReader Engine 12


## 2. Version History

- **V 0.0.5** _(2021-11-18)_
  - Internal: package restructure

- **V 0.0.4** _(2021-11-02)_
  - Generate OCR json file for `Azure OCR API v3` and `Azure Read API v3`
  - Added new provider interface `DataServiceProviderInterface` for generating ocr files

- **V 0.0.3** _(2021-09-24)_
  - Removed image grayscale conversion pre-processing step
  - Internal: dependencies cleanup

- **V 0.0.2** _(2021-06-29)_
  - Name changed from `ocr-generator` to `infy_ocr_generator`
  - Internal: package restructure and dependencies cleanup

- **V 0.0.1** _(2021-06-22)_
  - Generate OCR xml file for `ABBYY FineReader Engine 12`

- **V 0.0.0** _(2021-02-01)_
  - Generate HOCR file for `Tesseract`.


## 3. Prerequisite

The following software should be installed in your local

- Python 3.6
- Any one of the following OCR tools
  - Tesseract v5.0.0-alpha.20190623
  - Azure Read API v3
  - Azure OCR API v3
  - ABBYY FineReader Engine 12

"""
