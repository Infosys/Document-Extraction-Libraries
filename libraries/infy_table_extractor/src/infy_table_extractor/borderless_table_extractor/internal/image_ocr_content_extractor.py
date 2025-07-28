# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Image OCR content Extractor

This script allows the user to take an image as a input and extract text content from the images using tesseract 
and leveraging hocr enhancement techniques for enhanced accuracy

This tool accepts jpg files

This script requires tools such as tesseract, xpdf and hocr-tools, the path of these tools should be added
to the configuration file

This file can also be imported as a module and contains the following
functions:

    * extract - this function takes image as an input and returns text content extracted with same layout as an output
"""
import pytesseract
import os
import cv2
import shutil
import traceback


class ImageOCRContentExtractor:
    __temp_path = None

    def __init__(self, tesseract_path, temp_path, logger, debug_mode_check=False):
        """ 
        The constructor for ImageOCRContentExtractor class. 

        Parameters: 
        logger: Instance of the logger      
        """
        self.debug_mode_check = debug_mode_check
        self.logger = logger
        self.__temp_path = temp_path
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def extract_enhanced_ocr(self, img_file_path, temp_folder_path, processing_msg=[], psm='6'):
        error = None
        enhanced_hocr_file_path = None
        try:
            hocrpath, filename, input_path = self.generate_ocr(
                img_file_path, temp_folder_path, psm)
            processing_msg.append(
                f"Generated hocr file {hocrpath} for the given image {img_file_path}.")
            enhanced_hocr_file_path, processing_msg_1 = self.__enhanceHocr(
                hocrpath, filename, input_path, temp_folder_path, temp_folder_path)
            processing_msg += processing_msg_1
        except Exception as e:
            error = traceback.format_exc()
            self.logger.info(img_file_path)
            error = e.args[0]
        return enhanced_hocr_file_path, temp_folder_path, error

    def __parse_hocr(self, hocr_file=None, regex=None):
        """Parse the hocr file and find a reasonable bounding box for each of the strings
        in search_terms.  Return a dictionary with values as the bounding box to be used for
        extracting the appropriate text.

        Parameters:
            search_terms = Tuple, A tuple of search terms to look for in the HOCR file.

        Returns:
            box_dict = Dictionary, A dictionary whose keys are the elements of search_terms and values
            are the bounding boxes where those terms are located in the document.
        """
        from bs4 import BeautifulSoup as bs
        if not hocr_file:
            raise ValueError(
                'The parser must be provided with an HOCR file handle.')

        hocr = open(hocr_file, 'r+b').read()
        soup = bs(hocr, features='xml')
        words = soup.find_all('span', class_='ocrx_word')

        result = dict()

        for word in words:

            w = word.get_text().lower()
            if len(w) > 1:
                bbox = word['title'].split(';')
                bbox = bbox[0].split(' ')
                bbox = tuple([int(x) for x in bbox[1:]])

                id = word['id']

                result.update({id: [bbox, w]})

            else:
                pass

        return result

    def __updatehocr(self, updateddict, hocr_file=None):
        """Parse the hocr file and find a reasonable bounding box for each of the strings
        in search_terms.  Return a dictionary with values as the bounding box to be used for
        extracting the appropriate text.

        Parameters:
            updateddict = Dictionary, A dictionary with updated values after extraction through OCR

        Returns:
            hocr = Hocr, file with rextraction values
        """

        from bs4 import BeautifulSoup as bs
        if not hocr_file:
            raise ValueError(
                'The parser must be provided with an HOCR file handle.')

        hocr = open(hocr_file, 'r+b').read()
        soup = bs(hocr, features='xml')

        for key, values in updateddict.items():
            words = soup.find('span', class_='ocrx_word', id=key)

            words.string = values[1]

        return soup

    def generate_ocr(self, imagepath, ocr_dir, psm):
        """Parse the image file, get the hocr output, save the hocr file and return back

        Parameters:
            imagepath = path to the image

        Returns:
            hocrpath = Hocr, path to hocr file
        """
        psm = str(psm)
        if psm == "6":
            custom_config = r'-c preserve_interword_spaces=1 --oem 1 --psm 6'
        else:
            custom_config = r'--psm '+psm
        hocr = pytesseract.image_to_pdf_or_hocr(
            imagepath, extension='hocr', config=custom_config)
        filename = os.path.basename(imagepath)
        (file, ext) = os.path.splitext(filename)
        hocrfile = f"{file}_psm={psm}.hocr"
        hocrpath = ocr_dir + "/"+hocrfile
        with open(hocrpath, "w+b") as outfile:
            outfile.write(hocr)
        return hocrpath, file, imagepath

    def __enhanceHocr(self, hocrpath, filename, imagepath, temp_img_path, enhancedHocrdir):
        """Parse the image file, get the hocr output, save the hocr file and return back

        Parameters:
            hocrpath = path of the original hoc file
            filename = name of the file
            imagepath = path to the image

        Returns:
            hocrpath = Hocr, path to hocr file
        """
        processing_msg = []
        msg = "Hocr enhancement in progress for: {}".format(hocrpath)
        self.logger.info(msg)
        processing_msg.append(msg)
        try:
            worddict = self.__parse_hocr(hocr_file=hocrpath)
        except Exception as e:
            msg = "Error while parsing the hocr to enhance."
            processing_msg.append(msg)
            self.logger.error(msg)

        cordinates_dict = {}
        for key, value in worddict.items():
            self.logger.info(
                "Hocr enhancement in progress for image: {}".format(imagepath))
            try:
                bounding_box_image = cv2.imread(imagepath)
            except Exception as e:
                self.logger.error(
                    "Error reading the image for hocr enhancement: {}".format(imagepath))
            h, w, _ = bounding_box_image.shape
            self.logger.info(
                "Bounding box image shape for hocr enhancement: {}".format(h, w))

            startx, starty, endx, endy = value[0]

            cordinate_key = str(starty) + str(endx) + str(endy)
            if cordinate_key in cordinates_dict:
                value[1] = ""
            else:
                cordinates_dict[cordinate_key] = startx

                width = endx - startx
                height = endy - starty

                self.logger.info("Size of cropped image : {}".format(
                    startx, starty, endx, endy))

                cropped_image = bounding_box_image[starty -
                                                   0: starty + height + 0, startx - 0: startx + width + 0]

                outputImage = cv2.copyMakeBorder(
                    cropped_image,
                    10,
                    10,
                    10,
                    10,
                    cv2.BORDER_CONSTANT,
                    value=[255, 255, 255]
                )

                cropped_dir = temp_img_path + "/cropped/"

                if not os.path.exists(cropped_dir):
                    os.makedirs(cropped_dir)

                self.logger.info("Cropped directory is ".format(cropped_dir))

                file_name_prefix = self.__convert_to_file_safe_text(value[1])
                cropped_image_path = f"{cropped_dir}\{file_name_prefix}_[{startx},{starty},{height},{width}].jpg"

                self.logger.info(
                    "Cropped image path is ".format(cropped_image_path))

                cv2.imwrite(cropped_image_path, outputImage)
                try:
                    newvalue = pytesseract.image_to_string(
                        cropped_image_path)
                except:
                    newvalue = "error"

                # os.remove(cropped_image_path)

                if newvalue != "" and newvalue != "error":
                    value[1] = newvalue
            worddict.update({key: value})

        soup = self.__updatehocr(worddict, hocr_file=hocrpath)

        import codecs

        enhancedHocrpath = enhancedHocrdir + "/" + filename+"_enhanced.hocr"

        with codecs.open(enhancedHocrpath, "w", encoding='utf8') as outfile:
            outfile.write(str(soup))
        self.logger.info(
            "Hocr ehancement completed. Hocr path is : {}".format(enhancedHocrpath))
        processing_msg.append(
            f"Hocr enhancement completed and enhanced path is {enhancedHocrpath}")

        return enhancedHocrpath, processing_msg

    def __create_dir(self, dir):
        dir = os.path.abspath(dir)
        self.__delete_dir(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def __delete_dir(self, dir):
        if not self.debug_mode_check and os.path.exists(dir):
            shutil.rmtree(dir, ignore_errors=True)

    def __convert_to_file_safe_text(self, raw_text):
        # If text is containing only ASCII chars, then return as-is
        if (all(ord(c) < 128 for c in raw_text)):
            return raw_text

        allowed_additional_characters = (' ', '.', '_')
        return "".join(c for c in raw_text if c.isalnum() or c in allowed_additional_characters).rstrip()
