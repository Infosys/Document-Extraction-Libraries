# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""## 1. Introduction

`infy_common_utils` is a python library to provide commonly used horizontal APIs.

It's also a python wrapper for the following non-python libraries:

- infy-format-converter.jar


## 2. Version History

- **V 0.0.2** _(2021-08-03)_
  - Removed jar file embeded in wheel file. Caller needs to provide the jar file home path.
  - APIs exposed are `PdfToImg`.

- **V 0.0.1** _(2021-07-05)_
  - Initial version as a python wrapper for `infy-format-converter.jar.
  - APIs exposed are `PdfToJson` and `PdfToText`.


## 3. Prerequisite

The following software should be installed in your local system.

- Python 3.6
- infy-format-converter.jar
"""
