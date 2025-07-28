# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import ctypes
import tkinter as tk
from PIL import Image, ImageDraw, ImageColor, ImageTk
import imageio

# Note : enable "DEBUG_MODE_ENABLED" in ".env" file to visualize region highlights
DEBUG_MODE_ENABLED = os.environ['DEBUG_MODE_ENABLED']

TEMP_DIR_PATH = './data/temp'
if not os.path.exists(TEMP_DIR_PATH):
    os.makedirs(TEMP_DIR_PATH)

SCALING_FACTOR = {
    'hor': 1,
    'ver': 1
}


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
        # img = img._PhotoImage__photo.subsample(scale_down_factor)

        canvas.create_image(0, 0, anchor=tk.NW, image=img)

        root.mainloop()


def get_bbox_for(reg_def_dict, ocr_obj, img_copy=None, img_file_path=None, sub_reg_def_dict=[],
                 scaling_factor=SCALING_FACTOR):
    regions_res = ocr_obj.get_bbox_for(
        reg_def_dict, sub_reg_def_dict, scaling_factor)
    multi_page_res_bbox = []
    if not regions_res["error"]:
        for bbox in regions_res["regions"]:
            reg_bbox_list = bbox["regionBBox"]
            multi_page_res_bbox += [reg_bbox_list]
            if DEBUG_MODE_ENABLED == 'true' and len(reg_bbox_list) > 0:
                if len(reg_bbox_list) == 1:
                    __singlepage_region(
                        reg_bbox_list, img_file_path, ocr_obj, bbox, img_copy)
                else:
                    print("Regions found from multiple pages...")
                    __multipage_regions(reg_bbox_list, img_file_path, ocr_obj)

    print(multi_page_res_bbox)
    for res_bbox in multi_page_res_bbox:
        for res in res_bbox:
            del res['text']
    print(regions_res["error"])
    return multi_page_res_bbox, regions_res["error"]


def __singlepage_region(reg_bbox_list, img_file_path, ocr_obj, bbox, img_copy):
    for i, reg_bbox in enumerate(reg_bbox_list):
        show = True if len(reg_bbox_list) == i+1 else False
        img_file_path_temp = None
        if img_file_path:
            img_file_path_temp = img_file_path + \
                "/"+str(reg_bbox["page"])+".jpg"
            img_copy = imageio.imread(img_file_path_temp)
        scale_fact_obj = _get_img_scale_factor(
            img_file_path_temp, ocr_obj, img_copy)
        print(scale_fact_obj["warnings"])
        img_pil = Image.fromarray(img_copy)
        for at_bbox in bbox["anchorTextBBox"]:
            __highlight_area(_scale_bbox(
                at_bbox["bbox"], scale_fact_obj["scalingFactor"]), img_pil,
                border_color="blue")
        __highlight_area(_scale_bbox(
            reg_bbox["bbox"], scale_fact_obj["scalingFactor"]), img_pil,
            border_color="red", show_matplot=show)


def __multipage_regions(reg_bbox_list, img_file_path, ocr_obj):
    for reg_bbox in [reg_bbox_list]:
        reg_bbox_temp = []
        for bbox in reg_bbox:
            img_file_path_temp = img_file_path + \
                "/"+str(bbox["page"])+".jpg"
            scale_fact_obj = _get_img_scale_factor(
                img_file_path_temp, ocr_obj)
            print(scale_fact_obj["warnings"])
            bbox["bbox"] = _scale_bbox(
                bbox["bbox"], scale_fact_obj["scalingFactor"])
            reg_bbox_temp.append(bbox)
        result = _merge_images_for(
            reg_bbox_temp, img_file_path)
        merged_img = imageio.imread(result["output"]["imagePath"])
        temp_file_path = os.path.abspath(f"{TEMP_DIR_PATH}/debug_image.jpg")
        merged_img.save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)


def __highlight_area(bbox, img_pil, border_color="blue",
                     border_thickness=4,
                     show_matplot=False):

    (l, t, w, h) = bbox
    draw_obj = ImageDraw.Draw(img_pil)
    # Draw boxes on image
    draw_obj.rectangle(((l, t), (l + w, t + h)),
                       outline=ImageColor.getrgb(border_color), width=border_thickness)
    if show_matplot:
        temp_file_path = os.path.abspath(f"{TEMP_DIR_PATH}/debug_image.jpg")
        img_pil.save(temp_file_path)
        ImageVisualizer.show_image(temp_file_path)
        # img_copy = imageio.imread(temp_file_path)
        # plt.imshow(img_copy)
        # plt.show()
        # img = Image.open(temp_file_path)
        # img.show()


