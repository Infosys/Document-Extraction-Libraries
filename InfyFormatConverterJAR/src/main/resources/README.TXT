
---------------------------------------
## To Convert PDF page(s) to image(s)
---------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToImg --fromfile <InputFile> [--dpi <DPI>]
    [--todir <OutputDir>] [--pages <PageNumbers>]

--fromfile 
    The full path of the input file to be converted.
  
--dpi
    The DPI of the output image file(s). 
    Default is 300.
  
--todir
    The output directory where the output file(s) will be saved to.
    Default is folder with name <InputFile>_files  
    If this folder doesn't exist, it will be created automatically.
  
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.

EXAMPLES:
    1) Images will be saved to default folder ("D:\TEMP\invoice23.pdf_files\")
       java -jar infy-format-converter-0.0.13.jar PdfToImg --fromfile "D:\TEMP\invoice23.pdf"
    2) Images will be saved to custom folder  
       java -jar infy-format-converter-0.0.13.jar PdfToImg --fromfile "D:\TEMP\invoice23.pdf" --todir "D:\TEMP\myinvoices"
    3) Images will be created using custom DPI
       java -jar infy-format-converter-0.0.13.jar PdfToImg --fromfile "D:\TEMP\invoice23.pdf" --dpi 400
    4) Only custom pages will be converted/saved  
       java -jar infy-format-converter-0.0.13.jar PdfToImg --fromfile "D:\TEMP\invoice23.pdf" --pages 1-5,7,8-10


---------------------------------------
## To Extract image(s) from PDF page(s)
---------------------------------------
java -jar infy-format-converter-0.0.13.jar ImgFromPdf --fromfile <InputFile> [--imgformats <ImageFormats>]
    [--todir <OutputDir>] [--pages <PageNumbers>]

--fromfile 
    The full path of the input file from which to extract images.
  
--imgformats
    The image format(s) of the output file(s). 
    They need to be provided as comma separated values.    
    E.g. jpg,png
    Default is jpg.
  
--todir
    The output directory where the output file(s) will be saved to.
    Default is folder with name <InputFile>_files  
    If this folder doesn't exist, it will be created automatically.
  
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.

EXAMPLES:
    1) Images will be saved to default folder ("D:\TEMP\invoice23.pdf_files\")
       java -jar infy-format-converter-0.0.13.jar ImgFromPdf --fromfile "D:\TEMP\invoice23.pdf"

---------------------------------------
## To Convert PDF document to text file
---------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToText --fromfile <InputFile> [--todir <OutputDir>] 
    [--pages <PageNumbers>] [--pagewidth <PageWidth>] [--pageheight <PageHeight>]
    [--bbox[?] <X,Y,W,H>] 

--fromfile 
    The full path of the input file to be converted.
  
--todir
    The output directory where the output files will be saved to.
    Default is empty and prints output in CLI.
    If this folder doesn't exist, it will be created automatically.
    	
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.

--bbox[?]
	The identifier used for a bounding box coordinates.
	Applicable for all pages.
	E.g. bbox --bbox1 1707,49,467,441 --bboxA 1707,49,467,441
	
--pagewidth & --pageheight
    The page width and height of source image from where bbox coordinates were fetched.
    This will be used to scale bbox coordinates to match the dimensions of PDF file.
    If not specified, bbox coordinates will be used as-is.  

EXAMPLES:
    1) A single file containing text from all pages of document will be saved to default folder ("D:\TEMP")
       java -jar infy-format-converter-0.0.13.jar PdfToText --fromfile "D:\TEMP\invoice23.pdf"


------------------------------------------------------------------------------
## To Convert PDF document to JSON file
------------------------------------------------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToJson --fromfile <InputFile> [--todir <OutputDir>] 
    [--pages <PageNumbers>] [--pagewidth <PageWidth>] [--pageheight <PageHeight>]
    [--bbox1 <X,Y,W,H>] 

--fromfile 
    The full path of the input file to be converted.
  
--todir
    The output directory where the output files will be saved to.
    Default is empty and prints output in CLI.
    If this folder doesn't exist, it will be created automatically.
    	
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.

