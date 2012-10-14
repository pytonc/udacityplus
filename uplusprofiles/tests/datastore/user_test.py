import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from models.Details import CourseAttempt
from models.User import User
from models.Course import Course, Source
from tests.testdata import *


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
        courses = Course.query().fetch(20)
        for course in courses:
            self.u1.add_course(course.key)
        o = self.u1.courses[-1].get()
        o.completed = False
        o.put()
        return self.u1.courses

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

    def testTypeError(self):
        with self.assertRaises(TypeError) as e:
            self.u1.reassign_courses('asdf')

    def testReassignCourses(self):
        nc = CourseAttempt(
            course=Course.get_by_id('udacitycs101').key,
            completed=True)
        nc.put()
        newcourses = [nc]

        self.u1.reassign_courses(newcourses)
        c = self.u1.get_courses()
        i = self.u1.get_courses(completed=False)

        self.assertEqual(len(c), 1, "Badly reassigned course list: %s, should be 1" % len(c))
        self.assertEqual(len(i), 0, "Badly reassigned incomplete course number: %s, should be 0" % len(i))

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

    def testUserInClass(self):
        uinCS101 = CourseAttempt.query(
            CourseAttempt.course == ndb.Key(Course, 'udacitycs101'),
        ).fetch(20)

        self.assertIsNotNone(uinCS101, "Zero students in class, should be non-zero")
        self.assertEqual(uinCS101[0].key.parent().get().username_norm,
            self.u1.username_norm, "Wrong user %s, should be %s" %
                                   (uinCS101[0].key.parent().get().username_norm, self.u1.username_norm)
        )

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    return suite