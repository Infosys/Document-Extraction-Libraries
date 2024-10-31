# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import datetime


class CommonUtil:
    @classmethod
    def update_app_info(self, req_res_dict: dict, about_app: dict):
        req_res_dict.update(about_app)
        new_record_list = []
        for record in req_res_dict['records']:
            new_record = {**{'workflow': []}, **record}
            workflow_list = new_record.get("workflow")
            is_exist = any(x['service_name'] == about_app['service_name'] and x['service_version'] == about_app['service_version']
                           for x in workflow_list if x.get('service_name'))
            if not is_exist:
                workflow_list.append(about_app)
            new_record_list.append(new_record)
        req_res_dict['records'] = new_record_list

    @classmethod
    def sort_datalist_by_date(cls, datalist, key, timestamp_pattern='%Y-%m-%d %I:%M:%S %p'):
        def sort_by_dates(data):
            # for data in output_response:
            return datetime.datetime.strptime(data[key], timestamp_pattern)
        return sorted(datalist, key=sort_by_dates, reverse=True)
