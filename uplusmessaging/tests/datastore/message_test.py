import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from models.Message import Conversation
from models.User import User
from tests.testdata import *


class TestMessages(unittest.TestCase):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.u1 = User.save(username1, email1, password1)
        self.u2 = User.save(username2, email2, password2)

    def tearDown(self):
        self.testbed.deactivate()

    def testCreate(self):
        ck = User.add_new_conversation(self.u1.username_norm, self.u2.username_norm, 'sample title', 'sample content')

        conv = ck.get()
        self.assertEqual(conv.title, 'sample title')
        self.assertEqual(conv.messages[0].content, 'sample content')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMessages))
    return suite