# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


from os import path
import warnings
import copy
import numpy as np
import cv2
from PIL import Image
from infy_field_extractor.internal.constants import Constants
from infy_field_extractor.internal.common_utils import CommonUtils


class ExtractorHelper():
    """Helper class for data extraction"""
    @staticmethod
    def extract_with_text_coordinates(
            image, bboxes_text, get_text_provider, file_data_list, additional_info,
            fieldboxes, logger, temp_folderpath, field="checkbox", debug_mode_check=False):
        """
        Method to help extract fields using image, imagepath, bounding boxes coordinates of the text and
        bounding boxes coordinates of the field
        """
        _, width = image.shape
        # filter fieldboxes from bboxes_text
        bboxes_text = ExtractorHelper.filter_fieldboxes_from_ocr_words(
            fieldboxes, bboxes_text)

        if debug_mode_check:
            img_copy = image.copy()
            bboxes_list = [x['bbox'] for x in bboxes_text]
            img_copy = ExtractorHelper.draw_bboxes_on_image(
                img_copy, bboxes_list, Constants.COLOR_BLUE, thickness=4)
            ExtractorHelper.save_image(
                img_copy, f'{temp_folderpath}/text_bboxes.jpg')

        # getting phrases
        # bboxes_text = ocr_parser_object.get_tokens_from_ocr(
        #     token_type_value=3, ocr_word_list=bboxes_text)
        additional_info['word_bbox_list'] = bboxes_text
        bboxes_text = get_text_provider.get_tokens(
            3, image, [], file_data_list, additional_info, temp_folderpath)

        # dividing a series of horizontal fieldboxes as each bounding box
        Y_SCALE = 6
        H_SCALE = 3
        c = fieldboxes[0]
        # appends the first line in bboxes_line_list
        bboxes_line_list = [[0, c[Constants.BB_Y]-c[Constants.BB_H]//Y_SCALE,
                             width, c[Constants.BB_H]+c[Constants.BB_H]//H_SCALE]]
        # list to add a new line
        temp_list = []
        # to track the count of the number of lines in bboxes_line_list
        count = 0
        # to track if any new word found which is not present in any bboxes_line_list
        flag = False
        for f in fieldboxes:
            for i in bboxes_line_list:
                count += 1
                # if words already there in the bboxes_list_line then set flag
                # as True and moves to the next line
                if(i[Constants.BB_Y] <= f[Constants.BB_Y] <= i[Constants.BB_Y]+i[Constants.BB_H]):
                    flag = True
                elif(flag is False and count == len(bboxes_line_list)):
                    temp_list.append(
                        [0, f[Constants.BB_Y]-f[Constants.BB_H]//Y_SCALE, width,
                            f[Constants.BB_H]+f[Constants.BB_H]//H_SCALE])
            bboxes_line_list = bboxes_line_list + temp_list
            temp_list = []
            flag = False
            count = 0

        if debug_mode_check:
            img_copy = image.copy()
            bboxes_list = bboxes_line_list
            img_copy = ExtractorHelper.draw_bboxes_on_image(
                img_copy, bboxes_list, Constants.COLOR_BLUE, thickness=4)
            ExtractorHelper.save_image(
                img_copy, f'{temp_folderpath}/text_bboxes_pass2.jpg')

        # getting the final result
        # for each line divided calls the __get_status_for_each_line method
        result = {}
        done_fields_dList = []
        count = 0
        for bbox_line in bboxes_line_list:
            count += 1
            logger.info(
                "Extracting checkboxes from line "+str(count)+":")
            r, done_fieldsList = ExtractorHelper.get_status_for_each_line(
                bbox_line, bboxes_text, fieldboxes, image, logger, field)
            done_fields_dList = done_fields_dList+done_fieldsList
            result.update(r)
        return result, done_fields_dList

    @staticmethod
    def get_status_for_each_line(bbox_line, bboxes_text, fieldboxes, image, logger, field):
        """
        It returns a dictionary with text as key and the field's status or bbox as value
        """

        # stores the x,y,width and height of the bbox of the line
        _ = bbox_line[Constants.BB_X]
        y_l = bbox_line[Constants.BB_Y]
        _ = bbox_line[Constants.BB_W]
        h_l = bbox_line[Constants.BB_H]
        # filter fieldboxes present in bbox_line
        fieldboxes_line = []
        for c in fieldboxes:
            if(y_l <= c[Constants.BB_Y] <= y_l+h_l):
                fieldboxes_line.append(c)

        # filter texts present in bbox_line
        texts_line = []
        for t in bboxes_text:
            # gets all the text even if a small region of the text is in the line, therefore
            # matches both the y-coordinate and y-coordinate+height of the text
            # lying inside the line's bbox
            if((y_l <= t.get("bbox")[Constants.BB_Y] <= (y_l+h_l)) or
                    (y_l <= (t.get("bbox")[Constants.BB_Y]+t.get("bbox")[Constants.BB_H]) <= (y_l+h_l))):
                texts_line.append(t)

        # check if the fieldboxes are at the right or left side of the texts
        # initializing isfieldRight as True, assuming that the last bbox in the line is of checkbox
        isfieldRight = True
        last_field = fieldboxes_line[len(fieldboxes_line)-1]
        y_c = last_field[Constants.BB_Y]
        h_c = last_field[Constants.BB_H]
        for t in texts_line:
            x_t = t.get("bbox")[Constants.BB_X]
            y_t = t.get("bbox")[Constants.BB_Y]
            # if the last bbox in the line is a phrase then fieldboxes are on the left side
            if((y_c-(h_c//2) <= y_t <= y_c + h_c) and x_t > last_field[Constants.BB_X]):
                isfieldRight = False
        logger.info(
            "Fieldboxes on the right side of value:"+str(isfieldRight))

        result = {}

        # get the final result
        # the variable adds dictionary with key as the text used for radiobutton and value as its bbox
        done_fields_dList = []
        for f in fieldboxes_line:
            if len(texts_line) == 0:
                break
            # declare closest variable to consider the key for the fielbox which is closest to it
            closest = texts_line[0]
            # if key are to the right of fields, the closest text to the right
            #  of the field is key for that field
            if(isfieldRight is False):
                for t in texts_line:
                    x_t = t.get("bbox")[Constants.BB_X]
                    t_dist = x_t - (f[Constants.BB_X]+f[Constants.BB_W])
                    close_dist = closest.get(
                        "bbox")[Constants.BB_X] - (f[Constants.BB_X]+f[Constants.BB_W])
                    if(close_dist < 0):
                        closest = t
                    if(close_dist > 0 and t_dist > 0 and t_dist < close_dist):
                        closest = t
            # if key are to the left of fields, the closest text to the left of the field
            #  is key for that field
            else:
                for t in texts_line:
                    x_t = t.get("bbox")[Constants.BB_X]
                    w_t = t.get("bbox")[Constants.BB_W]
                    t_dist = f[Constants.BB_X] - x_t - w_t
                    close_dist = f[Constants.BB_X] - (
                        closest.get("bbox")[Constants.BB_X]+closest.get("bbox")[Constants.BB_W])
                    if(close_dist < 0):
                        closest = t
                    if(close_dist > 0 and t_dist > 0 and t_dist < close_dist):
                        closest = t
            text = closest.get("text")
            done_fields_dList.append(closest)
            # if two phrases arranged vertically is meant for that field, it looks for the texts
            # which has almost the same y-coordinate
            X_SCALE = 2
            Y_SCALE = 2
            for t in texts_line:
                x_t = t.get("bbox")[Constants.BB_X]
                y_t = t.get("bbox")[Constants.BB_Y]
                w_t = t.get("bbox")[Constants.BB_W]
                h_t = t.get("bbox")[Constants.BB_H]
                x_ct = closest.get("bbox")[Constants.BB_X]
                y_ct = closest.get("bbox")[Constants.BB_Y]
                # compares the closest text's y-coordinates with the current text
                # which should be more than
                # heigth of the phrase and the x- coordinate should be almost equal
                if((x_t-w_t//X_SCALE) <= x_ct <= (x_t+w_t//X_SCALE) and (Y_SCALE*abs(y_t - y_ct) > h_t)):
                    done_fields_dList.append(t)
                    if(y_ct < y_t):
                        text = closest.get("text") + " " + t.get("text")
                    else:
                        text = t.get("text") + " " + closest.get("text")
                    break
            # if the field is a checkbox then calls the method to see if checkbox checked or not
            if(field == "checkbox"):
                isCheck = ExtractorHelper.check_if_true(
                    image, f, field)
                result[text] = isCheck
            # if the fiels is radio then returns the text as key and radiobutton bbox as value
            elif(field == "radio"):
                result[text] = f

        return result, done_fields_dList

    @staticmethod
    def check_if_true(
            image, field_bbox, field, field_coordinate=[], debug_mode_check=False,
            temp_folderpath=None, img_name=None):
        """
        checks the status of the checkbox/radio using contour detection method
        """
        # to get the image of only field
        x, y, w, h = field_bbox[Constants.BB_X], field_bbox[Constants.BB_Y], \
            field_bbox[Constants.BB_W], field_bbox[Constants.BB_H]
        img = image[y:y+h, x:x+w]
        _, threshold = cv2.threshold(
            img, 170, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if(debug_mode_check is True):
            img = cv2.drawContours(img, contours, -1, (180, 105, 255), 3)
            cv2.imwrite(f'{temp_folderpath}\\{img_name}_contours.png', img)
        if(field == "radio"):
            isCheck = False
            x, y, r = field_coordinate[0] - \
                x, field_coordinate[1] - y, field_coordinate[2]
            for i in range(0, len(contours)):
                cnt = contours[i]
                for c in cnt:
                    if(int(x-r/3) < c[0][0] < int(x+r/3) and int(y - r/3) < c[0][1] < int(y+r/3)):
                        isCheck = True
            return isCheck
        elif(field == "checkbox"):
            MY_CONS_1 = 6
            cv2.drawContours(img, contours, -1, (100, 255, 150), 5)
            # x,y,w,h of the outer most boundary of the checkbox
            x, y = 0, 0
            # to count the number of squares
            count = 0
            # to count junk contours
            count_false_cnt = 0
            # checked_area = 0
            for i in range(0, len(contours)):
                cnt = contours[i]
                epsilon = 0.04*cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                x1, _, w1, h1 = cv2.boundingRect(cnt)
                # counts the if the contours has four edges and if the x-coordinate lies in the range of
                # x-coordinate of the outermost boundary of the checkbox
                if (len(approx) == Constants.RECT_EDGES and x-(w//MY_CONS_1) <= x1 <= x+(w//MY_CONS_1)):
                    count += 1
                elif w1*h1 < 0.05*w*h:
                    count_false_cnt += 1
                # else:
                #     checked_area += w1*h1
                # if there is another contour other than the margins of the checkboxes, then true
            if(len(contours)-count - count_false_cnt > 0):
                return True
            else:
                return False

    @staticmethod
    def filter_fieldboxes_from_ocr_words(fieldboxes, bboxes_text):
        filter_list = []
        # filter fieldboxes from bboxes_text
        for t in bboxes_text:
            for c in fieldboxes:
                x_t = t.get("bbox")[Constants.BB_X]
                y_t = t.get("bbox")[Constants.BB_Y]
                w_t = t.get("bbox")[Constants.BB_W]
                h_t = t.get("bbox")[Constants.BB_H]
                # checks if the fieldbox x-coordinate is in the range of bboxes_text x -coordinate
                # and x-coordinate+width or vice-versa
                # also checks for the fieldbox y-coordinate is in the range of bboxes _text
                if((x_t <= c[Constants.BB_X] <= (x_t+w_t) and
                    y_t <= c[Constants.BB_Y] <= (y_t+h_t)) or
                    (c[Constants.BB_X] <= x_t <= (c[Constants.BB_X]+c[Constants.BB_W]) and
                     c[Constants.BB_Y] <= y_t <= (c[Constants.BB_Y]+c[Constants.BB_H]))):
                    filter_list.append(t)
                    continue
                # checks if the fieldbox y-coordinate is in the range of bboxes_text y-coordinate
                # and x-coordinate+width or vice-versa
                # also checks for the fieldbox x-coordinate is in the range of bboxes _text
                if((x_t <= c[Constants.BB_X] <= (x_t+w_t) and
                    c[Constants.BB_Y] <= y_t <= (c[Constants.BB_Y]+c[Constants.BB_H])) or
                    (c[Constants.BB_X] <= x_t <= (c[Constants.BB_X]+c[Constants.BB_W]) and
                     y_t <= c[Constants.BB_Y] <= (y_t+h_t))):
                    filter_list.append(t)
                    continue
        bboxes_text = [x for x in bboxes_text if x not in filter_list]
        return bboxes_text

    @staticmethod
    def check_image_dpi(imagepath, logger):
        im = Image.open(imagepath)
        try:
            dpi = im.info['dpi']
            if(dpi[0] < Constants.TESSERACT_MIN_DPI and dpi[1] < Constants.TESSERACT_MIN_DPI):
                warning = "The result might be not accurate due to low dpi"
                warnings.warn(warning)
                logger.warning(warning)
        except Exception:
            warning = ("Dpi of the image cannot be extracted: "
                       "The result might be not accurate if the dpi is less than 300")
            warnings.warn(warning)
            logger.warning(warning)

    @staticmethod
    def read_image(image_path, logger, temp_folderpath, coordinates=[], image_to_bw=False):
        if(path.exists(image_path) is False):
            logger.error("property imagepath not found")
            raise Exception("property imagepath not found")
        img_name = path.splitext(path.split(image_path)[1])[0]
        image = cv2.imread(image_path)
        try:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            if image_to_bw:
                img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
        except Exception:
            img = image
        if(coordinates != []):
            if type(coordinates[0]) == dict:
                coordinates = coordinates[0]["bbox"]
            x_img, y_img, width, height = coordinates[Constants.BB_X], coordinates[
                Constants.BB_Y], coordinates[Constants.BB_W], coordinates[Constants.BB_H]
            image = img[y_img:y_img+height, x_img:x_img+width]
            imagepath = temp_folderpath + "//" + img_name + '_crop.jpg'
            PILimage = Image.fromarray(image)
            PILimage.save(imagepath, dpi=(300, 300))
            # cv2.imwrite(path.join(imagepath), image)
        else:
            image = img
            # Save a copy of original image
            temp_imagepath = temp_folderpath + "//" + img_name + '_full.jpg'
            PILimage = Image.fromarray(image)
            PILimage.save(temp_imagepath, dpi=(300, 300))
            imagepath = image_path
        return (image, imagepath, img_name)

    @staticmethod
    def get_closest_fieldbox(fieldboxes, field_pos, phrase_bbox):
        closest = fieldboxes[0]
        if(field_pos == "right"):
            for c in fieldboxes:
                c_dist = c[Constants.BB_X] - \
                    (phrase_bbox[Constants.BB_X] + phrase_bbox[Constants.BB_Y])
                close_dist = closest[Constants.BB_X] - \
                    (phrase_bbox[Constants.BB_X] + phrase_bbox[Constants.BB_Y])
                closest = ExtractorHelper.closest_fieldbox_if_left_right(
                    phrase_bbox, c, close_dist, c_dist, closest)
        elif(field_pos == "left"):
            for c in fieldboxes:
                c_dist = phrase_bbox[Constants.BB_X] - \
                    (c[Constants.BB_X] + c[Constants.BB_W])
                close_dist = phrase_bbox[Constants.BB_X] - \
                    (closest[Constants.BB_X]+closest[Constants.BB_W])
                closest = ExtractorHelper.closest_fieldbox_if_left_right(
                    phrase_bbox, c, close_dist, c_dist, closest)
        elif(field_pos == "bottom"):
            for c in fieldboxes:
                c_dist = c[Constants.BB_Y] - \
                    (phrase_bbox[Constants.BB_Y] + phrase_bbox[Constants.BB_H])
                close_dist = closest[Constants.BB_Y] - \
                    (phrase_bbox[Constants.BB_Y] + phrase_bbox[Constants.BB_H])
                closest = ExtractorHelper.closest_fieldbox_if_top_bottom(
                    phrase_bbox, c, close_dist, c_dist, closest)
        elif(field_pos == "top"):
            for c in fieldboxes:
                c_dist = phrase_bbox[Constants.BB_Y] - \
                    (c[Constants.BB_Y] + c[Constants.BB_H])
                close_dist = phrase_bbox[Constants.BB_Y] - \
                    (closest[Constants.BB_Y]+closest[Constants.BB_H])
                closest = ExtractorHelper.closest_fieldbox_if_top_bottom(
                    phrase_bbox, c, close_dist, c_dist, closest)
        else:
            dist_list = []
            for f in fieldboxes:
                dist_dict = {}
                dist_dict["fieldbox"] = f
                dist_dict["x_dist"] = abs(
                    f[Constants.BB_X] - phrase_bbox[Constants.BB_X])
                dist_dict["y_dist"] = abs(
                    f[Constants.BB_Y] - phrase_bbox[Constants.BB_Y])
                dist_list.append(dist_dict)
            dist_list.sort(key=lambda x: (x["x_dist"], x["y_dist"]))
            return dist_list[0]["fieldbox"]
        return closest

    @staticmethod
    def closest_fieldbox_if_top_bottom(
            phrase_bbox, fieldbox, closest_fieldbox_dist, fieldbox_dist, closest_fieldbox):
        close_dist = closest_fieldbox_dist
        c = fieldbox
        c_dist = fieldbox_dist
        closest = closest_fieldbox
        if(close_dist < 0):
            if(phrase_bbox[Constants.BB_X] >= c[Constants.BB_X] and
                    phrase_bbox[Constants.BB_X]+phrase_bbox[Constants.BB_W] <= c[Constants.BB_X]+c[Constants.BB_W]):
                closest = c
            elif(phrase_bbox[Constants.BB_X] <= c[Constants.BB_X] <= phrase_bbox[Constants.BB_X]+phrase_bbox[Constants.BB_W]):
                closest = c
            elif(phrase_bbox[Constants.BB_X] <= c[Constants.BB_X]+c[Constants.BB_W] <= phrase_bbox[Constants.BB_X]+phrase_bbox[Constants.BB_W]):
                closest = c
        elif(close_dist > 0 and c_dist > 0 and c_dist <= close_dist):
            if(phrase_bbox[Constants.BB_X] >= c[Constants.BB_X] and
                    phrase_bbox[Constants.BB_X]+phrase_bbox[Constants.BB_W] <= c[Constants.BB_X]+c[Constants.BB_W]):
                closest = c
            elif(phrase_bbox[Constants.BB_X] <= c[Constants.BB_X] <= phrase_bbox[Constants.BB_X]+phrase_bbox[Constants.BB_W]):
                closest = c
            elif(phrase_bbox[Constants.BB_X] <= c[Constants.BB_X]+c[Constants.BB_W] <= phrase_bbox[Constants.BB_X]+phrase_bbox[Constants.BB_W]):
                closest = c
        return closest

    @staticmethod
    def closest_fieldbox_if_left_right(phrase_bbox, fieldbox, closest_fieldbox_dist, fieldbox_dist, closest_fieldbox):
        close_dist = closest_fieldbox_dist
        c = fieldbox
        c_dist = fieldbox_dist
        closest = closest_fieldbox
        if(close_dist < 0):
            if(phrase_bbox[Constants.BB_Y] >= c[Constants.BB_Y] and
                    phrase_bbox[Constants.BB_Y]+phrase_bbox[Constants.BB_H] <= c[Constants.BB_Y]+c[Constants.BB_H]):
                closest = c
            elif(phrase_bbox[Constants.BB_Y] <= c[Constants.BB_Y] <= phrase_bbox[Constants.BB_Y]+phrase_bbox[Constants.BB_H]):
                closest = c
            elif(phrase_bbox[Constants.BB_Y] <= c[Constants.BB_Y]+c[Constants.BB_W] <= phrase_bbox[Constants.BB_Y]+phrase_bbox[Constants.BB_H]):
                closest = c
        elif(close_dist > 0 and c_dist > 0 and c_dist <= close_dist):
            if(phrase_bbox[Constants.BB_Y] >= c[Constants.BB_Y] and
                    phrase_bbox[Constants.BB_Y]+phrase_bbox[Constants.BB_H] <= c[Constants.BB_Y]+c[Constants.BB_H]):
                closest = c
            elif(phrase_bbox[Constants.BB_Y] <= c[Constants.BB_Y] <= phrase_bbox[Constants.BB_Y]+phrase_bbox[Constants.BB_H]):
                closest = c
            elif(phrase_bbox[Constants.BB_Y] <= c[Constants.BB_Y]+c[Constants.BB_W] <= phrase_bbox[Constants.BB_Y]+phrase_bbox[Constants.BB_H]):
                closest = c
        return closest

    @staticmethod
    def get_box_region(
            image, img_name, debug_mode_check, temp_folderpath,
            MIN_BOX_HEIGHT, MIN_BOX_WIDTH, MAX_BOX_HEIGHT=None, MAX_BOX_WIDTH=None):
        # get regions
        img = image.copy()
        (_, img_bin) = cv2.threshold(img, 128, 255,
                                     cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        img_bin = 255-img_bin

        # Defining a kernel length
        kernel_length = img.shape[1]//200

        # A verticle kernel of (1 X kernel_length), which will detect
        # all the verticle lines from the image.
        verticle_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (1, kernel_length))
        # A horizontal kernel of (kernel_length X 1), which will help
        # to detect all the horizontal line from the image.
        hori_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (kernel_length, 1))
        # A kernel of (3 X 3) ones.
        # Morphological operation to detect verticle lines from an image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
        verticle_lines_img = cv2.dilate(
            img_temp1, verticle_kernel, iterations=3)
        # Morphological operation to detect horizontal lines from an image
        img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
        horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
        # Weighting parameters, this will decide the quantity of an image
        # to be added to make a new image.

        alpha = 0.5
        beta = 1.0 - alpha
        # This function helps to add two image with specific weight
        # parameter to get a third image as summation of two image.
        img_final_bin = cv2.addWeighted(
            verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
        img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
        (_, img_final_bin) = cv2.threshold(img_final_bin, 128,
                                           255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        if(debug_mode_check is True):
            cv2.imwrite(temp_folderpath+"//"+img_name +
                        "verticle_line.png", verticle_lines_img)
            cv2.imwrite(temp_folderpath+"//"+img_name +
                        "horizontal_line.png", horizontal_lines_img)
            cv2.imwrite(temp_folderpath+"//"+img_name +
                        "img_final_bin.png", img_final_bin)
        # Find contours for image, which will detect all the boxes
        contours, _ = cv2.findContours(
            img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        idx = 0
        bboxes_region = []
        for c in contours:
            # Returns the location and width,height for every contour
            x, y, w, h = cv2.boundingRect(c)
            if(MAX_BOX_HEIGHT is None and MAX_BOX_WIDTH is None):
                if (w >= MIN_BOX_WIDTH and h >= MIN_BOX_HEIGHT):
                    idx += 1
                    bboxes_region.append([x, y, w, h])
                    if(debug_mode_check is True):
                        new_img = img[y:y+h, x:x+w]
                        cv2.imwrite(temp_folderpath+"//"+img_name+str(x) +
                                    '_'+str(y) + '.png', new_img)
            else:
                if (MAX_BOX_WIDTH >= w >= MIN_BOX_WIDTH and MAX_BOX_HEIGHT >= h >= MIN_BOX_HEIGHT):
                    idx += 1
                    bboxes_region.append([x, y, w, h])
                    if(debug_mode_check is True):
                        new_img = img[y:y+h, x:x+w]
                        cv2.imwrite(temp_folderpath+"//"+img_name+str(x) +
                                    '_'+str(y) + '.png', new_img)
        return bboxes_region

    @staticmethod
    def get_updated_within_box(within_bbox, scaling_factor):
        if(len(within_bbox) > 0):
            for i in [0, 2]:
                within_bbox[i] = round(
                    within_bbox[i] * scaling_factor.get('hor', 1))
            for i in [1, 3]:
                within_bbox[i] = round(
                    within_bbox[i] * scaling_factor.get('ver', 1))
        return within_bbox

    @staticmethod
    def get_updated_text_bbox(text_bboxes, scaling_factor):
        if(len(text_bboxes) > 0):
            for bbox in text_bboxes:
                for i in [0, 2]:
                    bbox['bbox'][i] = round(
                        bbox['bbox'][i] * scaling_factor.get('hor', 1))
                for i in [1, 3]:
                    bbox['bbox'][i] = round(
                        bbox['bbox'][i] * scaling_factor.get('ver', 1))
        return text_bboxes

    @staticmethod
    def get_invalid_keys(truth_dict, test_dict) -> list:
        """Compare two dictionary objects and return invalid keys by using one of them as reference

        Args:
            truth_dict (dict): The object containing all valid keys
            test_dict (dict): The object to evaluate for presence of invalid keys

        Returns:
            list: The list of invalid keys
        """

        def __get_all_keys_recursively(parent_key, dict_obj):
            all_keys = []
            for k, val in dict_obj.items():
                key = k if parent_key is None or len(
                    parent_key) == 0 else f"{parent_key}->{k}"
                if not key in all_keys:
                    all_keys.append(key)
                if isinstance(val, dict):
                    all_keys += __get_all_keys_recursively(key, val)
            return all_keys

        truth_keys = __get_all_keys_recursively(None, truth_dict)
        test_keys = __get_all_keys_recursively(None, test_dict)
        return list(set(test_keys)-set(truth_keys))

    @staticmethod
    def get_updated_config_dict(from_dict, default_dict):
        config_dict_temp = copy.deepcopy(default_dict)
        for key in from_dict:
            if isinstance(from_dict[key], dict):
                if config_dict_temp.get(key) is None:
                    config_dict_temp[key] = from_dict[key]
                else:
                    config_dict_temp[key] = ExtractorHelper.get_updated_config_dict(
                        from_dict[key], config_dict_temp[key])
            else:
                if config_dict_temp.get(key) is None:
                    config_dict_temp[key] = from_dict[key]
        return config_dict_temp

    @staticmethod
    def save_image(image, image_save_path):
        CommonUtils.archive_file(image_save_path)
        cv2.imwrite(image_save_path, image)

    @staticmethod
    def convert_grayscale_to_rgb(img_obj):
        stacked_img = np.stack((img_obj,)*3, axis=-1)
        return stacked_img

    @staticmethod
    def draw_bboxes_on_image(image, bboxes_list, color=Constants.COLOR_BLUE, thickness=4, write_coordinates=False):
        if len(image.shape) == 2:
            image = ExtractorHelper.convert_grayscale_to_rgb(image)

        # Draw boxes on image
        for rt_bbox in bboxes_list:
            (l, t, w, h) = tuple([(i) for i in rt_bbox])
            image = cv2.rectangle(
                image, (l, t), (l + w, t + h), color=color, thickness=thickness)
            if write_coordinates:
                cv2.putText(image, f"[{l},{t},{w},{h}]",
                            (l-thickness, t-thickness), cv2.FONT_HERSHEY_PLAIN, 1, color)
        return image

    @staticmethod
    def order_the_text(multiline_sorting_left_to_right, bboxes_text):
        if not multiline_sorting_left_to_right:
            stk = []
            orderedList = []
            # sort by Y-axis (vertically)
            bboxes_text = sorted(bboxes_text, key=lambda i: i['bbox'][1])
            for idx in range(len(bboxes_text)):
                if(idx == 0):
                    mainY1 = bboxes_text[idx]['bbox'][1]
                    mainY2 = bboxes_text[idx]['bbox'][1] + \
                        bboxes_text[idx]['bbox'][3]
                    main_Ycenter = mainY2 - (bboxes_text[idx]['bbox'][3] / 2)
                    stk.append(bboxes_text[idx])
                    if (len(bboxes_text) == 1):
                        orderedList = stk
                    continue
                y1 = bboxes_text[idx]['bbox'][1]
                y2 = bboxes_text[idx]['bbox'][1] + bboxes_text[idx]['bbox'][3]
                Ycenter = y2 - (bboxes_text[idx]['bbox'][3] / 2)
                if y1 > mainY1 and y1 < main_Ycenter:
                    stk.append(bboxes_text[idx])
                else:
                    # sort based on X axis (left to right)
                    stk = sorted(stk, key=lambda i: i['bbox'][0], reverse=True)
                    while(stk != []):
                        orderedList.append(stk.pop())

                    mainY1, mainY2, main_Ycenter = y1, y2, Ycenter
                    stk.append(bboxes_text[idx])

                if (idx == (len(bboxes_text)-1)):
                    # sort based on X axis (left to right)
                    stk = sorted(stk, key=lambda i: i['bbox'][0], reverse=True)
                    while(stk != []):
                        orderedList.append(stk.pop())
        else:
            orderedList = bboxes_text
            orderedList.sort(key=lambda x: (x.get("bbox")[Constants.BB_X]))
        return orderedList
