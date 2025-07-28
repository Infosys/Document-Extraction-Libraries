# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import requests


class Moderator():
    """Class to perform moderation"""
    # api_url: str = None

    def perform_moderation_checks(self, moderation_config, moderation_payload):
        """Method to perform moderation checks"""
        response = requests.post(
            moderation_config.get('api_url'), json=moderation_payload, headers=None,
            verify=False, timeout=180)
        result = response.json()
        return result.get('moderationResults')
