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

import os
from refstack.utils import INSTANCE_FOLDER_PATH


class DockerBuildFile(object):
    '''*
    Build a docker buildfile with customized parameters from a pre-defined
    docker build file template
    '''
    test_id = None
    api_server_address = None
    tempest_code_url = None
    confJSON = None
    docker_template_file_name = 'docker_buildfile.template'
    docker_template_file = INSTANCE_FOLDER_PATH + "/refstack/tools/" \
        + docker_template_file_name

    def __init__(self):
        '''
        Constructor
        '''
        print self.docker_template_file

    def build_docker_buildfile(self, output_file_with_path):
        '''*
        Build a new docker build file based on a template and customized
        parameters
        '''
        output_dir = os.path.dirname(os.path.abspath(output_file_with_path))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        fin = open(self.docker_template_file, "rt")
        contents = fin.read()
        contents = contents.replace('THE_TEMPEST_CODE_URL',
                                    self.tempest_code_url)
        contents = contents.replace('THE_API_SERVER_ADDRESS',
                                    self.api_server_address)
        contents = contents.replace('THE_TEST_ID', self.test_id)
        contents = contents.replace('THE_CONF_JSON', self.confJSON)

        fout = open(output_file_with_path, "wt")
        fout.write(contents)
