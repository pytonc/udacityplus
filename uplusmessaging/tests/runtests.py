#!/usr/bin/python
import sys
import os


APP_ENGINE = '/home/jzegan/google_appengine'
sys.path.insert(0, APP_ENGINE)

# so that
import dev_appserver
dev_appserver.fix_sys_path()
APP_PATH = os.path.abspath("/home/jzegan/code/udacityplus/uplusmessaging")
sys.path.insert(0, APP_PATH)

# for the No api proxy found for service "memcache";
# http://blairconrad.wordpress.com/2010/02/20/automated-testing-using-app-engine-service-apis-and-a-memcaching-memoizer/
from google.appengine.tools import dev_appserver as das
from google.appengine.tools.dev_appserver_main import ParseArguments
args, option_dict = ParseArguments(sys.argv) # Otherwise the option_dict isn't populated.
das.SetupStubs('local', **option_dict)


import unittest
from datastore import user_test, message_test


suite1 = user_test.suite()
suite2 = message_test.suite()

suite = unittest.TestSuite()
suite.addTest(suite1)
suite.addTest(suite2)

unittest.TextTestRunner(verbosity=2).run(suite)
