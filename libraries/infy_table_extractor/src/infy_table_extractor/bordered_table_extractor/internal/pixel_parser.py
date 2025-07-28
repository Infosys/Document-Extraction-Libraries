# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from numpy.lib.function_base import copy
from infy_table_extractor.bordered_table_extractor.internal.constants import *
import cv2
from sklearn.cluster import KMeans
import copy


class PixelParser:

    @staticmethod
    def create_colors_hash_table(rgb_matrix):
        # Height
        axis_1 = len(rgb_matrix)
        # Width
        axis_2 = len(rgb_matrix[0])
        color_hash = {}
        row_pix_info = {}
        try:
            for i in range(axis_1):
                row_i_info = []
                count, start = 1, 0
                for j in range(axis_2):
                    pix = rgb_matrix[i][j].tolist()
                    rgb_matrix[i][j] = [int(pix[0]), int(pix[1]), int(pix[2])]
                    hash_code = str(int(pix[0])).zfill(3) + \
                        str(int(pix[1])).zfill(3) + str(int(pix[2])).zfill(3)
                    if(hash_code not in color_hash):
                        color_hash[hash_code] = 1
                    else:
                        color_hash[hash_code] += 1
                    if(j != 0 and prev_hashcode == hash_code):
                        count += 1
                    elif(j != 0 and prev_hashcode != hash_code):
                        row_i_info.append(
                            [str(start)+'_'+str(count), prev_hashcode])
                        start += count
                        count = 1
                    if(j+1 == axis_2):
                        row_i_info.append(
                            [str(start)+'_'+str(count), hash_code])
                    prev_hashcode = hash_code
                row_pix_info[str(i)] = row_i_info
        except Exception as e:
            pass

        return rgb_matrix, color_hash, row_pix_info

    @staticmethod
    def identify_annotation(clustered_img, img_row_info, color_hash):
        max_px = max(color_hash, key=color_hash.get)
        inner_height, conti_heights_list, prev_no_of_color, a_height, anno_count = 0, [], 0, 0, 0
        only_anno_end = False
        for row, info in img_row_info.items():
            if(len(info) > 1):
                no_of_color, used_code = 1, [info[0][1]]
                for i in range(len(info)):
                    if(info[i][1] not in used_code):
                        no_of_color += 1
                        used_code.append(info[i][1])
                if(len(info) < 8):
                    if len(info) < 8:
                        a_count, o_count = 0, 0
                        for i in info:
                            if(i[1] != max_px):
                                o_count += 1
                                if(int(i[0].split('_')[1]) > clustered_img.shape[1]//5):
                                    a_count += 1
                                    only_anno_end = True
                                    break
                                else:
                                    only_anno_end = False
                        if(a_count == 1):
                            a_height += 1
                        else:
                            conti_heights_list.append(a_height)
                            a_height = 0
                else:
                    if(only_anno_end is True):
                        anno_count += 1
                    else:
                        only_anno_end = False
                    conti_heights_list.append(a_height)
                    a_height = 0
        if(len(conti_heights_list) > 0 and max(conti_heights_list) > 2 and anno_count >= clustered_img.shape[0]//10):
            return True
        else:
            return False

    @ staticmethod
    def pixel_diff(pix_1, pix_2):
        r_diff = (abs(int(pix_1[0]) - int(pix_2[0])))**2
        g_diff = (abs(int(pix_1[1]) - int(pix_2[1])))**2
        b_diff = (abs(int(pix_1[2]) - int(pix_2[2])))**2

        diff = r_diff + g_diff + b_diff
        return diff/255

    @staticmethod
    def convert_img_pix(img, to_black, to_white):
        # Height
        axis_1 = len(img)
        # Width
        axis_2 = len(img[0])

        white = [255, 255, 255]
        black = [0, 0, 0]
        for i in range(axis_1):
            for j in range(axis_2):
                if to_black:
                    if(all(img[i][j] == to_black)):
                        img[i][j] = black
                    else:
                        img[i][j] = white
                else:
                    if(all(img[i][j] == to_white)):
                        img[i][j] = white
                    else:
                        img[i][j] = black
        return img

    @staticmethod
    def cluster_pixels(img, cluster_size):
        image_2D = img.reshape(img.shape[0]*img.shape[1], img.shape[2])
        # Use KMeans clustering algorithm from sklearn.cluster to cluster pixels in image
        # tweak the cluster size and see what happens to the Output
        kmeans = KMeans(n_clusters=cluster_size, random_state=0).fit(image_2D)
        clustered = kmeans.cluster_centers_[kmeans.labels_]
        # Reshape back the image from 2D to 3D image
        clustered_3D = clustered.reshape(
            img.shape[0], img.shape[1], img.shape[2])
        return clustered_3D.astype('uint8')

    @staticmethod
    def find_contours(clustered_img, pix, debug_mode_check, temp_folderpath):
        img = PixelParser.convert_img_pix(
            clustered_img, pix, None)
        # if(debug_mode_check is True):
        #     cv2.imwrite(f'{temp_folderpath}.png', clustered_img)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(
            gray, 180, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_sorted = sorted(
            contours, key=lambda x: cv2.contourArea(x))
        return contour_sorted

    @staticmethod
    def find_text_color(midbw_lst, minbw_lst):
        # print("mid:" + str(midbw_lst), " \nmin: " + str(minbw_lst))
        mid_count_noise, min_count_noise, mid_count, min_count = 0, 0, 0, 0

        for i in midbw_lst:
            if(i == 4 or i == 2):
                mid_count_noise += 1
            else:
                mid_count += 1
        for i in minbw_lst:
            if(i == 4 or i == 2):
                min_count_noise += 1
            else:
                min_count += 1

        if(len(midbw_lst) < 3 and len(minbw_lst) > 3):
            if(min_count > 3):
                return "min"
            else:
                return "org"

        if(len(midbw_lst) > 3 and len(minbw_lst) < 3):
            if(mid_count > 3):
                return "mid"
            return "org"

        if(min_count > mid_count and mid_count_noise > min_count_noise):
            return "min"

        elif(min_count < mid_count and mid_count_noise < min_count_noise):
            return "mid"

        else:
            if(len(midbw_lst) > 10 and len(minbw_lst) > 10):
                per_min_noise_midbw = mid_count_noise/len(midbw_lst)
                per_min_noise_minbw = min_count_noise/len(minbw_lst)
                if(mid_count - min_count > 5 and abs(min_count_noise-mid_count_noise) <= 10):
                    return "mid"
                elif(min_count-mid_count > 5 and abs(min_count_noise-mid_count_noise) <= 10):
                    return "min"
                if(per_min_noise_midbw > per_min_noise_minbw):
                    return "min"
                elif(per_min_noise_midbw < per_min_noise_minbw):
                    return "mid"

            elif(len(midbw_lst) < 5 or len(minbw_lst) < 5 and len(minbw_lst)-len(midbw_lst) > 10):
                if(mid_count - min_count > 5):
                    return "mid"
                return "min"

            else:
                return "org"

    @staticmethod
    def preprocess_image(img, temp_folderpath, debug_mode_check):
        if(debug_mode_check is True):
            cv2.imwrite(f'{temp_folderpath}_org.png', img)
        clustered_3 = PixelParser.cluster_pixels(img, 3)
        clustered_img, color_hash, row_pix_info = PixelParser.create_colors_hash_table(
            clustered_3)
        clustered_3 = copy.deepcopy(clustered_img)
        clustered_img2 = copy.deepcopy(clustered_img)
        if(debug_mode_check is True):
            cv2.imwrite(f'{temp_folderpath}_cluster_3.png', clustered_img)
        annotate = PixelParser.identify_annotation(
            clustered_img, row_pix_info, color_hash)

        min_px = min(color_hash, key=color_hash.get)
        max_px = max(color_hash, key=color_hash.get)
        mid_px = None
        for k, v in color_hash.items():
            if(k != min_px and k != max_px):
                mid_px = k
                break
        mid_px = min_px if mid_px is None else mid_px
        max_px = [int(max_px[:3]), int(max_px[3:6]), int(max_px[6:])]
        min_px = [int(min_px[:3]), int(min_px[3:6]), int(min_px[6:])]
        mid_px = [int(mid_px[:3]), int(mid_px[3:6]), int(mid_px[6:])]

        if(annotate is True):
            px_to_conv = "annotate"
            finalimg = PixelParser.convert_img_pix(
                clustered_img, min_px, None)
        else:
            # If b/g is white(the max pixel), OCR extract texts quite accurately, so the img is returned as is
            if(max_px[0] >= 225 and max_px[1] >= 225 and max_px[2] >= 225):
                return img, "org"
            if(min_px == mid_px):
                finalimg = PixelParser.convert_img_pix(
                    clustered_img, min_px, None)
            else:
                minbw_lst, midbw_lst = [], []
                midbw_contour_sorted = PixelParser.find_contours(
                    clustered_img, mid_px, debug_mode_check, temp_folderpath+'_mid')
                for i in midbw_contour_sorted:
                    midbw_lst.append(i.size)

                minbw_contour_sorted = PixelParser.find_contours(
                    clustered_3, min_px, debug_mode_check, temp_folderpath+'_min')
                for i in minbw_contour_sorted:
                    minbw_lst.append(i.size)

                # returns either mid or min number of px is to be converted to black, or if the orginal is to be returned
                px_to_conv = PixelParser.find_text_color(
                    midbw_lst, minbw_lst)
                if(px_to_conv == "mid"):
                    finalimg = PixelParser.convert_img_pix(
                        clustered_img2, mid_px, None)
                elif(px_to_conv == "min"):
                    finalimg = PixelParser.convert_img_pix(
                        clustered_img2, min_px, None)
                else:
                    return img, "org"
        if(debug_mode_check is True):
            cv2.imwrite(f'{temp_folderpath}_final.jpg', finalimg)
        return finalimg, px_to_conv
