
----------------------------------------------
## To generate OCR file using Tesseract engine
----------------------------------------------
java -jar infy-ocr-engine-0.0.1.jar --fromfile <InputFile> --modeldir <ModelDir> 
    --ocrformat <hocr|txt> [--todir <OutputDir>]  [--lang <Language>]

--fromfile 
    The full path of the input file to be converted.

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

EXAMPLES:
    1) Output will be saved to default folder ("C:\TEMP\eng.png.hocr")
       java -jar infy-ocr-engine-0.0.1.jar --fromfile "C:\Temp\eng.png" --modeldir "C:\MyProgramFiles\AI\models\tessdata" --ocrformat "hocr"
    2) Ouput will be saved to custom folder ("C:\TEMP\output\eng.png.txt") 
       java -jar infy-ocr-engine-0.0.1.jar --fromfile "C:\Temp\eng.png" --modeldir "C:\MyProgramFiles\AI\models\tessdata" --ocrformat "txt" --todir "C:\Temp\output"

---------------------------------------