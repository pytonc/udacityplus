import unittest
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from models.User import User
from tests.testdata import *
from util.searching import find_users, find_all
import webapp2


class TestUser(unittest.TestCase):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.u1 = User.save(username1, email1, password1)
        self.u2 = User.save(username2, email2, password2)

    def tearDown(self):
        self.testbed.deactivate()

    def testValidUsername(self):
        for k, v in uv.iteritems():
            u, err = User.valid_username(k)
            self.assertEqual(u, v, k)

    def testValidPassword(self):
        for k, v in pv.iteritems():
            p, err = User.valid_password(k)
            self.assertEqual(p, v, k)

    def testValidEmail(self):
        e, err = User.valid_email(email1)
        self.assertEqual(e, True, "With no existing user")
        u = User.save(username1, email1, password1)
#        u.put()
        e, err = User.valid_email(email1)
        self.assertEqual(e, False, "After create user with the email being tested")

    def testValid(self):
        email = 'jzegan@gmail.com'
        for k, v in uv.iteritems():
            for p, t in pv.iteritems():
                valid, err = User.valid(k, email, p)
                self.assertEqual(valid, v and t, "{} - {}".format(k, p))

    def testSave(self):
        email = 'jzegan@gmail.com'
        user_combos = []
        for k, v in uv.iteritems():
            for p, t in pv.iteritems():
                u = User.save(k, email, p)
                if u:
                    r = u.key.get()
                    if r:
                        self.assertEqual(r.username == k, v and t, "{}".format(k, p))
                        user_combos.append(r)
        self.assertEqual(len(user_combos), 2, "Should contain 2 users - per current test data (check if changed)")

    def testSearch(self):
        results = find_all()
        self.assertEqual(len(results), 3, "Should find 2 users, found: %s" % len(results))

        results = find_users("person")
        self.assertEqual(results.number_found, 2, "Should find 2 users, found: %s" % results.number_found)

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    return suite