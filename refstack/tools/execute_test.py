#!/usr/bin/env python
# encoding: utf-8
# Copyright (c) 2014 Ted Chang @ IBM
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

import ConfigParser
import urllib2
import requests
import os
import fnmatch
import subprocess
import json
import argparse


class Test:
    def __init__(self, args):
        self.args = args
        self.api_ip = args['APP_ADDRESS']
        self.test_id = args['TEST_ID']
        '''
        Static variables
        TODO: future implementation may read some static variables from the
        miniTempest.Config which will have a refstack section.
        '''
        self.tempestHome = '/tempest'
        self.sampleConfFile = self.tempestHome + '/etc/tempest.conf.sample'
        self.miniConfig = '/tmp/miniTempest.config'
        self.tempestConfFile = '/tmp/tempest.config'
        self.saveMiniConfAs = '/tmp/miniTempest.config'
        self.testCaseFile = '/tmp/testCase.config'
        self.defaultTestCase = ['tempest']
        self.resultDir = self.tempestHome + '/.testrepository/'
        self.result = self.resultDir + 'result'
        self.sampleConfParser = ConfigParser.SafeConfigParser()
        self.sampleConfParser.read(self.sampleConfFile)
        self.miniConfDict = None
        self.extraConfDict = None
        self.mergedConfDict = {}

    def genConfig(self):
        ''' Find common keys in mini config and temepst sample config and
            then replace values in the tempest sample config
        '''
        self.miniConfDict = json.loads(self.getMiniConfig())
        self._mergeToSampleConf(self.miniConfDict)
        self._mergeToSampleConf({'identity' : self.args})

    def _mergeToSampleConf(self, new):
        for section in new:
            #second loop iterates through keys in a section
            for key in new[section]:
                #find common keys and replace values
                if self.sampleConfParser.has_option(section, key):
                    self.sampleConfParser.set(section, key, new[section][key])

    def writeConfToFile(self):
        '''
        write merged tempest config to a file
        '''
        try:
            self.sampleConfParser.write(open(self.tempestConfFile, 'w'))
        except AttributeError:
            self.genConfig(self)
            self.sampleConfParser.write(open(self.tempestConfFile, 'w'))

    def getMiniConfig(self):
        '''return a mini config in JSON string
        '''
        url = "http://%s/get-miniconf?test_id=" % (self.api_ip) + self.test_id
        j = urllib2.urlopen(url=url)
        return j.readlines()[0]

    def _getTestCaseFile(self):
        '''Get test cases list from mock up API. This is for debugging only
        since the full test is too long to run.
        '''
        url = "http://%s/get-testcases?test_id=" % (self.api_ip) + self.test_id
        j = urllib2.urlopen(url=url)
        return j.readlines()[0]

    def runTestCases(self):
        testcases = json.loads(self._getTestCaseFile())['testcases']
        try:
            for case in testcases:
                cmd = (self.tempestHome + '/run_tests.sh -C ' +
                       self.tempestConfFile + ' -N -- %s' % (case))
                subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print 'ERROR: ' + e.__str__()

    def postTestResult(self):
        '''
        Filter file names under self.resultDir by numbers in a list
        Sort  list as integers from lowest to highest.
        Concatanate files to sefl.result and then POST it.
        '''
        url = "http://%s/post-result?test_id=" % (self.api_ip) + self.test_id

        r_list = [l for l in os.listdir(self.resultDir)
                  if fnmatch.fnmatch(l, '[0-9]*')]
        r_list.sort(key=int)
        with open(self.result, 'w') as outfile:
            for r in r_list:
                with open(self.resultDir + r, 'r') as infile:
                    outfile.write(infile.read())
        files = {'file': open(self.result, 'rb')}
        r = requests.post(url, files=files)

    #TODO: This part is for image discovery
    def createImage(self):
        #connection = httplib.HTTPSConnection()
        pass

    def findSmallestFlavor(self):
        pass

    def deleteImage(self):
        pass

    def run(self):
        print 'Downloading miniConfig file'
        self.getMiniConfig()
        print 'Generating tempest.config'
        self.genConfig()
        self.writeConfToFile()
        print 'Downloading test case file'
        self._getTestCaseFile()
        print 'Running test cases'
        self.runTestCases()
        print 'Send back the result'
        self.postTestResult()

if __name__ == '__main__':
    ''' Generate tempest.conf from a tempest.conf.sample and then run test
    cases.
    Example:
        execute_test.py

    '''
    #TODO(JMC): Will support command-line override of ENV later...
    # args = {}
    # args = {key : os.environ[key] for key in ['APP_ADDRESS', 'TEST_ID']}
    mapping = [
        ("APP_ADDRESS", "APP_ADDRESS"),
        ("APP_ADDRESS", "app_address"), 
        ("TEST_ID", "TEST_ID"),
        ("OS_TENANT_NAME", "tenant_name"),
        ("OS_USERNAME", "username"),
        ("OS_PASSWORD", "password"),
        ("OS_AUTH_URL", "uri")]

    args = {key : os.environ[envkey] for (envkey, key) in mapping}
    test = Test(args)
    test.run()
