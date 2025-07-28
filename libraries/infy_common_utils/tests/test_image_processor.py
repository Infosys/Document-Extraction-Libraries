# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import shutil
import cv2
import ctypes
import tkinter as tk
from PIL import Image, ImageDraw, ImageColor, ImageTk
from infy_common_utils.image_processor import ImageProcessor

IMAGE_FILE = os.path.abspath("./data/1.jpg")
IMAGE_FILE_LIST = [IMAGE_FILE]
DEBUG_MODE_ENABLED = False

TEMP_DIR_PATH = './data/temp'
if not os.path.exists(TEMP_DIR_PATH):
    os.makedirs(TEMP_DIR_PATH)


class ImageVisualizer:
    """Simple image visualizer to avoid the practice of using 3rd party packages such as
        matplotlib or opencv only for visualizations."""
    @classmethod
    def _get_screen_size(cls):
        user32 = ctypes.windll.user32
        screen_size_list = user32.GetSystemMetrics(
            0), user32.GetSystemMetrics(1)
        return screen_size_list  # E.g. (1920, 1080)

    @classmethod
    def show_image(cls, image_path):
        screen_sizes = cls._get_screen_size()
        max_visible_screen_width = screen_sizes[0] - 200
        max_visible_screen_height = screen_sizes[1] - 200

        _img = Image.open(image_path)
        _width, _height = _img.size
        print(_width, _height)
        scale_down_factor = 1
        if _width > max_visible_screen_width:
            scale_down_factor = _width/max_visible_screen_width

        width, height = int(
            _width/scale_down_factor), int(_height/scale_down_factor)
        _img = _img.resize((width, height))

        root = tk.Tk()
        frame = tk.Frame(root, width=10, height=10)
        frame.pack(expand=True, fill=tk.BOTH)  # .grid(row=0,column=0)
        canvas = tk.Canvas(frame, bg='#FFFFFF', width=0,
                           height=0, scrollregion=(0, 0, width, height))

        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        hbar.config(command=canvas.xview)

        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        vbar.config(command=canvas.yview)

        canvas.config(width=width, height=min(
            max_visible_screen_height, height))
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        img = ImageTk.PhotoImage(_img)

        canvas.create_image(0, 0, anchor=tk.NW, image=img)

        root.mainloop()


def test_draw_bbox_1():
    """Positive test to draw_bbox api"""
    config_param_dict_list = [{"bbox": [3636, 625, 4071, 888]}, {"bbox": [1637, 646, 2355, 1069], "color": (
        0, 0, 255)}, {"bbox": [4275, 964, 4809, 1227], "color": (0, 0, 255)}]
    result = ImageProcessor.draw_bbox(
        IMAGE_FILE, None, config_param_dict_list)
    if DEBUG_MODE_ENABLED:
        temp_file_path = os.path.abspath(
            f"{TEMP_DIR_PATH}/debug_image.jpg")
        cv2.imread(result).save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)
    assert os.path.exists(result)


def test_draw_bbox_2():
    """Positive test to draw_bbox api without optional value"""
    config_param_dict_list = [{"bbox": [3636, 625, 4071, 888]}]
    result = ImageProcessor.draw_bbox(
        IMAGE_FILE, None, config_param_dict_list)
    if DEBUG_MODE_ENABLED:
        temp_file_path = os.path.abspath(
            f"{TEMP_DIR_PATH}/debug_image.jpg")
        cv2.imread(result).save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)
    assert os.path.exists(result)


def test_draw_bbox_and_get_horizontally_cropped_image():
    """Test method"""
    config_param_dict_list = [{"bbox": [3636, 625, 4071, 888]}, {"bbox": [1637, 646, 2355, 1069], "color": (
        0, 0, 255)}, {"bbox": [4275, 964, 4809, 1227], "color": (0, 0, 255)}]
    result = ImageProcessor.draw_bbox(
        IMAGE_FILE, None, config_param_dict_list,
        margin_horizontal=50)
    if DEBUG_MODE_ENABLED:
        temp_file_path = os.path.abspath(
            f"{TEMP_DIR_PATH}/debug_image.jpg")
        cv2.imread(result).save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)
    assert os.path.exists(result)


