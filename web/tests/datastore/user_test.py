import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from web.models.Details import CourseAttempt
from web.models.Course import  Source
from web.models import User, Course
from web.tests.testdata import *


class TestUser(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        # make sure you know what this does
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.u1 = User.save(username1, email1, password1)
        self.u2 = User.save(username2, email2, password2)

        self.createNewSource()
        self.createNewCourses()
        self.courses = self.createNewAttempts()


    def tearDown(self):
        self.u1.delete_all_courses()
        self.testbed.deactivate()

    def createNewSource(self):
        s = Source(
            name = sources['name'],
            url = sources['url']
        )
        s.put()

    def createNewAttempts(self):
        courses = Course.query()
        attempts = []
        for course in courses:
            k = self.u1.add_course(course.key)
            attempts.append(k)

        courses = self.u1.get_all_courses()
        try:
            o = [c for c in courses if c.course == ndb.Key(Course, 'udacitycs215')][0]
        except IndexError:
            raise ValueError("Test data is wrong")
        o.completed = False
        o.put()
        return attempts

    def createNewCourses(self):
        for course in courses:
            c = Course.add_course(**course)

    def testGetAllCourses(self):
        courses = Course.query().count(10)

        self.assertEqual(courses, 3, "Wrong number of courses %s should be 3" % courses)

    def testGetAllAttempts(self):
        attempts = CourseAttempt().query().fetch(10)
        self.assertEqual(len(attempts), 3, "Wrong number of attempts %s, should be 3" % attempts)

    def testGetCourse(self):
        completed = self.u1.get_courses()
        incomplete = self.u1.get_courses(completed=False)

        self.assertEqual(len(completed), 2, "Not get completed courses %s" % len(completed))
        self.assertEqual(len(incomplete), 1, "Not get in progress courses %s" %len(incomplete))

    def testDeleteCourse(self):
        self.u1.delete_courses()
        self.u1.delete_courses(completed=False)

        completed = self.u1.get_courses()
        incomplete = self.u1.get_courses(completed=False)
        all = self.u1.get_all_courses()

        self.assertEqual(len(completed), 0, "Not deleted completed courses: %s" % len(completed))
        self.assertEqual(len(incomplete), 0, "Not deleted in progress courses: %s" % len(completed))
        self.assertEqual(len(all), 0, "Not deleted in all courses: %s" % len(all))

    def testDeleteSingleCourse(self):
        completed = self.u1.get_courses()

        self.assertEqual(len(completed), 2, "Incorrect completed course number")

        delcourse = completed[0].key
        delname = completed[0].course.get().name

        self.u1.remove_course(delcourse)
        self.assertEqual(len(completed), 2,
            "Incorrect completed course number after course %s deletion" % delname)

        self.u1.remove_course(delcourse)
        self.assertEqual(len(completed), 2,
            "Incorrect completed course number after deleted course %s deletion" % delname)

    def testUsersInCourse(self):
        inCS101c = CourseAttempt.query(
            CourseAttempt.course == ndb.Key(Course, 'udacitycs101'),
            CourseAttempt.completed == True).fetch(5)

        self.assertEqual(len(inCS101c), 1, "Wrong number of students completed CS101: %s should be 1" % len(inCS101c))

        incomplete = CourseAttempt.query(
            CourseAttempt.completed == False
        ).fetch(5)

        self.assertEqual(len(incomplete), 1, "Wrong number of total course enrollments %s should be 1" % len(incomplete))

        completed = CourseAttempt.query(
            CourseAttempt.completed == True
        ).fetch(5)

        self.assertEqual(len(completed), 2, "Wrong number of total course enrollments %s should be 2" % len(completed))

    def testStudentsInClass(self):
        uinCS101 = CourseAttempt.query(
            CourseAttempt.course == ndb.Key(Course, 'udacitycs101'),
        ).get()

        self.assertIsNotNone(uinCS101, "Zero students in class, should be non-zero")
        self.assertEqual(uinCS101.student,
            self.u1.key, "Wrong user %s, should be %s" %
                                   (uinCS101.student, self.u1.key)
        )

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    return suite