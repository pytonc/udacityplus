import unittest
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from models.User import User
from tests.testdata import *

class TestUser(unittest.TestCase):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    def tearDown(self):
        self.testbed.deactivate()

    def testValidUsername(self):


        for k, v in uv.iteritems():
            u = User.valid_username(k)
            self.assertEqual(u, v, k)

    def testValidPassword(self):

        for k, v in pv.iteritems():
            p = User.valid_password(k)
            self.assertEqual(p, v, k)

    # this needs to be implemented differently
    def testValidEmail(self):
        e = User.valid_email(email1)
        self.assertEqual(e, True, "With no existing user")
        u = User.save(username1, email1, password1)
        u.put()
        e = User.valid_email(email1)
        self.assertEqual(e, False, "After create user with the email being tested")

    def testValid(self):
        email = 'jzegan@gmail.com'
        for k, v in uv.iteritems():
            for p, t in pv.iteritems():
                valid = User.valid(k, email, p)
                self.assertEqual(valid, v and t, "{} - {}".format(k, p))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    return suite