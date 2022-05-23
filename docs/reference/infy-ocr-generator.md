## 1. Introduction

`infy_ocr_generator`(v0.0.5) is a python library for generating OCR xml files which is used as the input for `infy_ocr_parser` python library.

Currently, it works with the following OCR tools. Support for other OCR tools may be added in future.

- Tesseract
- Azure Read API v3
- Azure OCR API v3

The library requires python 3.6

## 2. Build and Install
For build:
```python
python setup.py bdist_wheel
```
For install:
```python
pipenv install <whl file>
```

## 3. API

### Initialization
Creates an instance of OCR generator.
```python
class OcrGenerator(data_service_provider:infy_ocr_generator.interface.data_service_provider_interface.DataServiceProviderInterface):
```

**Input:**

Argument|Description
---|----
**data_service_provider (DataServiceProviderInterface)**|Provider to generate OCR file using a specified OCR tool.


**Output:**

None

### API - generate
API to generate OCR based on given OCR provider.
```python
def generate(doc_data_list:[{'doc_path': '',
	'pages': ''}]=None,
	api_response_list:list=None) -> list:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA], optional)**|Use these input files to<br>    -implement technique and generate output files. Defaults to None.
**api_response_list (list, optional)**|API response will be generated into output file.Defaults to None.


**Output:**

Param|Description
---|----
**list**|List of generated ocr file path.

### API - receive_response
API to Received response of asynchorouns call submit request.
```python
def receive_response(submit_req_result:[{'input_doc': '',
		'submit_api': {'query_params': {},
		'response': {}},
		'receive_api': {'response': {}},
		'error': None}],
	rerun_unsucceeded_mode:bool=False) -> [{'input_doc': '',
		'submit_api': {'query_params': {},
		'response': {}},
		'receive_api': {'response': {}},
		'error': None}]:
```

**Input:**

Argument|Description
---|----
**submit_req_result ([SUB_RE_API_STRUCTURE])**|Response structure of `submit_request` api
**rerun_unsucceeded_mode (bool, optional)**|Enabling this mode and passing same request<br> -will rerun for unsuccessful call. Defaults to False.


**Output:**

Param|Description
---|----
**[SUB_RE_API_STRUCTURE]**|List of dictionary

### API - set_data_service_provider
Setter method to switch `data_service_provider` at runtime.
```python
def set_data_service_provider(data_service_provider:infy_ocr_generator.interface.data_service_provider_interface.DataServiceProviderInterface):
```

**Input:**

Argument|Description
---|----
**data_service_provider (DataServiceProviderInterface)**|Provider object


**Output:**

None

### API - submit_request
API to submit request for asynchorouns call
```python
def submit_request(doc_data_list:[{'doc_path': '',
		'pages': ''}]) -> [{'input_doc': '',
		'submit_api': {'query_params': {},
		'response': {}},
		'receive_api': {'response': {}},
		'error': None}]:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA])**|List of input documents and its pages. e.g, ['doc_path':'c:/1.jpg','pages':'1']


**Output:**

Param|Description
---|----
**[SUB_RE_API_STRUCTURE]**|List of dictionary
### Initialization
Creates an instance of Tesseract Ocr Data Service Provider
```python
class TesseractOcrDataServiceProvider(config_params_dict:{'tesseract': {'pytesseract_path': '',
		'psm': 3}},
	output_dir:str=None,
	output_to_supporting_folder:bool=False,
	overwrite:bool=False,
	logger:logging.Logger=None,
	log_level:int=None):
```

**Input:**

Argument|Description
---|----
**config_params_dict (CONFIG_PARAMS_DICT)**|Provider CONFIG values.
**output_dir (str, optional)**|Directory to generate OCR file,<br>    if not given will generate into same file location. Defaults to None.
**output_to_supporting_folder (bool, optional)**|If True, OCR file will be generated to<br>    same file location but into supporting folder named `* _files`. Defaults to False.
**overwrite (bool, optional)**|If True, existing OCR file will be overwritten. Defaults to False.
**logger (logging.Logger, optional)**|logger object. Defaults to None.
**log_level (int, optional)**|log level. Defaults to None.


**Output:**

None

### API - generate
API to generate OCR based on OCR provider given
```python
def generate(doc_data_list:[{'doc_path': '',
	'pages': ''}]=None,
	api_response_list:list=None) -> list:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA], optional)**|Use these input files to<br>    -implement technique and generate output files. Defaults to None.
**api_response_list (list, optional)**|API response will be generated into output file. Defaults to None.


**Output:**

Param|Description
---|----
**list**|List of generated ocr file path.

### API - receive_response
API of tesseract ocr data service to Received response of asynchorouns call submit request.
```python
def receive_response(submit_req_response_list:list,
	rerun_unsucceeded_mode:bool=False) -> list:
```

**Input:**

Argument|Description
---|----
**submit_req_response_list (list)**|Response structure of `submit_request` api
**rerun_unsucceeded_mode (bool, optional)**|Enabling this mode and passing same request<br> -will rerun for unsuccessful call. Defaults to False.


**Output:**

Param|Description
---|----
**list**|[SUB_RE_API_STRUCTURE]

### API - submit_request
API to submit tesseract ocr data service request for asynchorouns call
```python
def submit_request(doc_data_list:[{'doc_path': '',
		'pages': ''}]) -> list:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA])**|List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']


