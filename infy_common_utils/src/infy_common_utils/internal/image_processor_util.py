# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import concurrent.futures
import math
import cv2
import numpy as np

# CV2_HOUGH_LP default technique
_SKEW_DETECT_TECH_LIST: list = ['CV2_HOUGH_LP']
# _SKEW_DETECT_TECH_LIST: list = ['CV2_HOUGH_LP', 'CV2_MAR']


class ImageProcessorUtil:
    """Util class to Image Processor APIs"""

    @classmethod
    def deskew_image(cls, image_file_path, response_dict) -> dict:
        """Util method to deskew the image"""
        image = cv2.imread(image_file_path)
        gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detected_skew_dict = {}
        detected_skew_dict_list = []
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(5, len(_SKEW_DETECT_TECH_LIST)),
                thread_name_prefix="thread_detect_skew") as executor:
            thread_pool_dict = {
                executor.submit(
                    cls._determine_skew,
                    gray_scale.copy(),
                    technique_name
                ): technique_name for technique_name in _SKEW_DETECT_TECH_LIST
            }
            for future in concurrent.futures.as_completed(thread_pool_dict):
                result = future.result()
                detected_skew_dict[result['name']] = result
                detected_skew_dict_list.append(result)

        # This `for loop` used to control the priority order of skew technique execution
        for method_name in _SKEW_DETECT_TECH_LIST:
            try:
                rot_angle = detected_skew_dict[method_name]['detected_skew_angle']
                # TODO: look for perfect threshold and enable below condition
                # if abs(rot_angle) >= response_dict['threshold_angle']:
                if abs(rot_angle) != 0:
                    response_dict['skew_corrected'] = True
                    detected_skew_dict[method_name]['selected'] = True
                    response_dict['deskewed_image_array'] = cls._rotate_img(
                        image.copy(), rot_angle)
            except Exception as e:
                detected_skew_dict[method_name]['error'] = e.args[0]
            if detected_skew_dict[method_name]['selected']:
                break
        response_dict['method'] = list(detected_skew_dict.values())

    @ classmethod
    def _determine_skew(cls, gray_scale, technique_name):
        result = {'name': technique_name,
                  'selected': False,
                  'detected_skew_angle': 0}
        if technique_name == 'CV2_MAR':
            result['detected_skew_angle'] = round(
                cls._determine_skew_MAR(gray_scale), 5)
        elif technique_name == 'CV2_HOUGH_LP':
            result['detected_skew_angle'] = round(
                cls._determine_skew_houghlinep(gray_scale), 5)
        return result

    @ classmethod
    def _determine_skew_MAR(cls, gray_scale):
        gray = cv2.bitwise_not(gray_scale)
        # threshold the image, setting all foreground pixels to
        # 255 and all background pixels to 0
        thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # grab the (x, y) coordinates of all pixel values that
        # are greater than zero, then use these coordinates to
        # compute a rotated bounding box that contains all
        # coordinates
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        # the `cv2.minAreaRect` function returns values in the
        # range [-90, 0); as the rectangle rotates clockwise the
        # returned angle trends to 0 -- in this special case we
        # need to add 90 degrees to the angle
        rot_angle = 90 + angle if angle < -45 else angle
        # rot_angle = -1*rot_angle if rot_angle != 0 else rot_angle
        return rot_angle if abs(int(rot_angle)) == 0 else -1*rot_angle

    @classmethod
    def _determine_skew_houghlinep(cls, gray_scale):
        canny = cv2.Canny(gray_scale, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(canny, 1, np.pi/180, 80,
                                minLineLength=100, maxLineGap=10)
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angles.append(np.arctan2(y2 - y1, x2 - x1))

        # If the majority of our lines are vertical, this is probably a landscape image
        landscape = np.sum(
            [abs(angle) > np.pi / 4 for angle in angles]) > len(angles) / 2
        max_skew = 10
        if landscape:
            angles = [
                angle
                for angle in angles
                if np.deg2rad(90 - max_skew) < abs(angle) < np.deg2rad(90 + max_skew)
            ]
        else:
            angles = [angle for angle in angles if abs(
                angle) < np.deg2rad(max_skew)]

        if len(angles) < 5:
            # Insufficient data to deskew
            return 0
        angle_deg = np.rad2deg(np.median(angles))

        # If this is landscape image, rotate the entire canvas appropriately
        if landscape:
            if angle_deg < 0:
                angle_deg += 90
            elif angle_deg > 0:
                angle_deg -= 90

        return angle_deg

    @classmethod
    def _rotate_img(cls, image, angle, background=(255, 255, 255)) -> np.ndarray:
        old_width, old_height = image.shape[:2]
        angle_radian = math.radians(angle)
        width = abs(np.sin(angle_radian) * old_height) + \
            abs(np.cos(angle_radian) * old_width)
        height = abs(np.sin(angle_radian) * old_width) + \
            abs(np.cos(angle_radian) * old_height)

        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        rot_mat[1, 2] += (width - old_width) / 2
        rot_mat[0, 2] += (height - old_height) / 2
        return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)

    @classmethod
    def calculate_container_bbox(cls, bbox_array_list: list) -> list:
        """Calculates the largest bbox that can contain all provided bbox

        Args:
            bbox_array_list (list): The list of bboxes in the format [[x,y,w,h]]

        Returns:
            [list]: The container bbox
        """
        _bbox_array_list = [[x1, y1, x1+w, y1+h]
                            for x1, y1, w, h in bbox_array_list]
        x_min = min([min(x1, x2) for x1, y1, x2, y2 in _bbox_array_list])
        y_min = min([min(y1, y2) for x1, y1, x2, y2 in _bbox_array_list])
        x_max = max([max(x1, x2) for x1, y1, x2, y2 in _bbox_array_list])
        y_max = max([max(y1, y2) for x1, y1, x2, y2 in _bbox_array_list])
        return [x_min, y_min, x_max-x_min, y_max - y_min]