--bbox[?]
	The identifier used for a bounding box coordinates. 
	Applicable for all pages.
	E.g. bbox --bbox1 1707,49,467,441 --bboxA 1707,49,467,441
	
--pagewidth & --pageheight
    The page width and height of source image from where bbox coordinates were fetched.
    This will be used to scale bbox coordinates to match the dimensions of PDF file.
    If not specified, bbox coordinates will be used as-is.  


EXAMPLES:
    1) A single JSON file containing text extracted from given bounding boxes will be 
       saved to default folder ("D:\TEMP") ("D:\TEMP")
       java -jar infy-format-converter-0.0.13.jar PdfToJson --fromfile "D:\TEMP\invoice23.pdf" --pages 1 
            --pagewidth 2000 --pageheight 3000 --bbox1 100,100,50,50 --bbox2 200,200,50,50

---------------------------------------
## To Convert PDF document to HTML file
---------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToHtml --fromfile <InputFile> [--todir <OutputDir>]  

--fromfile 
    The full path of the input file to be converted.
  
--todir
    The output directory where the output files will be saved to.
    Default is same folder containing <InputFile>. 
    If this folder doesn't exist, it will be created automatically.
    	

EXAMPLES:
    1) A single file containing HTML format of all pages of document will be saved to default folder ("D:\TEMP")
       java -jar infy-format-converter-0.0.13.jar PdfToHtml --fromfile "D:\TEMP\invoice23.pdf"       


---------------------------------------
## To Convert image(s) to PDF document
---------------------------------------
java -jar infy-format-converter-0.0.13.jar ImgToPdf --fromfile <InputFile1,InputFile2,...> --tofile <OutputFile>
    [--watermarktext <PlainText>]

--fromfile 
    The full path of the input file(s) to be converted separated by pipe(|) character.
  
--tofile
    The full path of the output file to be saved.
    
--watermarktext
    A plain text which will be added as a watermark on every page.      
    	

EXAMPLES:
    1) A single PDF file containing two pages will be created with the given watermark on each page. 
       java -jar infy-format-converter-0.0.13.jar ImgToPdf --fromfile D:\1.jpg|D:\2.jpg --tofile D:\new.pdf --watermarktext "NOT ORIGINAL"

---------------------------------------
## To convert Word to PDF
---------------------------------------
java -jar infy-format-converter-0.0.13.jar WordToPdf --fromfile <InputFile> --tofile <OutputFile>
    [--timeout <TimeoutInSecs>] 

--fromfile 
    The full path of the input file to be converted.
    
--tofile 
    The full path of the output file after conversion. 
    
--timeout   
    The time to wait in seconds before abandoning the conversion process.
    Default is 60.
	
EXAMPLES	
    java -jar infy-format-converter-0.0.13.jar WordToPdf --fromfile "D:\TEMP\orders.docx" --tofile "D:\TEMP\orders.pdf" --timeout 120
    
------------------------------------------------------
## To plot bounding boxes on image using HOCR XML file
------------------------------------------------------
java -jar infy-format-converter-0.0.13.jar PlotBbox --fromfile <InputFile> --hocrfile <OutputFile> --todir <OutputDir>

--fromfile 
    The full path of the image file to be used as reference for plotting bounding box.
    
--hocrfile 
    The full path of the HOCR XML file containing bound box details. 
    
--todir
    The output directory where the images with bounding boxes will be created.
    Default is same folder containing <InputFile>. 
    If this folder doesn't exist, it will be created automatically.
	
EXAMPLES	
    java -jar infy-format-converter-0.0.13.jar PlotBbox --fromfile "D:\TEMP\1.jpg" --hocrfile "D:\TEMP\1.hocr" --todir "D:\TEMP\output"

------------------------------------------------------
## To create text bbox file from a native PDF file
------------------------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToTextBbox --fromfile <InputFile> --todir <OutputDir>
    [--plotbbox True] [--pages <PageNumbers>]

--fromfile 
    The full path of the native PDF file from which to extract text + bbox.
    
