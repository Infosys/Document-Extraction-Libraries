# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import numpy as np
import cv2
import tempfile
import random
import subprocess
from IPython.display import display, Image, clear_output, HTML
import ipywidgets as widgets

class DemoHelper():    
    class Constants():
        COLOR_BLUE = (255, 0, 0)
        COLOR_RED = (0, 0, 255)
        COLOR_GRAY = (211,211,211)
    
    @classmethod
    def read_image(cls, image_path):
        image = cv2.imread(image_path)
        return image
    
    @classmethod
    def convert_grayscale_to_rgb(cls, img_obj):
        stacked_img = np.stack((img_obj,)*3, axis=-1)
        return stacked_img

    @classmethod
    def draw_bboxes_on_image(cls, image, bboxes_list, border_color=Constants.COLOR_BLUE, 
                             border_thickness=4, write_coordinates=False, write_thickness=3):
        if len(image.shape) == 2:
            image = cls.convert_grayscale_to_rgb(image)
        
        # Draw boxes on image
        for rt_bbox in bboxes_list:
            (l, t, w, h) = tuple([int(i) for i in rt_bbox])
            image = cv2.rectangle(
                image, (l, t), (l + w, t + h), color=border_color, thickness=border_thickness)
            if write_coordinates:
                cv2.putText(image, f"[{l},{t},{w},{h}]",
                            (l-write_thickness, t-write_thickness), cv2.FONT_HERSHEY_PLAIN, write_thickness, border_color)
        return image
    
    @classmethod
    def show_image(cls, image):
        image= cv2.copyMakeBorder(image,1,1,1,1,cv2.BORDER_CONSTANT)
        _,enc_img = cv2.imencode('.jpg', image) 
        display(Image(data=enc_img))

    @classmethod
    def calculate_container_bbox(cls, bbox_array_list:list):
        # Expected format of bboxes_list is [[x,y,w,h]]
        _bbox_array_list = [[x1,y1, x1+w, y1+h] for x1,y1,w,h in bbox_array_list]
        x_min = min([min(x1,x2) for x1,y1,x2,y2 in _bbox_array_list])
        y_min = min([min(y1,y2) for x1,y1,x2,y2 in _bbox_array_list])
        x_max = max([max(x1,x2) for x1,y1,x2,y2 in _bbox_array_list])
        y_max = max([max(y1,y2) for x1,y1,x2,y2 in _bbox_array_list])
        return [x_min, y_min, x_max-x_min, y_max - y_min]
    
    @classmethod
    def reduce_image_based_on_context(cls, image, bbox_array_list):
        height, width, _ = image.shape
        _bbox_array_list = [[int(x1), int(y1), int(w), int(h)] for x1,y1,w,h in bbox_array_list]
        container_bbox = cls.calculate_container_bbox(_bbox_array_list)
        l,t,w,h = 0, max(0,container_bbox[1]-200) ,width, min(container_bbox[3]+400,height)
        reduced_image = image[t:t+h, 0:w]
        return reduced_image
    
    @classmethod
    def create_tab_toolbar(cls, tab_labels):
        tab_children = []
        for i in range(len(tab_labels)):
            output_tab = widgets.Output(layout={"border": "0px solid green"})
            tab_children.append(output_tab)

        tab = widgets.Tab()
        tab.children = tab_children
        for i in range(len(tab_children)):
            tab.set_title(i, str(tab_labels[i]))
        return tab 
    
    @classmethod
    def read_file(cls, file_path):
        with open(file_path, encoding='UTF-8') as file:
            data = file.read()
            return data
        
    @classmethod
    def get_shortened_text(cls, text, max_line_count=None, max_text_length=None):
        if max_line_count:
            lines = text.split('\n')
            if len(lines)<=max_line_count:
                return text 
            mid_point = int(max_line_count/2)
            new_lines = lines[0:mid_point] + ['...','...','...'] + lines[-mid_point:]
            new_text = '\n'.join(new_lines)
            return new_text
        if max_text_length:
            if len(text)<=max_text_length:
                return text
            mid_point = int(max_text_length/2)
            new_text = text[0:mid_point] + '\n...\n...\n...\n' + text[-mid_point:]
            return new_text
        
    @classmethod
    def visualize_get_bbox_for_result(cls, get_bbox_for_result, image_path_list):
        for region in get_bbox_for_result['regions']:
            anchor_text_bboxes = []
            region_bboxes = []
            for item in region['anchorTextBBox']:
                anchor_text_bboxes.append(item['bbox'])
            page_region_bboxes_dict = {}
            for item in region['regionBBox']:
                page = item['page']
                items = page_region_bboxes_dict.get(page, [])
                items.append(item['bbox'])
                page_region_bboxes_dict[page] = items

            pages = sorted(page_region_bboxes_dict.keys())
            for page in pages:
                region_bboxes = page_region_bboxes_dict[page]
                all_bboxes = anchor_text_bboxes + region_bboxes

                print('page =', page)
                print('anchor_text_bboxes =', anchor_text_bboxes)
                print('region_bboxes =', region_bboxes)

                img = cls.read_image(image_path_list[page-1])
                img = cls.draw_bboxes_on_image(img, anchor_text_bboxes, border_color = cls.Constants.COLOR_BLUE)
                img = cls.draw_bboxes_on_image(img, region_bboxes, border_color = cls.Constants.COLOR_RED)
                img = cls.reduce_image_based_on_context(img, all_bboxes)

                cls.show_image(img)

    @classmethod
    def check_command(cls, run_command_list):
        # run_command_list=['tesseract','--version']
        try:
            sub_process = subprocess.Popen(
                        run_command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        universal_newlines=True)
            stdout, stderr = sub_process.communicate()
            if (not stdout and stderr):
                display(HTML("<p style='color:Red'><b>ERROR: </b>Command failed: "
                            + ' '.join(run_command_list) + "</p>"))
                if 'tesseract' in run_command_list:
                    display(HTML("<div style='line-height: 1;color:Red'>"+
                                "<span>Install Tesseract.<br>"
                                +"Add it's home path to environment PATH variable."
                                +" e.g.'C:/Program Files/Tesseract-OCR'</span>"+"</div>"))
        except Exception:
            display(HTML("<p style='color:Red'><b>ERROR: </b>Command failed: "
                        + ' '.join(run_command_list) + "</p>"))
