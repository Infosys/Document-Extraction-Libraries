# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
from os import path
import cv2
from PIL import Image


class ImageParserUtil:
    """Parser class to do image processing"""
    @classmethod
    def get_grayscale_and_noborder_img(cls, image_file_path, is_debug_mode=False, debug_path=None):
        """Return gray scale image by removing all lines"""
        no_border_img_bin_out, debug_location = None, None
        if is_debug_mode:
            file_name = path.split(image_file_path)[1]
            _, ext = path.splitext(file_name)
            debug_path = debug_path+"/"+file_name if debug_path else image_file_path
            debug_location = cls.__make_dir(debug_path)
        file_name = ""
        try:
            im = cv2.imread(image_file_path)
            gray_img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            if is_debug_mode:
                Image.fromarray(gray_img).save(
                    f"{debug_location}/{file_name}_grayscale{ext}")

            # **********start: Remove vertical and horizontal line from images
            _, binary = cv2.threshold(gray_img, 200, 255, 0)
            inv = 255 - binary
            horizontal_img = inv
            vertical_img = inv
            if is_debug_mode:
                Image.fromarray(inv).save(
                    f"{debug_location}/{file_name}_grayscale_binary_inv{ext}")

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 1))
            horizontal_img = cv2.erode(horizontal_img, kernel, iterations=1)
            horizontal_img = cv2.dilate(horizontal_img, kernel, iterations=1)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 100))
            vertical_img = cv2.erode(vertical_img, kernel, iterations=1)
            vertical_img = cv2.dilate(vertical_img, kernel, iterations=1)

            mask_img = horizontal_img + vertical_img
            if is_debug_mode:
                Image.fromarray(mask_img).save(
                    f"{debug_location}/{file_name}_noborders_mask{ext}")
            no_border_img_bin = cv2.bitwise_or(binary, mask_img)
            no_border_img_bin_out = Image.fromarray(no_border_img_bin)
        except Exception as e:
            print(e)

        return no_border_img_bin_out, debug_location

    @classmethod
    def get_line_position(cls, image_file_path, is_debug_mode=False, debug_path=None):
        """Returns horizontal and vertical line from image"""
        hor_line_position_list, ver_line_position_list = [], []
        debug_location = None
        if is_debug_mode:
            file_name = path.split(image_file_path)[1]
            _, ext = path.splitext(file_name)
            debug_location = debug_path if debug_path else cls.__make_dir(
                image_file_path)
        file_name = ""
        try:
            im = cv2.imread(image_file_path)
            height, width = im.shape[:2]
            no_border_img_bin = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            if is_debug_mode:
                Image.fromarray(no_border_img_bin).save(
                    f"{debug_location}/{file_name}_grayscale{ext}")
            # plt.imshow(no_border_img_bin, cmap='gray')
            # plt.show()
            # **********End: Remove vertical and horizontal line from images

            # ***********Start: Horizontal line
            # binary inverse important to horrizontal line
            hor_bin_inv_thresh = cv2.threshold(
                no_border_img_bin, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            if is_debug_mode:
                Image.fromarray(hor_bin_inv_thresh).save(
                    f"{debug_location}/{file_name}_hor_binary_inv{ext}")
            # plt.imshow(bin_inv_thresh, cmap='gray')
            # plt.show()
            hor_line_position_list = cls.__get_line_pixels(
                hor_bin_inv_thresh, is_horizontal_line=True)
            # ***********End: Horizontal line

            # ***********Start: Vertical line
            ver_line_position_list = cls.__get_line_pixels(
                no_border_img_bin, bg_color=(255))
            # ****************End: Vertical Line

            # add last line
            hor_line_position_list.append(height)
            ver_line_position_list.append(width)
        except Exception as e:
            pass
        return {'rows': hor_line_position_list, 'cols': ver_line_position_list}, debug_location

    @classmethod
    def draw_line_position(cls, image_file_path, line_pos_list, debug_location, from_model=""):
        """Dram horizontal and vertical line in image"""
        bin_line_im_pixel = None
        try:
            im = cv2.imread(image_file_path)
            height, width = im.shape[:2]
            no_border_img_bin = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            file_name = path.split(image_file_path)[1]
            _, ext = path.splitext(file_name)
            # *********** Draw horizontal and vertical line on binary thresh image
            bin_thresh = cv2.threshold(
                no_border_img_bin, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            bin_line_im_pixel = Image.fromarray(bin_thresh)
            if debug_location:
                with open(f"{debug_location}/{from_model}_linepos.json", "w") as f:
                    f.write(json.dumps(line_pos_list))
            cls.__convert_img_pixel(
                bin_line_im_pixel, line_pos_list['rows'], width=width)
            cls.__convert_img_pixel(
                bin_line_im_pixel, line_pos_list['cols'], height=height)
            if debug_location:
                bin_line_im_pixel.save(
                    f"{debug_location}/{from_model}_line{ext}")
        except Exception as e:
            print(e)
        finally:
            if bin_line_im_pixel:
                # bin_line_im_pixel.show()
                bin_line_im_pixel.close()

    @classmethod
    def __make_dir(cls, img_name):
        """make dir"""
        folderpath = None
        try:
            # timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            # folderpath = path.abspath(img_name)+'_'+timestr
            folderpath = path.abspath(img_name)+"_line_detection_files"
            os.mkdir(folderpath)
        except Exception as e:
            pass
        return folderpath

    @classmethod
    def __convert_img_pixel(cls, img_pixels, to_fill_list, width=None, height=None):
        """Change image pixel color"""
        for mid_pixel in to_fill_list:
            try:
                if width is not None:
                    for w in range(0, width):
                        img_pixels.putpixel(
                            (w, mid_pixel['bbox'][1] if isinstance(mid_pixel, dict) else mid_pixel), 0)
                elif height is not None:
                    for h in range(0, height):
                        img_pixels.putpixel((mid_pixel['bbox'][0] if isinstance(
                            mid_pixel, dict) else mid_pixel, h), 0)
            except:
                pass

    @ classmethod
    def __get_line_pixels(cls, im_pixel_array, is_horizontal_line=False, bg_color=(0)):
        """Return pixel of line from horizontal and vertical end-to-end """
        temp_im = Image.fromarray(im_pixel_array)
        width, height = temp_im.size
        pixel_array = temp_im.load()
        axis_1, axis_2 = width, height
        if is_horizontal_line:
            axis_1, axis_2 = axis_2, axis_1
        fill_width_list = []
        try:
            for i in range(0, axis_1):
                should_draw_line = True
                for j in range(0, axis_2):
                    if is_horizontal_line:
                        g = pixel_array[j, i]
                    else:
                        g = pixel_array[i, j]

                    if (g) != bg_color:
                        should_draw_line = False
                        break
                if should_draw_line:
                    fill_width_list.append(i)
        except Exception as e:
            print(e)
        return [] if not fill_width_list else cls.__get_pixels_to_fill(cls.group_sequence(fill_width_list))

    @ classmethod
    def __get_pixels_to_fill(cls, pixel_list):
        """Mid point of pixels"""
        pixels = []
        for pixel in pixel_list:
            mid_pixel = (pixel[1]+pixel[-1])//2
            pixels.append(mid_pixel)
        return pixels

    @ classmethod
    def group_sequence(cls, x):
        """Group the sequence"""
        it = iter(x)
        prev, res = next(it), []
        while prev is not None:
            start = next(it, None)

            if prev + 1 == start:
                res.append(prev)
            elif res:
                yield list(res + [prev])
                res = []
            prev = start