def test_draw_bbox_and_get_vertically_cropped_image():
    """Test method"""
    config_param_dict_list = [{"bbox": [3636, 625, 4071, 888]}, {"bbox": [1637, 646, 2355, 1069], "color": (
        0, 0, 255)}, {"bbox": [4275, 964, 4809, 1227], "color": (0, 0, 255)}]
    result = ImageProcessor.draw_bbox(
        IMAGE_FILE, None, config_param_dict_list,
        margin_vertical=50)
    if DEBUG_MODE_ENABLED:
        temp_file_path = os.path.abspath(
            f"{TEMP_DIR_PATH}/debug_image.jpg")
        cv2.imread(result).save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)
    assert os.path.exists(result)


def test_draw_bbox_and_get_hor_and_ver_cropped_image():
    """Test method"""
    config_param_dict_list = [{"bbox": [3636, 625, 4071, 888]}, {"bbox": [1637, 646, 2355, 1069], "color": (
        0, 0, 255)}, {"bbox": [4275, 964, 4809, 1227], "color": (0, 0, 255)}]
    result = ImageProcessor.draw_bbox(
        IMAGE_FILE, None, config_param_dict_list,
        margin_horizontal=50,
        margin_vertical=50)
    if DEBUG_MODE_ENABLED:
        temp_file_path = os.path.abspath(
            f"{TEMP_DIR_PATH}/debug_image.jpg")
        cv2.imread(result).save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)
    assert os.path.exists(result)


def test_draw_bbox_without_passing_any_bbox_gives_error():
    """Test method"""
    try:
        config_param_dict_list = []
        ImageProcessor.draw_bbox(
            IMAGE_FILE, None, config_param_dict_list)
    except Exception as ex:
        assert str(ex) == "config_param_dict_list needs to be populated"


def test_plot_1():
    """Test method"""
    result_json = {
        'regions': [
            {'anchorTextBBox': [{'text': ['Women employees'],
                                 'bbox': [3676, 625, 4022, 651],
                                 'scalingFactor': 1.0}],
             'regionBBox': [{'bbox': [3676, 625, 4022, 651],
                             'page': 1,
                             'scalingFactor': 1.0}]}],
        'error': None}
    for value in result_json['regions']:
        config_param_dict_list = []
        for anc_bbox in value['anchorTextBBox']:
            config_param_dict_list.append(
                {'bbox': anc_bbox['bbox'], 'color': (0, 0, 255)})
        for reg_bbox in value['regionBBox']:
            bbox_list = config_param_dict_list+[{'bbox': reg_bbox['bbox']}]
            image_name = os.path.abspath(IMAGE_FILE_LIST[reg_bbox["page"]-1])
            print(f"image {image_name}")
            result = ImageProcessor.draw_bbox(
                image_name, None, bbox_list)
            print(f"result {result}")
            if DEBUG_MODE_ENABLED:
                temp_file_path = os.path.abspath(
                    f"{TEMP_DIR_PATH}/debug_image.jpg")
                cv2.imread(result).save(temp_file_path)
                ImageVisualizer.show_image(temp_file_path)
    assert os.path.exists(result)


def test_deskew_not_corrected():
    """Deskew api test method"""
    image_file = IMAGE_FILE
    output_file_path = "data/temp/1.jpg_original.jpg"
    # revert_original_img(backup_file_path, image_file)
    result = ImageProcessor.deskew(
        image_file, output_file_path=output_file_path)
    print(result)
    assert result == {'skew_corrected': False,
                      'method': [
                          {'name': 'CV2_HOUGH_LP', 'selected': False, 'detected_skew_angle': 0.0}],
                      'threshold_angle': 0.1,
                      'output_file_path': None,
                      'backup_file_path': None,
                      'error': None}


def revert_original_img(bkup_image, original_image):
    """Util method to revert backup image to original image"""
    if os.path.exists(bkup_image):
        shutil.copy(bkup_image, original_image)
