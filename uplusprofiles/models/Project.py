#from google.appengine.ext.ndb import Key
from google.appengine.ext import  ndb
import logging

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

    @classmethod
    def update_project(cls, project_id, **kwargs):
        p = Project.get_by_id(int(project_id))
        p.title = kwargs['title']
        p.screenshot = kwargs['screenshot']
        p.url = kwargs['url']
        p.description = kwargs['description']
        p.put()

    @classmethod
    def remove_project(cls, project_id):
        p = Project.get_by_id(int(project_id))
        p.key.delete()