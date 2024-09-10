## Overview

To run the notebook files locally, please follow the instructions below. 

## Prerequisites 

- Python (version >=3.8.8 and <3.12)
- Java (JDK or JRE) >= 8
- Apache Maven >= 3.8
- Tesseract >= 5.0 (Optional, Ref: https://tesseract-ocr.github.io)

## Installation for Windows machine

Verify that python is available on PATH. If not, please check `Appendix` below.

```dos
python --version
# Python 3.X.X
```


### Create virtual environment

> Create venv from `\docs\notebook` directory

```dos
python -m venv .venv
```

### Activate virtual environment

```dos
.\.venv\Scripts\activate
```

### Install dependencies

> Note: This step might take a few minutes.
```dos
pip install -r .\requirements.txt
```


### Start Jupyter Notebook

> Run below commands from `\docs\notebook` directory
> Set `PYTHONPATH` to `src` directory. Then, start the server.

| Command Prompt| Powershell |
|--------|--------|
| <pre>.\\.venv\Scripts\activate<br>SET PYTHONPATH=%CD%/src<br>jupyter lab</pre>| <pre>.\\.venv\Scripts\activate<br>$env:PYTHONPATH = "$(Get-Location)/src"<br>jupyter lab</pre>|


A browser will be opened automatically with below URL

- http://localhost:8888/lab

### Continue installation
Run below notebooks to install the python libraries.
```dos
docs/notebook/src/use_cases/dpp/installation.ipynb
```
```dos
docs/notebook/src/libraries/installation.ipynb
```
> After above steps, the installation is complete. 

### Run Use cases
> If Jupyter notebook is not running refer to **Start Jupyter Notebook** step above.
- `docs/notebook/src/libraries` : To explore low level libraries.
- `docs/notebook/src/use_cases/dpp` : To explore different use cases leveraging one or more low level libraries.

## Appendix

### Setting up the correct python version 

- Check for version of python available on PATH

    ```dos
    python --version
    # Python X.X.X
    ```

> If python is not available or incorrect version is showing up, then do the following **whenever opening a new command prompt**.
> 1. Identify the correct location of python E.g. `C:\Program Files\Python310\python.exe`.
> 2. In command prompt, run the following: `set PATH="C:\Program Files\Python310";%PATH%`  
> Note: Do NOT include `\python.exe` in the above command
