# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
import tempfile
from pathlib import Path

import cv2
from PIL import Image

from infy_common_utils.internal.file_util import FileUtil
from infy_common_utils.internal.image_processor_util import ImageProcessorUtil

_DESKEW_RESPONSE_DICT: dict = {
    'skew_corrected': False,
    'method': [{'name': '', 'detected_skew_angle': None, 'selected': False, 'error': None}],
    'threshold_angle': 0,
    'output_file_path': None,
    'backup_file_path': None,
    'error': None
}

CONFIG_PARAMS_DICT = {
    "bbox": [],
    "color": (255, 0, 0),
    "thickness": 2
}


class ImageProcessor:
    """Class to convert document format.
    """

    @classmethod
    def draw_bbox(cls, image_file, output_dir=None,
                  config_param_dict_list=[CONFIG_PARAMS_DICT],
                  margin_vertical=None,
                  margin_horizontal=None
                  ):
        """API to draw a rectangle outline on given image and returns focused image.

        Args:
            image_file (str): full path of image. e.g., c:/1.jpg
            output_dir (str, optional): Output directory folder path to save file. Defaults to None.
            config_param_dict_list (list, optional): mandatory config bbox[x,y,w,h] dict with optional values.
                Defaults to [{"bbox": [], "color":(255, 0, 0), "thickness":2}].
            margin_vertical (int, optional): The vertical margin in pixels to add when image is cropped. 
                Defaults to None meaning image is not cropped vertically.
            margin_horizontal (int, optional): The horizontal margin in pixels to add when image is cropped. 
                Defaults to None meaning image is not cropped horizontally.

        Returns:
            (str): The path of image on which rectangles have been drawn.
        """
        if not config_param_dict_list or len(config_param_dict_list) == 0:
            raise ValueError('config_param_dict_list needs to be populated')
        img_copy = cv2.imread(image_file)
        height, width, _ = img_copy.shape
        sum_bbox = []
        for config_param_dict in config_param_dict_list:
            bbox = config_param_dict.get("bbox", [])
            if not bbox:
                continue
            l, t, w, h = bbox
            img_copy = cv2.rectangle(
                img_copy, (l, t), (l + w, t + h),
                color=config_param_dict.get("color", (255, 0, 0)),
                thickness=int(config_param_dict.get("thickness", 2))
            )
            sum_bbox = [
                x + y for (x, y) in zip(sum_bbox, bbox)] if list(zip(sum_bbox, bbox)) else bbox

        all_bboxes = [x['bbox'] for x in config_param_dict_list]
        container_bbox = ImageProcessorUtil.calculate_container_bbox(
            all_bboxes)

        if margin_vertical:
            t = max(0, container_bbox[1]-margin_vertical)
            h = min(container_bbox[3]+2*margin_vertical, height)
        else:
            t = 0
            h = height

        if margin_horizontal:
            l = max(0, container_bbox[0]-margin_horizontal)
            w = min(container_bbox[2]+2*margin_horizontal, width)
        else:
            l = 0
            w = width

        img_path_obj = Path(image_file)
        output_dir = output_dir if output_dir else tempfile.mkdtemp()
        new_img_file_name = f"{img_path_obj.name}_{'_'.join((str(x) for x in sum_bbox))}{img_path_obj.suffix}"
        new_img = str(Path(output_dir).joinpath(new_img_file_name))
        cropped_img = img_copy[t:t+h, l:l+w]
        cv2.imwrite(new_img, cropped_img)
        return new_img

    @classmethod
    def deskew(cls, image_file_path: str,
               output_file_path: str = None,
               backup_file_path: str = None,
               threshold_angle: float = 0.1) -> _DESKEW_RESPONSE_DICT:
        """API to Correct the image skew.

        Args:
            image_file_path (str): Image file full path to do skew correction.
            output_file_path (str, optional): File path to save Deskewed image. Defaults to None.
            backup_file_path (str, optional):  File path to original file backup. Defaults to None.
            threshold_angle (float, optional): Threshold for deskew. Defaults to 0.1.

        Raises:
            AttributeError: Incase of invalid output_file_path/backup_file_path.

        Returns:
            _DESKEW_RESPONSE_DICT: Deskewed response structure.
        """

        response_dict = copy.deepcopy(_DESKEW_RESPONSE_DICT)
        try:
            if output_file_path and Path(output_file_path).is_dir():
                raise AttributeError(
                    f"Full File Path expected not a directory {output_file_path}. e.x, C:\\Temp\\abc.jpg")
            if backup_file_path and Path(backup_file_path).is_dir():
                raise AttributeError(
                    f"Full File Path expected not a directory {backup_file_path}. e.x, C:\\Temp\\abc.jpg")
            response_dict['threshold_angle'] = threshold_angle
            ImageProcessorUtil.deskew_image(
                image_file_path,
                response_dict
            )
            if response_dict['skew_corrected']:
                if backup_file_path:
                    response_dict['backup_file_path'] = backup_file_path
                    FileUtil.copy(image_file_path,
                                  response_dict['backup_file_path'])
                response_dict['output_file_path'] = output_file_path if output_file_path else image_file_path
                # cv2 image array converted to pillow image array to prevent quality and dpi loss.
                pli_im_tmp = Image.open(image_file_path)
                img_dpi = pli_im_tmp.info.get('dpi', None)
                rgb_img_array = cv2.cvtColor(
                    response_dict['deskewed_image_array'],
                    cv2.COLOR_BGR2RGBA if pli_im_tmp.mode == 'RGBA' else cv2.COLOR_BGR2RGB)
                pli_im = Image.fromarray(rgb_img_array)
                pli_im.info = pli_im_tmp.info
                if img_dpi is not None:
                    pli_im.save(
                        response_dict['output_file_path'], quality=100,
                        dpi=img_dpi
                    )
                else:
                    pli_im.save(response_dict['output_file_path'], quality=100)
            response_dict.pop('deskewed_image_array', None)
            return response_dict
        except Exception as e:
            response_dict.pop('deskewed_image_array', None)
            response_dict['error'] = str(e)
            return response_dict
