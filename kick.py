#!/usr/bin/env python

import os
import subprocess

if __name__ == "__main__":
    
    # Confirm that they've sourced their openrc credentials already
    if not os.environ.get('OS_PASSWORD'):
        raise Exception('You need to source your openrc file first.')
    
    #TODO(JMC): Consider using PIPE instead, ala 
    # http://stackoverflow.com/questions/13332268/python-subprocess-command-with-pipe
    subprocess.check_output("docker build .".split(" "), env=os.environ)