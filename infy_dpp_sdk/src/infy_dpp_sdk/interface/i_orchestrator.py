# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
import json
import logging
import infy_fs_utils
from ..common import Constants
from ..common.config_data_helper import ConfigDataHelper


class IOrchestrator(ABC):
    """Orchestrator interface for remote execution of processors"""

    class Model():
        """Model class (MVC model)"""
        input_config_file_path: None
        deployment_config_file_path: None
        input_config_data: None
        deployment_config_data: None

    def __init__(self, input_config_file_path: str, deployment_config_file_path: str = None):
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        config_data_helper_obj = ConfigDataHelper(self.__logger)

        model = self.Model()
        model.input_config_file_path = input_config_file_path
        model.deployment_config_file_path = deployment_config_file_path

        # Input config data loading and interpolation
        input_config_data = json.loads(self.__fs_handler.read_file(
            input_config_file_path))
        model.input_config_data = config_data_helper_obj.do_interpolation(
            input_config_data)

        # Deployment config data loading and interpolation
        model.deployment_config_data = None
        auto_generated_deployment_config = False
        if model.deployment_config_file_path:
            deployment_config_data = json.loads(self.__fs_handler.read_file(
                model.deployment_config_file_path))
        else:
            deployment_config_data = config_data_helper_obj.generate_default_deployment_config(
                input_config_data)
            auto_generated_deployment_config = True
        model.deployment_config_data = config_data_helper_obj.do_interpolation(
            deployment_config_data)

        # Validate the config files
        validation_messages = config_data_helper_obj.validate_dpp_input_config(
            model.input_config_data, model.deployment_config_data)
        if not auto_generated_deployment_config:
            validation_messages += config_data_helper_obj.validate_dpp_deployment_config(
                model.deployment_config_data)

        if validation_messages:
            message = "Validation of DPP config file(s) failed. " + \
                ".".join(validation_messages)
            self.__logger.error(message)
            raise Exception(message)
        self.__model = model

    @abstractmethod
    def run_batch(self, context_data: dict = None):
        """Run the pipeline"""
        raise NotImplementedError("run_batch not implemented")

    def _get_model(self):
        return self.__model

    def _get_logger(self):
        return self.__logger

    def _get_fs_handler(self):
        return self.__fs_handler
