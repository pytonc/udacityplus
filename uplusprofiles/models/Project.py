#from google.appengine.ext.ndb import Key
from google.appengine.ext import  ndb


class Project(ndb.Model):
    title = ndb.StringProperty()
    screenshot = ndb.StringProperty()
    url = ndb.StringProperty()
    description = ndb.TextProperty()

    @classmethod
    def add_project(cls, **kwargs):
        p  = Project(**kwargs)
        p_key = p.put()
        return p_key.id()