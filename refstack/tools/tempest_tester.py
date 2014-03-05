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

from docker_buildfile import DockerBuildFile
import json
import os
from refstack.refstack_config import RefStackConfig
import time

configData = RefStackConfig()

APP_ADDRESS = configData.get_app_address()

''' TODO: Determine tempest URL based on the cloud version '''
TEMPEST_URL = configData.get_tempest_url()


class TempestTester(object):
    '''Utility class to handle tempest test.'''

    test_id = None
    testObj = None
    cloudObj = None

    def __init__(self, test_id=None):
        '''Init method loads specified id.'''

        if test_id:
            self.test_id = test_id
            ''' TODO: Retrieve testObj and cloudObj '''

    def generate_miniconf(self):
        '''Return a JSON object representing the mini tempest conf.'''

        ''' TODO: Construct the JSON from cloud db obj '''
        ''' ForNow: Return the JSON in vendor config '''
        conf = configData.get_tempest_config()

        return json.dumps(conf)

    def generate_testcases(self):
        '''Return a JSON array of the tempest testcases to be executed.'''

        ''' TODO: Depends on DefCore's decision, either do the full test or
                  allow users to specify what to test
        '''
        ''' ForNow: Return the JSON in vendor config '''
        conf = configData.get_tempest_testcases()

        return json.dumps(conf)

    def process_resultfile(self, filename):
        '''Process the tempest result file.'''

        ''' TODO: store the file in test db obj '''
        ''' ForNow: write the file to console output '''
        with open(filename, 'r') as f:
            print f.read()
            f.close()

    def test_cloud(self, cloud_id, extraConfJSON=None):
        '''Create and execute a new test with the provided extraConfJSON.'''

        ''' TODO: Retrieve the cloud obj from DB '''

        ''' TODO: Create new test obj in DB and get the real unique test_id'''
        ''' ForNow: use timestamp as the test_id '''
        self.test_id = time.strftime("%m%d%H%M")

        ''' invoke execute_test '''
        self.execute_test(extraConfJSON)

    def execute_test(self, extraConfJSON=None):
        '''Execute the tempest test with the provided extraConfJSON.'''

        dockerFile = '%s/test_%s.dockerFile' % (configData.get_working_dir(),
                                                self.test_id)

        ''' Create the docker build file '''
        fileBuilder = DockerBuildFile()
        fileBuilder.test_id = self.test_id
        fileBuilder.api_server_address = APP_ADDRESS
        fileBuilder.tempest_code_url = TEMPEST_URL
        fileBuilder.confJSON = extraConfJSON
        fileBuilder.build_docker_buildfile(dockerFile)

        ''' Execute the docker build file '''
        outFile = '%s/test_%s.dockerOutput' % (configData.get_working_dir(),
                                               self.test_id)
        cmd = 'nohup docker build - < %s > %s &' % (dockerFile, outFile)
        os.environ['DOCKER_HOST'] = 'tcp://localhost:4243'
        os.system(cmd)
        print cmd

        ''' TODO: Clean up the temporary docker build and output file '''
