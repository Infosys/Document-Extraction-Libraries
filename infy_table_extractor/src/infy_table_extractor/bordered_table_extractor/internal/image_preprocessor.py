# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import cv2
from infy_table_extractor.bordered_table_extractor.internal.constants import *


class ImagePreprocessor:

    @staticmethod
    def pre_process_mask(img, cvt_hsv):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        count_dict = ImagePreprocessor.count_diff_color_pixel(
            img, True)
        msk_ranges = [(LIGHT_BLUE, DARK_BLUE), (LIGHT_ORANGE,
                                                DARK_ORANGE), (LIGHT_YELLOW, DARK_YELLOW)]
        org_img = img.copy()
        for (lw_rng, hgh_rng) in msk_ranges:
            img = ImagePreprocessor.msk_pixels(img, lw_rng, hgh_rng, cvt_hsv)
        # show_img("Final Image", img)
        # img = ImagePreprocessor.pre_process_img(img, False)
        return img

    @staticmethod
    def msk_pixels(img, lw_rng, hgh_rng, cvt_hsv):
        # show_img("original_image", img)
        # Image converted to HSV for better contrast
        if(cvt_hsv is True):
            hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # show_img("HSV Image ", hsv_img)
        # Color Ranges used for identifying the pixels in certain range
        mask = cv2.inRange(img, lw_rng, hgh_rng)
        # Replacing identified pixels with white values
        img[mask > 0] = (255, 255, 255)  # BGR value
        # show_img("Final....And", img)
        return img

    @staticmethod
    def pre_process_img(img, cvt_adap):
        if(len(img.shape) == 3):
            img = cv2.cvtColor(
                img, cv2.COLOR_BGR2GRAY)
        if(cvt_adap is False):
            img = cv2.adaptiveThreshold(
                img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 25)
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (2, 1))
        border = cv2.copyMakeBorder(
            img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[255, 255])
        resizing = cv2.resize(
            border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        dilation = cv2.dilate(resizing, kernel, iterations=2)
        erosion = cv2.erode(dilation, kernel, iterations=2)
        return erosion

    @staticmethod
    def count_diff_color_pixel(img, reduced_color_space):
        from scipy.spatial import cKDTree as KDTree
        from matplotlib import colors
        import numpy as np

        # borrow a list of named colors from matplotlib
        if reduced_color_space:
            use_colors = {k: colors.cnames[k] for k in [
                'red', 'green', 'blue', 'black', 'yellow', 'white', 'orange']}
        else:
            use_colors = colors.cnames

        # translate hexstring to RGB tuple
        named_colors = {k: tuple(map(int, (v[1:3], v[3:5], v[5:7]), 3*(16,)))
                        for k, v in use_colors.items()}
        ncol = len(named_colors)

        # make an array containing the RGB values
        color_tuples = list(named_colors.values())
        # color_tuples.append(no_match)
        color_tuples = np.array(color_tuples)

        color_names = list(named_colors)
        # color_names.append('no match')

        # build tree
        tree = KDTree(color_tuples[:-1])
        # tolerance for color match `inf` means use best match no matter how
        # bad it may be
        tolerance = np.inf
        # find closest color in tree for each pixel in picture
        dist, idx = tree.query(img, distance_upper_bound=tolerance)
        # count and reattach names
        counts = dict(zip(color_names, np.bincount(idx.ravel(), None, ncol+1)))
        counts = {key: val for key, val in counts.items() if val != 0}
        return counts
