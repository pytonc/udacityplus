from google.appengine.ext.ndb import Key
from google.appengine.ext import  ndb


class Source(ndb.Model):
    name        = ndb.StringProperty()
    url         = ndb.StringProperty()

class Course(ndb.Model):
    number      = ndb.IntegerProperty()
    dept        = ndb.StringProperty()
    cid         = ndb.ComputedProperty(lambda self: self.dept + str(self.number))
    name        = ndb.StringProperty(required=True)
    level       = ndb.StringProperty(choices=('Beginning', 'Intermediate', 'Advanced', 'Other'))
    short_desc  = ndb.StringProperty()
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

        return Course.get_or_insert(kn, **kwargs)