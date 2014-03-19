#!/usr/bin/env python

import os
import subprocess

from refstack import app as base_app
from refstack.tools.tempest_tester import TempestTester

if __name__ == "__main__":
    
    # Confirm that they've sourced their openrc credentials already
    if not os.environ.get('OS_PASSWORD'):
        raise Exception('You need to source your openrc file first.')
    
    #TODO(JMC): Consider using PIPE instead, ala 
    # http://stackoverflow.com/questions/13332268/python-subprocess-command-with-pipe

    app = base_app.create_app()
    app.test_request_context().push()
    test_id = "1000"
    TempestTester(test_id).execute_test()