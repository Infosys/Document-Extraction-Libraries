# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class FileSystemReaderConfigData(object):
    read_path: str = None
    filter: dict = None

    def __init__(self, read_path: str, filter: dict) -> None:
        self.read_path = read_path
        self.filter = FSDFilterConfigData(**filter)


class FSDFilterConfigData(object):
    def __init__(self, include: list, exclude: list) -> None:
        self.include = include
        self.exclude = exclude
