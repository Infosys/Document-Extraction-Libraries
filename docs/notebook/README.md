## Overview

To run the notebook files locally, please follow the instructions below. 

## Prerequisites 

- Ensure python version >=3.8 or <= 3.10
- Install `pipenv` for python virtual environment management (You can use any other tool)
- Install Tesseract from [https://tesseract-ocr.github.io/](https://tesseract-ocr.github.io/)

## Installation for Windows machine

Verify that python is available on PATH

```dos
python --version
# Python 3.8.2
```

### Build wheel files from source code and copy to lib folder

> Run below using commmand prompt from `\docs\notebook` directory.


```dos
md lib

cd ..\

cd ..\infy_bordered_table_extractor
python -m build --wheel
copy dist\* ..\docs\notebook\lib

cd ..\infy_field_extractor
python -m build --wheel
copy dist\* ..\docs\notebook\lib

cd ..\infy_ocr_generator
python -m build --wheel
copy dist\* ..\docs\notebook\lib

cd ..\infy_ocr_parser
python -m build --wheel
copy dist\* ..\docs\notebook\lib

cd ..\docs\notebook
```

### Create virtual environment

> Correct path as required

```dos
pipenv --python "C:/ProgramFiles/Python38-32/python.exe"
```

### Install depdendencies

```dos
pipenv shell
pip install -r .\requirements.txt
```
>Modify requirements.txt file if you want to use AWS,Azure for ocr_genration like below: 
```
./lib/infy_ocr_generator-0.0.12-py3-none-any.whl[tesseract,aws,azure]
```


## Start Jupyter Notebook

> Run below commands from `\docs\notebook` directory

```dos
pipenv shell
SET PYTHONPATH=%CD%/src
jupyter lab
```