--todir
    The output directory where the output file will be created.
    Default is same folder containing <InputFile>. 
    If this folder doesn't exist, it will be created automatically.

--plotbbox   
    If set to True, will plot bbox on copy of native PDF file.
    This file will be saved in same folder containing text bbox file.
    Default is False.
    
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.    
	
EXAMPLES	
    java -jar infy-format-converter-0.0.13.jar PdfToTextBbox --fromfile "D:\TEMP\native.pdf" --todir "D:\TEMP\output"


------------------------------------------------------
## To create image bbox file from a PDF file
------------------------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToImageBbox --fromfile <InputFile> --todir <OutputDir>
    [--plotbbox True] [--pages <PageNumbers>] [--saveresource True]

--fromfile 
    The full path of the native PDF file from which to extract text + bbox.
    
--todir
    The output directory where the output file will be created.
    Default is same folder containing <InputFile>. 
    If this folder doesn't exist, it will be created automatically.

--plotbbox   
    If set to True, will plot bbox on copy of native PDF file.
    This file will be saved in same folder containing text bbox file.
    Default is False.
    
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.    
    
--saveresource
	Save resouces such as image to path specified in todir.
	Default is False    
	
EXAMPLES	
    java -jar infy-format-converter-0.0.13.jar PdfToImageBbox --fromfile "D:\TEMP\my.pdf" --todir "D:\TEMP\output"


    
---------------------------------------
## To Split multipage PDF to multiple PDF
---------------------------------------
java -jar infy-format-converter-0.0.13.jar PdfToMultiPdf --fromfile <InputFile>
    [--todir <OutputDir>] [--pages <PageNumbers>]

--fromfile 
    The full path of the input file to be converted.
  
--todir
    The output directory where the output file(s) will be saved to.
    Default is folder with name <InputFile>_files  
    If this folder doesn't exist, it will be created automatically.
  
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    Ranges are also allowed. 
    E.g. 1-5,7,8-10 
    Default is all pages.

EXAMPLES:
    1) Images will be saved to default folder ("D:\TEMP\invoice23.pdf_files\")
       java -jar infy-format-converter-0.0.13.jar PdfToMultiPdf --fromfile "D:\TEMP\invoice23.pdf"
    2) Images will be saved to custom folder  
       java -jar infy-format-converter-0.0.13.jar PdfToMultiPdf --fromfile "D:\TEMP\invoice23.pdf" --todir "D:\TEMP\myinvoices"
    4) Only custom pages will be converted/saved  
       java -jar infy-format-converter-0.0.13.jar PdfToMultiPdf --fromfile "D:\TEMP\invoice23.pdf" --pages 1-5,7,8-10
       
  ---------------------------------------
## Rotate PDF pages
---------------------------------------
java -jar infy-format-converter-0.0.13.jar rotatePdfPage --fromfile <InputFile> --angles <Angles>
    [--todir <OutputDir>] [--pages <PageNumbers>]

--fromfile 
    The full path of the input file to be converted.
  
--todir
    The output directory where the output file(s) will be saved to.
    If this folder doesn't exist, it will be created automatically.
  
--pages
    The specific pages from the input file to be converted.
    They need to be provided as comma separated values.
    E.g. 1,2,3 
    Default is all pages.

--angles
	Rotate angle like 0|90|180|270
	They need to be provided as comma separated values.
	E.g. 90,180,90
	Default is 0
	
EXAMPLES:
    1) Images will be saved to default folder ("D:\TEMP\invoice23.pdf_files\")
       java -jar infy-format-converter-0.0.13.jar rotatePdfPage --fromfile "D:\TEMP\invoice23.pdf" --angle "90"
    2) Images will be saved to custom folder  
       java -jar infy-format-converter-0.0.13.jar rotatePdfPage --fromfile "D:\TEMP\invoice23.pdf" --todir "D:\TEMP\myinvoices" --angle "90"
    4) Only custom pages will be converted/saved  
       java -jar infy-format-converter-0.0.13.jar rotatePdfPage --fromfile "D:\TEMP\invoice23.pdf" --pages "1,2,3" --angles "90,180,90"

    