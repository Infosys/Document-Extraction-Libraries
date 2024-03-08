## Overview

To run the notebook files locally, please follow the instructions below. 

## Prerequisites 

- Ensure python version >=3.8.8
- Install Tesseract from [https://tesseract-ocr.github.io/](https://tesseract-ocr.github.io/)

## Installation for Windows machine

Verify that python is available on PATH

```dos
python --version
# Python 3.8.8
```


### Create virtual environment

> Correct path as required

> Create venv from `\docs\notebook` directory

```
python -m venv .venv
```

### Activate virtual environment

```
.\.venv\Scripts\activate.bat
```
### Install depdendencies

```dos
pip install -r .\requirements.txt
```


## Start Jupyter Notebook

> Run below commands from `\docs\notebook` directory

```dos
SET PYTHONPATH=%CD%/src

jupyter lab
```
