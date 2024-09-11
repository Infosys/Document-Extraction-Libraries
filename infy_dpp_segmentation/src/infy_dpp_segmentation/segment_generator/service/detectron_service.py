# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from PIL import Image

import numpy
import infy_dpp_sdk
import infy_fs_utils
try:
    import torch
    from detectron2.engine import DefaultPredictor
    from detectron2.config import get_cfg
except Exception as e:
    print(f"{e}")

ID2LABEL = {0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}


class DetectronService:
    '''detectron service class'''

    def __init__(self, model_config_dict: dict) -> None:
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        try:
            cfg = get_cfg()
            cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
            # Load your Detectron2 model config
            cfg.merge_from_file(model_config_dict['config_file_path'])
            # Set the threshold for prediction
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = model_config_dict['model_threshold']
            # Load your trained model weights
            cfg.MODEL.WEIGHTS = model_config_dict['model_path']
            self.__predictor = DefaultPredictor(cfg)
        except Exception as ex:
            self.__logger.error(f"{ex}")

    def get_bbox(self, image_file_path) -> list:
        '''get bbox from image using detectron model'''
        try:
            image_io = Image.open(image_file_path)
            image = numpy.array(image_io)
            output = self.__predictor(image)
            id2label = ID2LABEL
            model_outputs_list = []
            instances = output["instances"].to("cpu")
            for i in range(len(instances)):
                pred_class = id2label[instances.pred_classes[i].item()]
                # Assuming single instance detection
                bbox = instances.pred_boxes[i].tensor.tolist()[0]
                score = instances.scores[i].item()
                content = ''
                # page = os.path.splitext(os.path.basename(image_path))[0]
                segment = -1

                result = {
                    "content_type": pred_class,
                    "content": content,
                    "content_bbox": bbox,
                    "confidence_pct": score,
                    "page": -1,
                    "segment_no": segment
                }
                model_outputs_list.append(result)
        except Exception as ex:
            self.__logger.error(f"{ex}")
            model_outputs_list = []
        return model_outputs_list
