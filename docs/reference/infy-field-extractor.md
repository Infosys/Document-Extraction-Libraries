## 1. Introduction

`infy_field_extractor`(v0.0.8) is a python library for extracting data from documents provided as image files. 
It provides APIs to extract attributes which can be of types `key-value` or `key-state` pair:
- Checkbox
- Radio button
- Text

The library requires python 3.6 and infy_ocr_parser library

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
Creates an instance of Text Extractor.
```python
class TextExtractor(get_text_provider:infy_field_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		search_text_provider:infy_field_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		temp_folderpath:str,
	logger:logging.Logger=None,
	debug_mode_check:bool=False):
```

**Input:**

Argument|Description
---|----
**get_text_provider (DataServiceProviderInterface)**|Provider to get text either word,<br>    line or phrases
**search_text_provider (DataServiceProviderInterface)**|Provider to search the text in the image.
**temp_folderpath (str)**|Path to temp folder.
**logger (logging.Logger, optional)**|Logger object. Defaults to None.
**debug_mode_check (bool, optional)**|To get debug info while using the API. Defaults to False.


**Output:**

None

### API - extract_all_fields
API to extract text from an image automatically as key-value pair.
```python
def extract_all_fields(image_path:str,
		config_params_dict:{'field_value_pos': 'right',
		'page': 1,
		'eliminate_list': [],
		'scaling_factor': {'hor': 1,
		'ver': 1},
	'within_bbox': []}=None,
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None):
```

**Input:**

Argument|Description
---|----
**image_path (str)**|Path to the image
**config_params_dict (CONFIG_PARAMS_DICT, optional)**|Additional info for min and max<br>    radiobutton radius to text height ratio, position of state w.r.t key,<br>    within_bbox, eliminate_list, scaling_factor and page number.<br>    Defaults to CONFIG_PARAMS_DICT.
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas. Each file data<br>    has the path to supporting document and page numbers, if applicable. Defaults to None.


**Output:**

Param|Description
---|----
**dict**|Dict of extracted info.

### API - extract_custom_fields
API to extract text value for respective given key words or value within given bounding boxes.
```python
def extract_custom_fields(image_path:str,
		text_field_data_list:[{'field_key': [''],
		'field_key_match': {'method': 'normal',
		'similarityScore': 1},
		'field_value_bbox': [],
		'field_value_pos': 'left'}],
		config_params_dict:{'field_value_pos': 'right',
		'page': 1,
		'eliminate_list': [],
		'scaling_factor': {'hor': 1,
		'ver': 1},
	'within_bbox': []}=None,
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None):
```

**Input:**

Argument|Description
---|----
**image_path (str)**|Path to the image
**text_field_data_list (list, optional)**|Info for field_key and its match method,<br>    and either field_value_pos w.r.t key or field_value_bbox.<br>    Defaults to [TEXT_FIELD_DATA_DICT].
**config_params_dict (dict, optional)**|Additional info for position of value w.r.t key and<br>    within_bbox, eliminate_list, within_bbox, eliminate_list, scaling_factor and page number.<br>    Defaults to CONFIG_PARAMS_DICT.
**file_data_list (list, optional)**|List of all file datas. Each file data has the path to<br>    supporting document and page numbers, if applicable. Defaults to None.


**Output:**

Param|Description
---|----
**dict**|Dict of extracted info.
### Initialization
Creates an instance of Checkbox Extractor.
```python
class CheckboxExtractor(get_text_provider:infy_field_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		search_text_provider:infy_field_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		temp_folderpath:str,
	logger=None,
	debug_mode_check=False):
```

**Input:**

Argument|Description
---|----
**get_text_provider (DataServiceProviderInterface)**|Provider to get text either word,<br>    line or phrases
**search_text_provider (DataServiceProviderInterface)**|Provider to search the text in the image.
**temp_folderpath (str)**|Path to temp folder.
**logger (logging.Logger, optional)**|Logger object. Defaults to None.
**debug_mode_check (bool, optional)**|To get debug info while using the API. Defaults to False.


**Output:**

None

### API - extract_all_fields
API to extract all checkboxes by contour detection automatically
```python
def extract_all_fields(image_path:str,
		config_params_dict:{'min_checkbox_text_scale': None,
		'max_checkbox_text_scale': None,
		'field_state_pos': None,
		'page': 1,
		'eliminate_list': [],
		'scaling_factor': {'hor': 1,
		'ver': 1},
	'within_bbox': []}=None,
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None):
```

