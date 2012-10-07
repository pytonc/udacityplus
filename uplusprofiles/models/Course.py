from google.appengine.ext import  ndb


class Source(ndb.Model):
    name        = ndb.StringProperty()
    url         = ndb.StringProperty()

class Course(ndb.Model):
    source      = ndb.StructuredProperty(Source)
    number      = ndb.IntegerProperty()
    dept        = ndb.StringProperty()
    cid         = ndb.ComputedProperty(lambda self: self.dept + str(self.number))
    name        = ndb.StringProperty(required=True)
    level       = ndb.StringProperty(choices=('Beginning', 'Intermediate', 'Advanced', 'Other'))
    description = ndb.TextProperty()

class CourseIndex(ndb.Model):
    student     = ndb.KeyProperty(kind='User', repeated=True)