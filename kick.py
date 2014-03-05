#!/usr/bin/env python

import os

from refstack import app as base_app
from refstack.tools.tempest_tester import TempestTester

if __name__ == "__main__":

    # Confirm that they've sourced their openrc credentials already
    if not os.environ.get('OS_PASSWORD'):
        raise Exception('You need to source your openrc file first.')

    app = base_app.create_app()
    app.test_request_context().push()
    test_id = os.environ.get('TEST_ID', "1000")
    TempestTester(test_id).execute_test()