**Input:**

Argument|Description
---|----
**image_path (str)**|Path to the image
**config_params_dict (CONFIG_PARAMS_DICT, optional)**|Additional info for min and<br>    max checkbox height to text height ratio, position of state w.r.t key,<br>    within_bbox, eliminate_list, scaling_factor and page number.<br>    Defaults to CONFIG_PARAMS_DICT.
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas. Each file data<br>    has the path to supporting document and page numbers, if applicable. Defaults to None.


**Output:**

Param|Description
---|----
**dict**|Dict of extracted info.

### API - extract_custom_fields
API to extract checkboxes using given repective keys for each checkbox or bbox of checkbox
```python
def extract_custom_fields(image_path:str,
		checkbox_field_data_list:[{'field_key': [''],
		'field_key_match': {'method': 'normal',
		'similarityScore': 1},
		'field_state_pos': 'left',
		'field_state_bbox': []}],
		config_params_dict:{'min_checkbox_text_scale': None,
		'max_checkbox_text_scale': None,
		'field_state_pos': None,
		'page': 1,
		'eliminate_list': [],
		'scaling_factor': {'hor': 1,
		'ver': 1},
	'within_bbox': []}=None,
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None):
```

**Input:**

Argument|Description
---|----
**image_path (str)**|Path to the image
**checkbox_field_data_list (CHECKBOX_FIELD_DATA_LIST)**|Info for field_key and its match method,<br>    or either field_state_pos w.r.t key or field_state_bbox.<br>    Defaults to [CHECKBOX_FIELD_DATA_DICT].
**config_params_dict (CONFIG_PARAMS_DICT, optional)**|Additional info for min and max<br>    checkbox height to text height ratio, position of state w.r.t key,<br>    within_bbox, eliminate_list, scaling_factor and page number..<br>    Defaults to CONFIG_PARAMS_DICT.
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas. Each file data<br>    has the path to supporting document and page numbers, if applicable. Defaults to None.


**Output:**

Param|Description
---|----
**dict**|Dict of extracted info.
### Initialization
Creates an instance of Radio button Extractor.
```python
class RadioButtonExtractor(get_text_provider:infy_field_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		search_text_provider:infy_field_extractor.interface.data_service_provider_interface.DataServiceProviderInterface,
		temp_folderpath:str,
	logger=None,
	debug_mode_check=False):
```

**Input:**

Argument|Description
---|----
**get_text_provider (DataServiceProviderInterface)**|Provider to get text either word,<br>    line or phrases
**search_text_provider (DataServiceProviderInterface)**|Provider to search the text in the image.
**temp_folderpath (str)**|Path to temp folder.
**logger (logging.Logger, optional)**|Logger object. Defaults to None.
**debug_mode_check (bool, optional)**|To get debug info while using the API. Defaults to False.


**Output:**

None

### API - extract_all_fields
API to extract all radiobuttons by template match automatically
```python
def extract_all_fields(image_path:str,
		config_params_dict:{'min_radius_text_scale': None,
		'max_radius_text_scale': None,
		'field_state_pos': None,
		'template_checked_folder': None,
		'template_unchecked_folder': None,
		'page': 1,
		'eliminate_list': [],
		'scaling_factor': {'hor': 1,
		'ver': 1},
	'within_bbox': []}=None,
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None):
```

**Input:**

Argument|Description
---|----
**image_path (str)**|Path to the image
**config_params_dict (CONFIG_PARAMS_DICT, optional)**|Additional info for min and<br>    max radiobutton radius to text height ratio, position of state w.r.t key,<br>    within_bbox, eliminate_list, scaling_factor and page number.<br>    Defaults to CONFIG_PARAMS_DICT.
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas. Each file data<br>    has the path to supporting document and page numbers, if applicable. Defaults to None.


**Output:**

Param|Description
---|----
**dict**|Dict of extracted info.

### API - extract_custom_fields
API to extract radiobuttons using given respective keys for each radiobutton or
    bbox of radiobuttons
