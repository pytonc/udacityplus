from google.appengine.ext.ndb import Key
from google.appengine.ext import  ndb
from collections import OrderedDict
from google.appengine.api import memcache

LEVELS = ('Beginning', 'Intermediate', 'Advanced', 'Other')

class Source(ndb.Model):
    name        = ndb.StringProperty()
    url         = ndb.StringProperty()

class Course(ndb.Model):
    number      = ndb.IntegerProperty()
    dept        = ndb.StringProperty()
    cid         = ndb.ComputedProperty(lambda self: self.dept + str(self.number))
    name        = ndb.StringProperty(required=True)
    level       = ndb.StringProperty(choices=LEVELS)
    short_desc  = ndb.StringProperty()
    url         = ndb.StringProperty()
    long_desc   = ndb.TextProperty()
    source      = ndb.KeyProperty(Source)


    @classmethod
    def centid(self, source, dept, number):
        return ''.join([source.lower(), dept.lower(), str(number).lower()])

    @classmethod
    def add_course(self, **kwargs):
        source = kwargs['source']
        parent = Key(Source, source)

        kwargs['source'] = parent
        kn = self.centid(source, kwargs['dept'], kwargs['number'])
        kwargs['number'] = int(kwargs['number'])

        # remove if a new course added
        memcache.delete('courses_by_level_cid', namespace='udacityplus')

        return Course.get_or_insert(kn, **kwargs)

    @classmethod
    def courses_to_dict(cls):
        courses = memcache.get('courses_by_level_cid', namespace='udacityplus')
        if courses:
            return courses
        else:
            crquery = Course.query().order(Course.cid)

            courses = OrderedDict()
            for level in LEVELS:
                co = []
                for cr in crquery:
                    if cr.level == level:
                        co.append(cr)
                    courses[level] = co

            # store for 3 weeks
            memcache.add('courses_by_level_cid', courses, time=1814400, namespace='udacityplus')

            return courses

    @classmethod
    def courses_to_optgroup(cls):
        courses = memcache.get('courses_by_level_cid_lt', namespace='udacityplus')
        if courses:
            return courses
        else:
            crquery = Course.query().order(Course.cid)

            courses = []
            for level in LEVELS:
                co = []
                for cr in crquery:
                    if cr.level == level:
                        co.append(cr)
                courses.append((level, co))

            # store for 3 weeks
            memcache.add('courses_by_level_cid_lt', courses, time=1814400, namespace='udacityplus')

            return courses