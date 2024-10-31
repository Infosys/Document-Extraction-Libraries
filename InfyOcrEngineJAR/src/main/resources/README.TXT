
----------------------------------------------
## To generate OCR file using Tesseract engine
----------------------------------------------
java -jar infy-ocr-engine-0.0.1.jar --fromfile <InputFile> --modeldir <ModelDir> 
    --ocrformat <hocr|txt> [--todir <OutputDir>]  [--lang <Language>]

--fromfile 
    The full path of the input file to be converted.
    Path to an image or a json are allowed.
    JSON should be in the format of list of dictionary where you can achieve bulk extraction
        E. g. 
        [
            {
                "image_path": "path to image",
                "data"
            },
            ...
        ]

--modeldir
    The directory containing the model files. E.g. "C:\MyProgramFiles\AI\models\tessdata"
    The model files are of the format "*.traineddata". E.g. "eng.traineddata"
    The language-specific model files can be downloaded from https://github.com/tesseract-ocr/tessdata
  
--todir
    The output directory where the output files will be saved to.
    Default is same folder containing <InputFile>. 
    If this folder doesn't exist, it will be created automatically.

--lang
    The three character language code from the list of supported languages. 
    E.g. eng,deu,hin
    Default is 'eng'

--ocrformat
    The output format of OCR. Valid values are "hocr" or "txt".
    Multiple values are allowed: hocr,txt

--psm
    The page segmentation mode to be set. Below are the supported values.
    E.g. '3', '6', '7'
    Default is '3'

EXAMPLES:
    1) Output will be saved to default folder ("C:\TEMP\eng.png.hocr")
       java -jar infy-ocr-engine-0.0.2.jar --fromfile "C:\Temp\eng.png" --modeldir "C:\MyProgramFiles\AI\models\tessdata" --ocrformat "hocr"
    2) Ouput will be saved to custom folder ("C:\TEMP\output\eng.png.txt") 
       java -jar infy-ocr-engine-0.0.2.jar --fromfile "C:\Temp\eng.png" --modeldir "C:\MyProgramFiles\AI\models\tessdata" --ocrformat "txt" --psm "3" --todir "C:\Temp\output"
    3) Ouput will be saved to custom folder ("C:\TEMP\output\image_list.json_infy_ocr_engine.json")
       java -jar infy-ocr-engine-0.0.2.jar --fromfile "C:\Temp\images_list.json" --modeldir "C:\MyProgramFiles\AI\models\tessdata" --ocrformat "txt" --psm "3" --todir "C:\Temp\output"
---------------------------------------