```python
def extract_custom_fields(image_path:str,
		radiobutton_field_data_list:[{'field_key': [''],
		'field_key_match': {'method': 'normal',
		'similarityScore': 1},
		'field_state_pos': 'left',
		'field_state_bbox': []}],
		config_params_dict:{'min_radius_text_scale': None,
		'max_radius_text_scale': None,
		'field_state_pos': None,
		'template_checked_folder': None,
		'template_unchecked_folder': None,
		'page': 1,
		'eliminate_list': [],
		'scaling_factor': {'hor': 1,
		'ver': 1},
	'within_bbox': []}=None,
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None):
```

**Input:**

Argument|Description
---|----
**image_path (str)**|Path to the image
**radiobutton_field_data_list (RADIOBUTTON_FIELD_DATA_LIST)**|Info for field_key and<br>    its match method, and either field_state_pos w.r.t key or field_state_bbox.<br>    Defaults to [RADIOBUTTON_FIELD_DATA_DICT].
**config_params_dict (CONFIG_PARAMS_DICT, optional)**|Additional info for min and<br>    max radiobutton radius to text height ratio, position of state w.r.t key,<br>    within_bbox, eliminate_list, scaling_factor and page number<br>    Defaults to CONFIG_PARAMS_DICT.
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas.<br>    Each file data has the path to supporting document and page numbers, if applicable.<br>    Defaults to None.


**Output:**

Param|Description
---|----
**dict**|Dict of extracted info.
### Initialization
Creates a Tesseract Data Service Provider
```python
class OcrDataServiceProvider(ocr_parser_object:infy_ocr_parser.ocr_parser.OcrParser,
	logger:logging.Logger=None,
	log_level:int=None):
```

**Input:**

Argument|Description
---|----
**ocr_parser_object (ocr_parser.OcrParser)**|ocr parser
**logger (logging.Logger, optional)**|Logger object. Defaults to None.
**log_level (int, optional)**|Logging Level. Defaults to None.


**Output:**

None

### API - get_bbox_for
Method to return the text from the
image from the text_bbox as a list of dictionary.
```python
def get_bbox_for(img:<built-in function array>,
		text:[''],
		text_match_method:{'method': <class 'str'>,
		'similarityScore': <class 'float'>,
		'maxWordSpace': <class 'str'>},
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None,
		additional_info:{'scaling_factor': {'hor': 1,
		'ver': 1},
	'pages': <class 'list'>}=None,
	temp_folderpath:str=None) -> [{'text': <class 'str'>,
		'bbox': <class 'list'>}]:
```

**Input:**

Argument|Description
---|----
**img (np.array)**|Read image as np array of the original images
**text (TEXT)**|Text
**text_match_method (TEXT_MATCH_METHOD)**|Method (`normal` or `regex`) used to match the text.
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas. Each file data has the path to<br>    supporting document and page numbers, if applicable.<br>    When multiple files are passed, provider has to pick the right file<br>    based on the image dimensions or type of file extension. Defaults to None.
**additional_info (ADDITIONAL_INFO, optional)**|Additional info. Defaults to None.
**temp_folderpath (str, optional)**|Path to temp folder. Defaults to None.


**Output:**

Param|Description
---|----
**BBOX**|list of dict containing text and its bbox.

### API - get_tokens
Method to return the text from the
    image from the text_bbox as a list of dictionary.
```python
def get_tokens(token_type_value:int,
		img:<built-in function array>,
		text_bbox:[0,
	0,
	0,
	0],
		file_data_list:[{'path': <class 'str'>,
	'pages': <class 'list'>}]=None,
		additional_info:{'scaling_factor': {'hor': 1,
		'ver': 1},
	'pages': <class 'list'>}=None,
	temp_folderpath:str=None) -> [{'text': <class 'str'>,
		'bbox': <class 'list'>}]:
```

**Input:**

Argument|Description
---|----
**token_type_value (int)**|Type of text to be returned.
**img (np.array)**|Read image as np array of the original image.
**text_bbox (BBOX)**|Text bbox
**file_data_list (FILE_DATA_LIST, optional)**|List of all file datas.<br>    Each file data has the path to supporting document and page numbers, if applicable.<br>    When multiple files are passed, provider has to pick the right file<br>    based on the image dimensions or type of file extension.<br>    Defaults to None.
**additional_info (ADDITIONAL_INFO, optional)**|Additional info. Defaults to None.
**temp_folderpath (str, optional)**|Path to temp folder. Defaults to None.


**Output:**

Param|Description
---|----
**GET_TOKENS_OUTPUT**|list of dict containing text and its bbox.
