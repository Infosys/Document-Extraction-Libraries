# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import enum


class OcrConstants(object):
    TXT = "text"
    WORDS = "words"
    ANCHOR2 = "anchor2"
    PAGE = "page"
    BBOX = "bbox"
    CONF = "conf"
    PAGE_NUM = "pageNum"
    C_PARAM = "charparams"
    C_CONF = "charconfidence"
    LINE = "line"

    BB_X = 0
    BB_Y = 1
    BB_W = 2
    BB_H = 3

    DOC_ANC_TXT_BOD = "{{BOD}}"
    DOC_ANC_TXT_EOD = "{{EOD}}"


class TokenType(enum.Enum):
    WORD = 1
    LINE = 2
    PHRASE = 3


class RegUnitsRe(object):
    PIXEL_RE = r"^-?[0-9]+[.]?[0-9]*(px)?$"
    PERCT_REL_RE = r"^-?[0-9]+%(r)?$"
    PERCT_ABS_RE = r"^-?[0-9]+%a$"
    STARTS_WITH_NUM_RE = r"^[0-9]"
    NUM_RE = r"-?[0-9]+[.]?[0-9]*"
    TEXT_SIZE_RE = r"^-?[0-9]+(.[0-9]+)?t$"


class BBoxLabel(object):
    LEFT = "left"
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"


class RegLabel(object):
    A_TXT = "anchorText"
    A_POINT_1 = "anchorPoint1"
    A_POINT_2 = "anchorPoint2"


class ResProp(object):
    PAGE = "page"
    BBOX = "bbox"
    ERROR = "error"
    REGIONS = "regions"
    REG_BBOX = "regionBBox"


class PlotBbox(object):
    COLOR_NAMES = ["red", "orange", "yellow", "parrot", "green", "spring_green",
                   "cyan", "light_blue", "blue", "violet", "magenta", "pink"]
    COLOR_DICT = {
        "red": [255, 0, 0],
        "orange": [255, 128, 0],
        "yellow": [255, 255, 0],
        "parrot": [128, 255, 0],
        "green": [0, 255, 0],
        "spring_green": [0, 255, 128],
        "cyan": [0, 255, 255],
        "light_blue": [0, 128, 255],
        "blue": [0, 0, 255],
        "violet": [128, 0, 255],
        "magenta": [255, 0, 255],
        "pink": [255, 0, 128]
    }
