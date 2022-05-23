## Overview

To run the notebook files locally, please follow the instructions below. 

## Prerequisites 

- Ensure python = v3.6
- Install `pipenv` for python virtual environment management (You can use any other tool)
- Install Tesseract from [https://tesseract-ocr.github.io/](https://tesseract-ocr.github.io/)

## Installation for Windows machine

Verify that python is available on PATH

```dos
python --version
# Python 3.6.2
```

### Build wheel files from source code and copy to lib folder

> Run below using commmand prompt from `\docs\notebook` directory.


```dos
md lib\v3.6

cd ..\

cd ..\infy_bordered_table_extractor
python setup.py bdist_wheel
copy dist\* ..\docs\notebook\lib\v3.6

cd ..\infy_field_extractor
python setup.py bdist_wheel
copy dist\* ..\docs\notebook\lib\v3.6

cd ..\infy_ocr_generator
python setup.py bdist_wheel
copy dist\* ..\docs\notebook\lib\v3.6

cd ..\infy_ocr_parser
python setup.py bdist_wheel
copy dist\* ..\docs\notebook\lib\v3.6

cd ..\docs\notebook
```

### Create virtual environment

> Correct path as required

```dos
pipenv --python "C:/ProgramFiles/Python36/python.exe"
```

### Install depdendencies

```dos
pipenv shell
pip install -r .\requirements_v36.txt
```

## Start Jupyter Notebook

> Run below commands from `\docs\notebook` directory

```dos
pipenv shell
SET PYTHONPATH=%CD%/src
jupyter lab
```
