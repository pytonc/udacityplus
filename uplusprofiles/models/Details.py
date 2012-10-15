from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from models.Course import Course


TOOL_CATEGORIES = ("Languages", "Software/Libraries")
LEVEL_OPTIONS = (1, 2, 3, 4, 5)


class ExternalProfileLink(ndb.Model):
    url             = ndb.StringProperty(required=True)
    profile_loc     = ndb.StringProperty(required=True, choices={'Facebook', 'Twitter', 'G+',
                                                                 'LinkedIn', 'Website', 'GitHub', 'BitBucket',
                                                                 'Blog', 'Portfolio', 'Other', 'Coursera', })

class Location(ndb.Model):
    city            = ndb.StringProperty()
    country         = ndb.StringProperty()


class Tool(ndb.Model):
    category        = ndb.StringProperty(choices=TOOL_CATEGORIES)
    skill           = ndb.StringProperty()
    level           = ndb.IntegerProperty(choices=LEVEL_OPTIONS, default=1)

class CourseAttempt(ndb.Model):
    course          = ndb.KeyProperty(Course)
    student         = ndb.KeyProperty('User')
    completed       = ndb.BooleanProperty(default=False)
    start_date      = ndb.DateTimeProperty()
    endDate         = ndb.DateTimeProperty()