def __make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def __delete_id_from_dict(res_dict):
    if type(res_dict) is list:
        for re_dict in res_dict:
            _delete_id(re_dict)
    elif type(res_dict) is dict:
        _delete_id(res_dict)


def __pdf_to_img(from_file, to_dir):
    if not os.path.exists(to_dir):
        try:
            import subprocess
            tool_path = os.path.abspath(
                r"C:\ProgramFiles\InfyFormatConverter\infy-format-converter-0.0.10.jar")
            p = subprocess.Popen(['java', '-jar', tool_path, 'PdfToImg', '--fromfile', from_file,
                                  '--todir', to_dir, '--dpi', '300'], shell=True, stdout=subprocess.PIPE)
            p.communicate()
        except Exception as e:
            print(e)


def _scale_bbox(bbox, scaling_factor):
    bbox[0], bbox[2] = int(bbox[0] *
                           scaling_factor['hor']), int(bbox[2]*scaling_factor['hor'])
    bbox[1], bbox[3] = int(bbox[1] *
                           scaling_factor['hor']), int(bbox[3]*scaling_factor['hor'])
    return bbox


def _get_img_scale_factor(img_file_path, ocr_obj, img_copy=None):
    im = imageio.imread(img_file_path) if img_file_path else img_copy
    return ocr_obj.calculate_scaling_factor(im.shape[1], im.shape[0])


def _delete_id(dict_obj):
    if "id" in dict_obj:
        del dict_obj["id"]
    if "words" in dict_obj:
        __delete_id_from_dict(dict_obj["words"])


def _merge_images_for(region_bbox, img_file_path, output_path=None):
    merged_img_path = error = None
    try:
        cropped_img_list = []
        region_bbox.sort(key=lambda x: (x["page"]))
        output_path_temp = __make_dirs(
            output_path if output_path else "{}/merged_images".format(img_file_path))
        for page_bbox in region_bbox:
            l, t, w, h = page_bbox["bbox"]
            page_img = imageio.imread(
                img_file_path+"/"+str(page_bbox["page"])+".jpg")
            crop_img = page_img[t:t+h, l:l+w]
            new_img_name = _concat_page_bbox(page_bbox)
            new_img_path = output_path_temp+"/" + new_img_name+".jpg"
            imageio.imwrite(new_img_path, crop_img)
            cropped_img_list.append(new_img_path)
        cat_img = _concatenate_images(cropped_img_list, is_vertical=True)
        first_page = _concat_page_bbox(region_bbox[0])
        last_page = _concat_page_bbox(region_bbox[len(region_bbox)-1])
        merged_img_path = "{}/fp{}-lp{}.jpg".format(
            output_path_temp, first_page, last_page)
        imageio.imwrite(merged_img_path, cat_img)
        _remove_files(cropped_img_list)
    except Exception as e:
        error = e.args[0]
    return {"output": {"imagePath": merged_img_path}, "error": error}


def _concat_page_bbox(p_bbox_obj):
    l, t, w, h = [str(int) for int in p_bbox_obj["bbox"]]
    return "{}_l{}t{}w{}h{}".format(str(p_bbox_obj["page"]), l, t, w, h)


def _concatenate_images(image_path_list: list, is_vertical: bool):
    """Merge given list of images in a specified direction"""
    for image_path in image_path_list:
        if not os.path.exists(image_path):
            raise ValueError(f"Provide valid image file paths {image_path}")
    image_obj_list = [Image.open(x) for x in image_path_list]
    image_size_list = [x.size for x in image_obj_list]
    print(image_size_list)
    if is_vertical:
        new_width = max([x[0] for x in image_size_list])
        new_height = sum([x[1] for x in image_size_list])
    else:
        new_width = sum([x[0] for x in image_size_list])
        new_height = max([x[1] for x in image_size_list])
    print('new_width =', new_width, 'new_height =', new_height)

    new_image = Image.new('RGB', (new_width, new_height))
    x_or_y_offset = 0
    for img_obj in image_obj_list:
        if is_vertical:
            new_image.paste(img_obj, (0, x_or_y_offset))
            x_or_y_offset += img_obj.size[1]
        else:
            new_image.paste(img_obj, (x_or_y_offset, 0))
            x_or_y_offset += img_obj.size[0]
    return new_image


def _remove_files(file_list):
    for file in file_list:
        os.remove(file)


def validate_file_contents(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        contents1 = f1.read()
        contents2 = f2.read()
    return contents1 == contents2
