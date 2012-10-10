import unittest
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from models.User import User
from models.Course import Course, Source
from tests.testdata import *


class TestUser(unittest.TestCase):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.u1 = User.save(username1, email1, password1)
        self.u2 = User.save(username2, email2, password2)

        self.createNewSource()
        self.courses = self.createNewCourses()

        self.u1.add_courses([c.key.id() for c in self.courses[:2]])
        self.u1.add_courses([self.courses[2].key.id()], completed=False)

    def tearDown(self):
        self.u1.delete_all_courses()
        self.u1.delete_all_courses(completed=False)

        self.testbed.deactivate()

    def createNewSource(self):
        s = Source(
            name = sources['name'],
            url = sources['url']
        )
        s.put()

    def createNewCourses(self):
        cm = []
        for course in courses:
            c = Course.add_course(**course)
            cm.append(c)
        return cm

    def testGetCourse(self):
        completed = self.u1.get_courses()
        incomplete = self.u1.get_courses(completed=False)

        self.assertEqual(len(completed), 2, "Not get completed courses")
        self.assertEqual(len(incomplete), 1, "Not get in progress courses")


    def testDeleteCourse(self):
        self.u1.delete_all_courses()
        self.u1.delete_all_courses(completed=False)

        completed = self.u1.get_courses()
        incomplete = self.u1.get_courses(completed=False)

        self.assertEqual(len(completed), 0, "Not deleted completed courses: %s" % len(completed))
        self.assertEqual(len(incomplete), 0, "Not deleted in progress courses: %s" % len(completed))

    def testDeleteSingleCourse(self):
        completed = self.u1.get_courses()

        self.assertEqual(len(completed), 2, "Incorrect completed course number")
        self.u1.remove_course(completed[0].key.id())
        self.assertEqual(len(completed), 2,
            "Incorrect completed course number after course %s deletion" % completed[0].name)



def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    return suite