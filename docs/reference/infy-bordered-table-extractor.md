## 1. Introduction

`infy_bordered_table_extractor`(v0.0.7) is a python package that can **extract data** from an **image of a bordered table**.
The output can be a `dictionary` or an `excel` file.

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
Creates an instance of Bordered Table Extractor.
```python
class BorderedTableExtractor(table_detection_provider:infy_bordered_table_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		cell_extraction_provider:infy_bordered_table_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		temp_folderpath:str,
	logger:logging.Logger=None,
	debug_mode_check:bool=False):
```

**Input:**

Argument|Description
---|----
**table_detection_provider (DataServiceProviderInterface)**|Provider for table detection
**cell_extraction_provider (DataServiceProviderInterface)**|Provider for cell data extraction
**temp_folderpath (str)**|Path to temp folder
**logger (logging.Logger, optional)**|Path to store all the debug info files. Defaults to None.
**debug_mode_check (bool, optional)**|To get debug info while using the API. Defaults to False.


**Output:**

None

### API - extract_all_fields
Extracts table information from an image and returns as an json output and saves it as an
        excel file, if required.
```python
def extract_all_fields(image_file:str,
		file_data_list:[{'path': '',
	'pages': []}]=None,
	within_bbox:list=None,
		config_param_dict:{'custom_cells': [{'rows': [],
		'columns': []}],
		'col_header': {'use_first_row': True,
		'values': []},
		'deskew_image_reqd': False,
		'image_cell_cleanup_reqd': True,
		'output': {'path': None,
		'format': None},
		'rgb_line_skew_detection_method': [<RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD: 1>],
	'line_detection_method': [<LineDetectionMethod.RGB_LINE_DETECT: 1>]}=None):
```

**Input:**

Argument|Description
---|----
**image_file (str)**|image file path for which table has to be extracted
**file_data_list ([FILE_DATA], optional)**|List of all supporting file paths and page numbers, if applicable.<br>    Image and the file must have the same content.
**within_bbox (list, optional)**|Bounding box coordinates(x, y, width, height) of the table in the image.<br>    Defaults to None.
**config_param_dict (CONFIG_PARAM_DICT, optional)**|Additional info. Defaults to None.<br>    `custom_cells`: customized cell extraction<br>    `col_header`: Choose the header to be used `use_first_row`. To customize values for header use `values`.<br>    `deskew_image_reqd`: If detected skew in image is to be corrected<br>    `image_cell_cleanup_reqd`: If each cell image is required for cleaning for text extraction<br>    `output`: `path` to specify where to save the file and `format` for type of file to save the data<br>    `rgb_line_skew_detection_method`: List of all skew detection methods for detecting skewness<br>    `line_detection_method`: list of all line detection methods for line detection


**Output:**

Param|Description
---|----
**dict**|Dict of saved info.
### Initialization
Creates an instance of Tesseract Data Service Provider
```python
class TesseractDataServiceProvider(tesseract_path:str,
	logger:logging.Logger=None,
	log_level:int=None):
```

**Input:**

Argument|Description
---|----
**tesseract_path (str)**|Path to Tesseract.
**logger (logging.Logger, optional)**|Logger object. Defaults to None.
**log_level (int, optional)**|Logging Level. Defaults to None.


**Output:**

None

### API - get_text
Method to be implemented to return the text from the list of
cell images or bbox of the original image as a list of dictionary.
(Eg. [{'cell_id': str,'cell_text':'{{extracted_text}}', 'cell_bbox':[x, y, w, h]}]
```python
def get_text(img:<built-in function array>,
		img_cell_bbox_list:[{'cell_id': '',
		'cell_bbox': []}],
		file_data_list:[{'path': '',
	'pages': []}]=None,
		additional_info:{'cell_info': [{'cell_id': '',
		'cell_img_path': '',
		'cell_bbox': [],
	'cell_img': <built-in function array>}]}=None,
	temp_folderpath:str=None) -> [{'cell_id': '',
		'cell_text': '',
		'cell_bbox': []}]:
```

**Input:**

Argument|Description
---|----
**img (np.array)**|Read image as np array of the original image.
**img_cell_bbox_list ([IMG_CELL_BBOX])**|List of all cell bbox
**file_data_list (FILE_DATA,optional)**|List of all file datas. Each file data<br>    has the path to supporting document and page numbers, if applicable.<br>    Defaults to None.
**additional_info (ADDITIONAL_INFO, optional)**|Additional info. Defaults to None.
**temp_folderpath (str, optional)**|Path to temp folder. Defaults to None.


**Output:**

Param|Description
---|----
**[GET_TEXT_OUTPUT]**|list of dict containing text and its bbox.

### API - get_tokens
Method to be implemented to get all tokens (word, phrase or line) and its 
    bounding box as x, y, width and height from an image as a list of dictionary.
    Currently word token is only required.
```python
def get_tokens(token_type_value:int,
		img:<built-in function array>,
		file_data_list:[{'path': '',
	'pages': []}]=None) -> [{'text': '',
		'bbox': [],
		'conf': <class 'int'>}]:
```

**Input:**

Argument|Description
---|----
**token_type_value (int)**|1(WORD), 2(LINE), 3(PHRASE)
**img (np.array)**|Read image as np array of the original image.
**file_data_list ([FILE_DATA], optional)**|List of all file datas. Each file data has<br>    the path to supporting document and page numbers, if applicable.<br>    When multiple files are passed, provider has to pick the right file based <br>    on the image dimensions or type of file extension.<br>    Defaults to None.


**Output:**

Param|Description
---|----
**[GET_TOKENS_OUTPUT]**|list of dict containing text and its bbox.
