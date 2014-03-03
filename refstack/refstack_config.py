# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 IBM Corp
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import os.path
from refstack.utils import INSTANCE_FOLDER_PATH


class RefStackConfig(object):

    refstack_config = {}
    config_file_name = '%s/config.json' % (INSTANCE_FOLDER_PATH)
    working_dir = '%s/tmpfiles' % (INSTANCE_FOLDER_PATH)

    def __init__(self, file_name=None):
        if file_name:
            self.config_file_name = file_name
        if os.path.isfile(self.config_file_name):
            self.refstack_config = json.load(open(self.config_file_name))

    def get_working_dir(self):
        return self.working_dir

    def get_app_address(self):
        return self.refstack_config["app_address"]

    def get_tempest_url(self):
        return self.refstack_config["tempest_url"]

    def get_tempest_config(self):
        return self.refstack_config["tempest_config"]

    def get_tempest_testcases(self):
        return self.refstack_config["tempest_testcases"]