**Output:**

Param|Description
---|----
**list**|[SUB_RE_API_STRUCTURE]
### Initialization
Creates an instance of Azure Ocr Data Service Provider.
```python
class AzureOcrDataServiceProvider(config_params_dict:{'azure': {'computer_vision': {'subscription_key': '',
		'api_ocr': {'url': '',
		'query_params': {'language': '',
		'model-version': 'latest',
		'detectOrientation': 'true'}}}}},
	output_dir:str=None,
	output_to_supporting_folder:bool=False,
	overwrite:bool=False,
	logger:logging.Logger=None,
	log_level:int=None):
```

**Input:**

Argument|Description
---|----
**config_params_dict (CONFIG_PARAMS_DICT)**|Provider CONFIG values.
**output_dir (str, optional)**|Directory to generate OCR file,<br>    if not given will generate into same file location. Defaults to None.
**output_to_supporting_folder (bool, optional)**|If True, OCR file will be generated to<br>    same file location but into supporting folder named `* _files`. Defaults to False.
**overwrite (bool, optional)**|If True, existing OCR file will be overwritten.Defaults to False.
**logger (logging.Logger, optional)**|logger object. Defaults to None.
**log_level (int, optional)**|log level. Defaults to None.


**Output:**

None

### API - generate
API of azure ocr data service to generate OCR based on OCR provider given
```python
def generate(doc_data_list:[{'doc_path': '',
	'pages': ''}]=None,
	api_response_list:list=None) -> list:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA], optional)**|Use these input files to<br>    -implement technique and generate output files.Defaults to None.
**api_response_list (list, optional)**|API response will be generated into output file.Defaults to None.


**Output:**

Param|Description
---|----
**list**|List of generated ocr file path.

### API - receive_response
API to Received azure ocr data service response of asynchorouns call submit request.
```python
def receive_response(submit_req_response_list:list,
	rerun_unsucceeded_mode:bool=False) -> list:
```

**Input:**

Argument|Description
---|----
**submit_req_response_list (list)**|Response structure of `submit_request` api.
**rerun_unsucceeded_mode (bool, optional)**|Enabling this mode and passing same request<br> -will rerun for unsuccessful call.Defaults to False.


**Output:**

Param|Description
---|----
**list**|[SUB_RE_API_STRUCTURE]

### API - submit_request
API to submit request of azure ocr data service for asynchorouns call
```python
def submit_request(doc_data_list:[{'doc_path': '',
		'pages': ''}]) -> list:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA])**|List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']


**Output:**

Param|Description
---|----
**list**|[SUB_RE_API_STRUCTURE]
### Initialization
Creates an instance of Azure Read Ocr Data Service Provider
```python
class AzureReadOcrDataServiceProvider(config_params_dict:{'azure': {'computer_vision': {'subscription_key': '',
		'api_read': {'url': '',
		'query_params': {'language': '',
		'readingOrder': 'basic',
		'model-version': 'latest'}}}}},
	output_dir:str=None,
	output_to_supporting_folder:bool=False,
	overwrite:bool=False,
	logger:logging.Logger=None,
	log_level:int=None):
```

**Input:**

Argument|Description
---|----
**config_params_dict (CONFIG_PARAMS_DICT)**|Provider CONFIG values
**output_dir (str, optional)**|Directory to generate OCR file,<br>    if not given will generate into same file location. Defaults to None.
**output_to_supporting_folder (bool, optional)**|If True, OCR file will be generated to<br>    same file location but into supporting folder named `* _files`. Defaults to False.
**overwrite (bool, optional)**|If True, existing OCR file will be overwritten. Defaults to False.
**logger (logging.Logger, optional)**|logger object. Defaults to None.
**log_level (int, optional)**|log level. Defaults to None.


**Output:**

None

### API - generate
API to generate OCR based on OCR provider given
```python
def generate(doc_data_list:[{'doc_path': '',
	'pages': ''}]=None,
	api_response_list:list=None) -> list:
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA], optional)**|Use these input files to<br>    -implement technique and generate output files. Defaults to None.
**api_response_list (list, optional)**|API response will be generated into output file. Defaults to None.


**Output:**

Param|Description
---|----
**list**|List of generated ocr file path.

### API - receive_response
API to Azure_read_ocr_data_service Received response of asynchorouns call submit request.
```python
def receive_response(submit_req_response_list,
	rerun_unsucceeded_mode=False):
```

**Input:**

Argument|Description
---|----
**submit_req_response_list ([SUB_RE_API_STRUCTURE])**|Response structure of `submit_request` api
**rerun_unsucceeded_mode (bool, optional)**|Enabling this mode and passing same request<br> -will rerun for unsuccessful call. Defaults to False.


**Output:**

None

### API - submit_request
API to submit Azure read ocr data serivce request for asynchorouns call
```python
def submit_request(doc_data_list:[{'doc_path': '',
		'pages': ''}]):
```

**Input:**

Argument|Description
---|----
**doc_data_list ([DOC_DATA])**|List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']


**Output:**

None
