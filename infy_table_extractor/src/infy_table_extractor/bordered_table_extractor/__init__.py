# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from .bordered_table_extractor import BorderedTableExtractor
from . import (interface, providers)
"""## 1. Introduction

`infy_bordered_table_extractor` is a python package that can **extract data** from an **image of a bordered table**.
The output can be a `dictionary` or an `excel` file.


## 2. Version History

- **V 0.0.7** _(2021-11-24)_
  - Internal: Code refactoring aand Package restructuring

- **V 0.0.6** _(2021-08-03)_
  - Added new provider interface `DataServiceProviderInterface` for delegating table detection and text extraction
  - Implemented new `NativePdfDataServiceProvider` for native PDF text extraction
  - Converted existing tesseract logic to new provider `TesseractDataServiceProvider`
  - Performance improvements via multi-threading in line detection and text extraction modules

- **V 0.0.5** _(2021-05-19)_
  - Cell level image noise removal for text extraction by OCR

- **V 0.0.4** _(2021-05-17)_
  - Fix for vertical line detection failures when they are partial or not visible due to dark background color
  - Performance of best skew contrast line optimized by making convolution technique default<br> and adaptive matching optional
  - Image skew correction (using RGB technique) for synergy with RGB line detection technique

- **V 0.0.3** _(2021-05-07)_
  - Skew handling added to RGB pixel contrast logic
  - Best contrast in skew line based on max of convolution technique and adaptive matching technique
  - RGB pixel contrast method made default for line detection

- **V 0.0.2** _(2021-04-22)_
  - New line detection technique using RGB pixel contrast
  - Extract API - Modify to return selected cell values

- **V 0.0.1** _(2021-04-06)_
  - Image skew correction (using OpenCV)
  - New line detection techniques (using OpenCV) - a) Adaptive Threshold b) HOCR
  - Order of preference - a) Adaptive Threshold b Normal Threshold c) HOCR

- **V 0.0.0** _(2021-03-01)_
  - Line detection technique - Normal threshold (using OpenCV)
  - Convert API - Extract cells from table and save as excel file
  - Extract API - Extract cells from table and return as dictionary/json

## 3. Prerequisite

The following software should be installed in your local

- Python 3.6
- Tesseract v5.0.0-alpha.20190623
- infy_common_utils

"""
